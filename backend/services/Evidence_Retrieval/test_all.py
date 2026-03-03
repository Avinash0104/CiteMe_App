"""
Comprehensive unit tests for retrieval.py, scoring.py, main.py, and cli.py
Run with: python test_all.py
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import services.Evidence_Retrieval.retrieval as retrieval
import services.Evidence_Retrieval.scoring as scoring
from main import app
from fastapi.testclient import TestClient


class TestRetrieval(unittest.TestCase):
    """Tests for retrieval.py"""

    @patch('retrieval.client')
    def test_retrieve_references_success(self, mock_client):
        """Test successful retrieval of references"""
        # Mock Tavily API response
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Test Source 1",
                    "url": "https://example.com/1",
                    "content": "This is test content about the claim."
                },
                {
                    "title": "Test Source 2",
                    "url": "https://example.com/2",
                    "content": "More evidence supporting the statement."
                }
            ]
        }

        claims = ["Test claim"]
        result = retrieval.retrieve_references_sync(claims)

        self.assertIn("Test claim", result)
        self.assertEqual(len(result["Test claim"]), 2)
        self.assertEqual(result["Test claim"][0]["title"], "Test Source 1")
        self.assertEqual(result["Test claim"][0]["url"], "https://example.com/1")
        mock_client.search.assert_called_once()

    @patch('retrieval.client')
    def test_retrieve_references_error_handling(self, mock_client):
        """Test error handling when Tavily API fails"""
        mock_client.search.side_effect = Exception("API Error")

        claims = ["Test claim"]
        result = retrieval.retrieve_references_sync(claims)

        self.assertIn("Test claim", result)
        self.assertEqual(len(result["Test claim"]), 1)
        self.assertEqual(result["Test claim"][0]["title"], "tavily_error")
        self.assertIn("API Error", result["Test claim"][0]["snippet"])

    @patch('retrieval.client')
    def test_retrieve_references_truncates_long_content(self, mock_client):
        """Test that long content is properly truncated"""
        long_content = "A" * 1000  # 1000 characters
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Long Content",
                    "url": "https://example.com",
                    "content": long_content
                }
            ]
        }

        claims = ["Test claim"]
        result = retrieval.retrieve_references_sync(claims)

        snippet = result["Test claim"][0]["snippet"]
        self.assertLessEqual(len(snippet), 600)

    @patch('retrieval.client')
    def test_retrieve_references_multiple_claims(self, mock_client):
        """Test retrieval for multiple claims"""
        mock_client.search.return_value = {
            "results": [
                {"title": "Source", "url": "https://example.com", "content": "Test"}
            ]
        }

        claims = ["Claim 1", "Claim 2", "Claim 3"]
        result = retrieval.retrieve_references_sync(claims)

        self.assertEqual(len(result), 3)
        self.assertIn("Claim 1", result)
        self.assertIn("Claim 2", result)
        self.assertIn("Claim 3", result)
        self.assertEqual(mock_client.search.call_count, 3)


class TestScoring(unittest.TestCase):
    """Tests for scoring.py"""

    @patch('scoring.groq_analyze')
    def test_check_claim_with_evidence(self, mock_groq):
        """Test claim checking with valid evidence"""
        mock_groq.return_value = """VERDICT: True
