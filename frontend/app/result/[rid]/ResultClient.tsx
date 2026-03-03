"use client";

import * as React from "react";
import { useEffect, useState } from "react";
import { GradedText } from "@/components/ui/graded-text";
import {
  getScoreTextColor,
  getScoreBgColor,
  getScoreGrade,
  calculateScoreDistribution,
  GRADE_THRESHOLDS,
} from "@/lib/grading-system";

interface Reference {
  title: string;
  url: string;
  snippet: string;
}

interface RetrievedReference {
  claim: string;
  verdict: string;
  is_claim: boolean;
  truth_score: number;
  reasoning: string;
  references: Reference[];
}

interface ApiResponse {
  retrieved_references: RetrievedReference[];
  overall_score?: number;
}

interface AssertionDetail {
  id: string;
  text: string;
  confidenceScore: number;
  sources: string[];
  explanation: string;
  evidence: string;
}

interface SentenceSegment {
  text: string;
  isAssertion?: boolean;
  confidenceScore?: number;
  assertionId?: string;
}

interface ResultData {
  totalScore: number;
  segments: SentenceSegment[];
  assertionDetails: AssertionDetail[];
}

interface ResultClientProps {
  rid: string;
}

/**
 * Convert API response to ResultData format
 * - Filters based on is_claim field
 * - Converts truth_score to confidenceScore (× 100)
 * - Uses overall_score from API or calculates weighted average
 * - Matches claims in original text to create segments
 */
function convertApiResponseToResultData(
  apiResponse: ApiResponse,
  originalText: string
): ResultData {
  // Filter based on is_claim field
  const validClaims = apiResponse.retrieved_references.filter(
    (ref) => ref.is_claim === true
  );

  // Use overall_score from API if available, otherwise calculate weighted average
  let totalScore: number;
  if (apiResponse.overall_score !== undefined) {
    // API provides overall_score (should already be 0-100)
    totalScore = apiResponse.overall_score;
  } else {
    // Fallback: calculate weighted average of truth_scores × 100
    totalScore =
      validClaims.length > 0
        ? (validClaims.reduce((sum, ref) => sum + ref.truth_score, 0) /
            validClaims.length) *
          100
        : 0;
  }

  // Create assertion details from valid claims
  const assertionDetails: AssertionDetail[] = validClaims.map((ref, index) => ({
    id: `assertion-${index}`,
    text: ref.claim,
    confidenceScore: ref.truth_score * 100,
    sources: ref.references.map((r) => `${r.title} - ${r.url}`),
    explanation: ref.reasoning,
    evidence:
      ref.references.length > 0
        ? ref.references[0].snippet
        : "No evidence available",
  }));

  // Create segments by matching claims in original text
  const segments: SentenceSegment[] = [];
  let currentIndex = 0;

  validClaims.forEach((ref, idx) => {
    const claimIndex = originalText.indexOf(ref.claim, currentIndex);

    if (claimIndex !== -1) {
      // Add text before claim
      if (claimIndex > currentIndex) {
        segments.push({
          text: originalText.substring(currentIndex, claimIndex),
        });
      }

      // Add claim as assertion
      segments.push({
        text: ref.claim,
        isAssertion: true,
        confidenceScore: ref.truth_score * 100,
        assertionId: `assertion-${idx}`,
      });

      currentIndex = claimIndex + ref.claim.length;
    }
  });

  // Add remaining text
  if (currentIndex < originalText.length) {
    segments.push({
      text: originalText.substring(currentIndex),
    });
  }

  return {
    totalScore: Math.round(totalScore * 10) / 10,
    segments,
    assertionDetails,
  };
}