TRUTH_SCORE: 0.85
REASONING: Strong evidence supports this claim."""

        references = [
            {
                "title": "Source 1",
                "url": "https://example.com",
                "snippet": "Supporting evidence for the claim."
            }
        ]

        result = scoring.check_claim("Test claim", references)

        self.assertEqual(result["verdict"], "True")
        self.assertEqual(result["truth_score"], 0.85)
        self.assertIn("Strong evidence", result["reasoning"])

    def test_check_claim_no_evidence(self):
        """Test claim checking with no evidence"""
        result = scoring.check_claim("Test claim", [])

        self.assertEqual(result["verdict"], "No Evidence")
        self.assertEqual(result["truth_score"], 0.00)
        self.assertIn("No evidence", result["reasoning"])

    @patch('scoring.groq_analyze')
    def test_check_claim_false_verdict(self, mock_groq):
        """Test claim that is determined to be false"""
        mock_groq.return_value = """VERDICT: False
                                    TRUTH_SCORE: 0.15
                                    REASONING: Evidence contradicts this claim."""

        references = [
            {"title": "Source", "url": "https://example.com", "snippet": "Contradicting evidence."}
        ]

        result = scoring.check_claim("False claim", references)

        self.assertEqual(result["verdict"], "False")
        self.assertEqual(result["truth_score"], 0.15)

    @patch('scoring.groq_analyze')
    def test_check_claim_uncertain_verdict(self, mock_groq):
        """Test claim with uncertain verdict"""
        mock_groq.return_value = """VERDICT: Uncertain
                                    TRUTH_SCORE: 0.50
                                    REASONING: Evidence is mixed and inconclusive."""

        references = [
            {"title": "Source", "url": "https://example.com", "snippet": "Mixed evidence."}
        ]

        result = scoring.check_claim("Uncertain claim", references)

        self.assertEqual(result["verdict"], "Uncertain")
        self.assertEqual(result["truth_score"], 0.50)

    @patch('scoring.groq_analyze')
    def test_check_claim_bounds_truth_score(self, mock_groq):
        """Test that truth scores are bounded between 0.0 and 1.0"""
        # Test upper bound
        mock_groq.return_value = """VERDICT: True
                                    TRUTH_SCORE: 1.5
                                    REASONING: Over the limit."""

        references = [{"title": "S", "url": "u", "snippet": "test"}]
        result = scoring.check_claim("Claim", references)
        self.assertLessEqual(result["truth_score"], 1.0)

        # Test lower bound
        mock_groq.return_value = """VERDICT: False
                                    TRUTH_SCORE: -0.5
                                    REASONING: Under the limit."""
        result = scoring.check_claim("Claim", references)
        self.assertGreaterEqual(result["truth_score"], 0.0)

    @patch('scoring.groq_analyze')
    def test_check_claim_llm_error_handling(self, mock_groq):
        """Test error handling when LLM call fails"""
        mock_groq.side_effect = Exception("LLM API Error")

        references = [{"title": "S", "url": "u", "snippet": "test"}]
        result = scoring.check_claim("Claim", references)

        self.assertEqual(result["verdict"], "Error")
        self.assertEqual(result["truth_score"], 0.00)
        self.assertIn("error occurred", result["reasoning"])

    @patch('scoring.groq_analyze')
    def test_check_claim_limits_evidence_count(self, mock_groq):
        """Test that only first 5 pieces of evidence are used"""
        mock_groq.return_value = """VERDICT: True
                                    TRUTH_SCORE: 0.80
                                    REASONING: Test."""

        # Provide 10 references
        references = [
            {"title": f"Source {i}", "url": f"https://example.com/{i}", "snippet": f"Snippet content {i}"}
            for i in range(10)
        ]

        result = scoring.check_claim("Claim", references)

        # Check that prompt only includes 5 pieces of evidence (Evidence 1-5)
        call_args = mock_groq.call_args[0][0]
        self.assertIn("Evidence 1 (Source 0):", call_args)
        self.assertIn("Evidence 5 (Source 4):", call_args)
        self.assertNotIn("Source 5", call_args)
        self.assertNotIn("Source 6", call_args)


class TestMain(unittest.TestCase):
    """Tests for main.py FastAPI endpoints"""

    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test root endpoint returns status"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "CiteMe is running!")

    @patch('scoring.check_claim')
    @patch('retrieval.retrieve_references')
    async def test_retrieve_references_endpoint(self, mock_retrieve, mock_score):
        """Test /retrieve-references endpoint"""
        # Mock retrieval response
        mock_retrieve.return_value = {
            "Test claim": [
                {"title": "Source", "url": "https://example.com", "snippet": "Evidence"}
            ]
        }

        # Mock scoring response
        mock_score.return_value = {
            "verdict": "True",
            "truth_score": 0.85,
            "reasoning": "Strong evidence supports this."
        }

        response = self.client.post(
            "/retrieve-references",
            json={"claims": ["Test claim"]}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("retrieved_references", data)
        self.assertEqual(len(data["retrieved_references"]), 1)
        
        result = data["retrieved_references"][0]
        self.assertEqual(result["claim"], "Test claim")
        self.assertEqual(result["verdict"], "True")
        self.assertEqual(result["truth_score"], 0.85)

    @patch('scoring.check_claim')
    @patch('retrieval.retrieve_references')
    async def test_retrieve_references_multiple_claims(self, mock_retrieve, mock_score):
        """Test endpoint with multiple claims"""
        mock_retrieve.return_value = {
            "Claim 1": [{"title": "S1", "url": "u1", "snippet": "e1"}],
            "Claim 2": [{"title": "S2", "url": "u2", "snippet": "e2"}]
        }

        mock_score.side_effect = [
            {"verdict": "True", "truth_score": 0.90, "reasoning": "R1"},
            {"verdict": "False", "truth_score": 0.20, "reasoning": "R2"}
        ]

        response = self.client.post(
            "/retrieve-references",
            json={"claims": ["Claim 1", "Claim 2"]}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["retrieved_references"]), 2)


class TestCLI(unittest.TestCase):
    """Tests for cli.py"""

    @patch('scoring.check_claim')
    @patch('retrieval.retrieve_references_sync')
    @patch('sys.stdout')
    def test_run_once_displays_results(self, mock_stdout, mock_retrieve, mock_score):
        """Test that run_once displays claim results correctly"""
        from backend.services.Evidence_Retrieval.cli import run_once

        mock_retrieve.return_value = {
            "Test claim": [
                {
                    "title": "Test Source",
                    "url": "https://example.com",
                    "snippet": "This is evidence."
                }
            ]
        }

        mock_score.return_value = {
            "verdict": "True",
            "truth_score": 0.85,
            "reasoning": "Strong evidence supports this claim."
        }

        # This will print to stdout
        run_once("Test claim")

        # Verify mocks were called
        mock_retrieve.assert_called_once_with(["Test claim"])
        mock_score.assert_called_once()

    @patch('scoring.check_claim')
    @patch('retrieval.retrieve_references_sync')
    def test_run_once_handles_no_references(self, mock_retrieve, mock_score):
        """Test run_once handles case with no references"""
        from backend.services.Evidence_Retrieval.cli import run_once

        mock_retrieve.return_value = {"Test claim": []}
        mock_score.return_value = {
            "verdict": "No Evidence",
            "truth_score": 0.00,
            "reasoning": "No evidence found."
        }

        # Should not raise exception
        run_once("Test claim")


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""

    @patch('retrieval.client')
    @patch('scoring.groq_analyze')
    def test_full_pipeline(self, mock_groq, mock_tavily):
        """Test complete pipeline from retrieval to scoring"""
        # Mock Tavily
        mock_tavily.search.return_value = {
            "results": [
                {
                    "title": "NASA",
                    "url": "https://nasa.gov",
                    "content": "The Earth is round and orbits the Sun."
                }
            ]
        }

        # Mock LLM
        mock_groq.return_value = """VERDICT: True
TRUTH_SCORE: 0.95
REASONING: Scientific consensus supports this claim."""

        # Run full pipeline
        claim = "The Earth is round"
        refs = retrieval.retrieve_references_sync([claim])
        score = scoring.check_claim(claim, refs[claim])

        self.assertEqual(score["verdict"], "True")
        self.assertGreater(score["truth_score"], 0.9)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRetrieval))
    suite.addTests(loader.loadTestsFromTestCase(TestScoring))
    suite.addTests(loader.loadTestsFromTestCase(TestMain))
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