export default function ResultClient({ rid }: ResultClientProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ResultData | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);

        // Check if result is already cached
        const cachedResult = sessionStorage.getItem(`result-${rid}`);
        if (cachedResult) {
          try {
            const resultData = JSON.parse(cachedResult);
            setData(resultData);
            setLoading(false);
            return;
          } catch (parseError) {
            console.warn("Failed to parse cached result, fetching new data");
          }
        }

        // Read text from sessionStorage
        const text = sessionStorage.getItem(`text-${rid}`);
        if (!text) {
          throw new Error("No text found for this analysis");
        }

        // Get API base URL from environment variable (default: http://localhost:8000)
        const apiBaseUrl =
          process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

        // POST request to /retrieve-references
        const response = await fetch(`${apiBaseUrl}/retrieve-references`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ text }),
        });

        if (!response.ok) {
          throw new Error(`API request failed: ${response.statusText}`);
        }

        const apiResponse: ApiResponse = await response.json();

        // Convert API response to ResultData format
        const resultData = convertApiResponseToResultData(apiResponse, text);
        
        // Cache the result
        sessionStorage.setItem(`result-${rid}`, JSON.stringify(resultData));
        
        setData(resultData);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [rid]);

  // Loading state
  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-8 shadow-2xl max-w-md w-full mx-4">
          <div className="flex flex-col items-center gap-4">
            <div className="relative w-20 h-20">
              <div className="absolute inset-0 border-4 border-green-200 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-green-500 rounded-full border-t-transparent animate-spin"></div>
            </div>
            <h3 className="text-xl font-semibold text-slate-800 dark:text-slate-100">
              Analyzing Your Text...
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 text-center">
              Our AI is verifying claims and checking credibility. This may take a moment.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !data) {
    return (
      <div className="relative z-10 container mx-auto px-4 py-12 max-w-3xl">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl p-8 text-center">
          <div className="text-red-600 dark:text-red-400 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-red-800 dark:text-red-200 mb-2">
            Error Loading Results
          </h2>
          <p className="text-red-600 dark:text-red-300 mb-6">
            {error || "Unable to load analysis results"}
          </p>
          <a
            href="/"
            className="inline-block px-6 py-2 bg-green-500 text-white rounded-full hover:bg-green-600 transition"
          >
            Return to Home
          </a>
        </div>
      </div>
    );
  }

  // Main result display
  const assertionScores = data.assertionDetails.map(
    (d) => d.confidenceScore
  );
  const scoreDistribution =
    calculateScoreDistribution(assertionScores);

  
  // Function to scroll to a specific assertion
  const scrollToAssertion = (assertionId: string) => {
    const element = document.getElementById(assertionId);
    if (element) {
      element.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      element.classList.add("highlight-flash");
      setTimeout(
        () => element.classList.remove("highlight-flash"),
        2000
      );
    }
  };

  return (
    <div className="relative z-10 container mx-auto px-4 py-12 max-w-5xl">
      {/* Header Section */}
      <div className="text-center mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-linear-to-r from-green-600 to-green-600">
          Credibility Analysis Report
        </h1>
        <p className="text-muted-foreground text-lg">
          Result ID:{" "}
          <span className="font-mono text-foreground">
            {rid}
          </span>
        </p>
      </div>

      {/* Overall Score Card */}
      <div className="mb-12 animate-in fade-in slide-in-from-bottom-5 duration-700 delay-100">
        <div className="relative group">
          <div className="absolute -inset-0.5 bg-linear-to-r from-green-500 to-emerald-600 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-500"></div>
          <div className="relative bg-white dark:bg-slate-900 rounded-2xl p-8 md:p-12 shadow-xl border border-slate-200 dark:border-slate-800">
            <div className="flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="flex-1 text-center md:text-left">
                <h2 className="text-2xl font-semibold mb-2 text-slate-700 dark:text-slate-200">
                  Overall Credibility Score
                </h2>
                <p className="text-sm text-muted-foreground">
                  Weighted average of all assertion confidence scores
                </p>
              </div>
              
              <div className="flex items-center gap-6">
                <div className="relative">
                  {/* Circular Progress Ring */}
                  <svg className="w-32 h-32 md:w-40 md:h-40 transform -rotate-90" viewBox="0 0 160 160">
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="currentColor"
                      strokeWidth="12"
                      fill="none"
                      className="text-slate-200 dark:text-slate-800"
                    />
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="currentColor"
                      strokeWidth="12"
                      fill="none"
                      strokeLinecap="round"
                      className={getScoreTextColor(data.totalScore)}
                      strokeDasharray={`${2 * Math.PI * 70}`}
                      strokeDashoffset={`${2 * Math.PI * 70 * (1 - data.totalScore / 100)}`}
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-5xl font-bold ${getScoreTextColor(data.totalScore)}`}>
                      {data.totalScore.toFixed(1)}
                    </span>
                    <span className="text-sm text-muted-foreground mt-1">Grade {getScoreGrade(data.totalScore)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Score Distribution Section */}
            <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-800">
              <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-4">
                Assertion Score Distribution
              </h3>
              <div className="space-y-3">
                {scoreDistribution.map((dist) => (
                  <div key={dist.letter} className="flex items-center gap-4">
                    <div className="flex items-center gap-2 min-w-[120px]">
                      <div className={`w-3 h-3 rounded-full ${dist.bgColor}`}></div>
                      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                        Grade {dist.letter}
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="relative h-5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${dist.bgColor} transition-all duration-500 ease-out flex items-center justify-end pr-2 w-[${dist.percentage}%]`}
                          style={{width:dist.percentage+"%"}}
                        > 
                            <span className="text-xs font-semibold text-white">
                            {dist.percentage.toFixed(1)}%
                            </span>
                        </div>
                      </div>
                    </div>
                    <div className="min-w-20 text-right">
                      <span className="text-sm text-slate-600 dark:text-slate-400">
                        {dist.count} {dist.count === 1 ? 'assertion' : 'assertions'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <p className="mt-4 text-xs text-muted-foreground">
                Distribution based on {assertionScores.length} total assertions in the text.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Text Analysis Card */}
      <div className="mb-12 animate-in fade-in slide-in-from-bottom-6 duration-700 delay-200">
        <div className="relative group">
          <div className="absolute -inset-0.5 bg-linear-to-r from-green-500 to-emerald-600 rounded-2xl blur opacity-20 group-hover:opacity-30 transition duration-500"></div>
          <div className="relative bg-white dark:bg-slate-900 rounded-2xl p-8 md:p-12 shadow-xl border border-slate-200 dark:border-slate-800">
            <h2 className="text-2xl font-semibold mb-6 text-slate-700 dark:text-slate-200 flex items-center gap-3">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-500/10 text-green-600 dark:text-green-400">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
              </span>
              Text Analysis
            </h2>
            
            <div className="prose prose-lg dark:prose-invert max-w-none">
              <div className="leading-relaxed text-lg text-slate-700 dark:text-slate-300 space-y-1">
                {data.segments.map((segment, index) => {
                  if (segment.isAssertion && segment.confidenceScore !== undefined && segment.assertionId) {
                    const detail = data.assertionDetails.find(d => d.id === segment.assertionId)
                    return (
                      <span
                        key={index}
                        className="group/tooltip relative"
                      >
                        <span
                          onClick={() => scrollToAssertion(segment.assertionId!)}
                          className="text-left"
                        >
                          <GradedText
                            grade={segment.confidenceScore}
                            color="auto"
                            showUnderline={true}
                            className="transition-all duration-200 hover:scale-105 cursor-pointer"
                          >
                            {segment.text}
                          </GradedText>
                        </span>
                        {/* Tooltip */}
                        {detail && (
                          <div className="invisible group-hover/tooltip:visible absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-80 p-4 bg-slate-900 dark:bg-slate-800 text-white text-sm rounded-lg shadow-xl border border-slate-700">
                            <div className="font-semibold mb-2 flex items-center gap-2">
                              <span className={`inline-block w-2 h-2 rounded-full ${getScoreBgColor(detail.confidenceScore)}`}></span>
                              Confidence: {detail.confidenceScore}%
                            </div>
                            <div className="text-slate-300 mb-2">
                              <strong>Evidence:</strong> {detail.evidence}
                            </div>
                            <div className="text-slate-400 text-xs italic">
                              Click to see full analysis
                            </div>
                            {/* Arrow pointer */}
                            <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px">
                              <div className="border-8 border-transparent border-t-slate-900 dark:border-t-slate-800"></div>
                            </div>
                          </div>
                        )}
                      </span>
                    )
                  }
                  return <span key={index}>{segment.text}</span>
                })}
              </div>
            </div>

            {/* Legend - ordered from high to low */}
            <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800">
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">
                Confidence Score Legend:
              </h3>
              <div className="flex flex-wrap gap-4">
                {GRADE_THRESHOLDS.map((threshold) => (
                  <div key={threshold.letter} className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${threshold.bgColor}`}></div>
                    <span className="text-sm text-muted-foreground">
                      {threshold.label} ({threshold.letter})
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Analysis Section */}
      <div className="space-y-6 animate-in fade-in slide-in-from-bottom-7 duration-700 delay-300">
        <h2 className="text-2xl font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-500/10 text-green-600 dark:text-green-400">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
            </svg>
          </span>
          Detailed Assertion Analysis
        </h2>

{data.assertionDetails.map((detail, index) => (
          <div
            key={detail.id}
            id={detail.id}
            className="relative group scroll-mt-24"
          >
            <div className="absolute -inset-0.5 bg-linear-to-r from-green-500 to-emerald-600 rounded-xl blur opacity-0 group-hover:opacity-20 transition duration-500"></div>
            <div className="relative bg-white dark:bg-slate-900 rounded-xl p-6 md:p-8 shadow-lg border border-slate-200 dark:border-slate-800 transition-all duration-300">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                      ASSERTION #{index + 1}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-slate-800 dark:text-slate-100">
                    &ldquo;{detail.text}&rdquo;
                  </h3>
                </div>
                <div className="flex flex-col items-center gap-1 min-w-20">
                  <div className={`text-4xl font-bold ${getScoreTextColor(detail.confidenceScore)}`}>
                    {detail.confidenceScore}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {getScoreGrade(detail.confidenceScore)} Grade
                  </div>
                </div>
              </div>

              {/* Score Explanation */}
              <div className="mb-4 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
                  </svg>
                  Explanation
                </h4>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {detail.explanation}
                </p>
              </div>

              {/* Evidence */}
              <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <h4 className="text-sm font-semibold text-green-800 dark:text-green-300 mb-2 flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Evidence
                </h4>
                <p className="text-sm text-green-900 dark:text-green-200">
                  {detail.evidence}
                </p>
              </div>

              {/* Citation Sources */}
              <div>
                <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                  </svg>
                  Sources
                </h4>
                <ul className="space-y-2">
                  {detail.sources.map((source, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                      <span className="text-green-600 dark:text-green-400 mt-0.5">•</span>
                      <span>{source}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}

      </div>

      {/* Bottom Information */}
      <div className="mt-12 text-center text-sm text-muted-foreground animate-in fade-in duration-700 delay-400">
        <p>
          Powered by AI-driven credibility analysis. Results are for informational purposes only and should be independently verified.
        </p>
      </div>

      {/* Flash animation */}
      <style>{`
        @keyframes highlight-flash {
          0%, 100% { background-color: transparent; }
          50% { background-color: rgba(34, 197, 94, 0.25); }
        }
        .highlight-flash {
          animation: highlight-flash 1.5s ease-in-out;
        }
      `}</style>
    </div>
  );
}
