---
emoji: 🐳
sdk: docker
app_port: 7860
---
# CiteMe Project

An automated citation and fact-checking system that extracts claims from text, retrieves relevant sources, and scores their credibility using advanced NLP techniques.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Team Members](#team-members)
- [License](#license)

## 🎯 Overview

CiteMe is a comprehensive system designed to help users verify claims and find credible sources automatically. The system uses natural language processing (NLP) to extract claims from text, searches for relevant sources using multiple search engines, and provides credibility scores based on source quality and relevance.

## ✨ Features

- **Claim Extraction**: Automatically identifies factual claims, opinions, and statements from text using ClaimBERT model
- **Entity Recognition**: Extracts named entities (people, places, organizations) using spaCy
- **Source Retrieval**: Searches for relevant sources using Google and Bing search APIs
- **Credibility Scoring**: Calculates credibility scores based on source quality, relevance, and domain authority
- **Modern UI**: Beautiful and intuitive React-based frontend with Tailwind CSS
- **RESTful API**: FastAPI-based backend with comprehensive endpoints

## 🛠 Technology Stack

### Backend

- **FastAPI**: Modern, fast web framework for building APIs
- **spaCy**: Advanced NLP library for entity extraction
- **Transformers**: Hugging Face transformers for ClaimBERT model
- **PyTorch**: Deep learning framework
- **Requests**: HTTP library for API calls

### Frontend

- **React**: Modern JavaScript library for building user interfaces
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API requests

### DevOps

- **GitLab CI/CD**: Continuous integration and deployment
- **Docker**: Containerization (optional)

## 📁 Project Structure

```
CiteMe-Project/
├── backend/                 # Backend + NLP modules
│   ├── app/
│   │   ├── main.py         # FastAPI main application
│   │   ├── routes/         # API endpoints
│   │   │   ├── extraction.py
│   │   │   ├── retrieval.py
│   │   │   └── scoring.py
│   │   ├── services/       # Core business logic
│   │   │   ├── nlp_pipeline.py
│   │   │   ├── retrieval_api.py
│   │   │   └── scoring_model.py
│   │   ├── tests/          # Unit tests
│   │   └── utils/          # Utility functions
│   └── notebooks/          # Jupyter notebooks for experiments
│
├── frontend/               # Frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── assets/        # Static assets
│   │   └── styles/        # Tailwind styles
│   └── public/              # Public files
│
├── data/                  # Data files
│   ├── sample_texts/      # Test texts
│   ├── example_outputs/   # Example JSON outputs
│   └── datasets/          # Training datasets
│
└── docs/                  # Documentation
    ├── architecture_diagram.png
    ├── meeting_notes/
    ├── eoi/
    └── ppt/
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn
- Google Custom Search API key (optional)
- Bing Search API key (optional)

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://projects.cs.nott.ac.uk/comp2002/2025-2026/team38_project.git
   cd team38_project
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   The spaCy transformer model (`en_core_web_trf`) will be automatically downloaded during the pip installation process.

4. **Set up environment variables**

   Create a `.env` file in the `backend` directory with the following variables:

   ```bash
   # Tavily API for evidence retrieval
   TAVILY_API_KEY=your_tavily_api_key
   
   # Optional: For LLM-based scoring (choose one)
   GROQ_API_KEY=your_groq_api_key  # For Groq API
   # OR use local Ollama (no API key needed, see backend README for setup)
   ```

5. **Run the backend**

   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 7860
   ```

   The API will be available at `http://localhost:7860`

### Frontend Setup

1. **Install dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server**

   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## 💻 Usage

### API Endpoints

#### Health Check

```bash
GET /
```

Example response:

```json
{
  "status": "CiteMe is running!",
  "version": "1.0.0"
}
```

#### Retrieve References and Verify Claims

```bash
POST /retrieve-references
Content-Type: application/json

{
  "text": "The Earth revolves around the Sun. Python is a programming language."
}
```

Response format:

```json
{
  "retrieved_references": [
    {
      "claim": "The Earth revolves around the Sun.",
      "is_claim": true,
      "verdict": "True",
      "truth_score": 0.95,
      "reasoning": "Well-established astronomical fact...",
      "references": [
        {
          "title": "Earth's orbit",
          "url": "https://...",
          "content": "..."
        }
      ]
    }
  ]
}
```

**Parameters:**

- `text` (string, required): Input text containing claims to verify. The system will automatically extract individual sentences and identify which ones are factual claims.

**Response fields:**

- `claim`: The extracted claim text
- `is_claim`: Whether the sentence was identified as a factual claim
- `verdict`: True, False, or Uncertain
- `truth_score`: Credibility score (0.00-1.00)
  - 0.90-1.00: Definitely True
  - 0.70-0.89: Mostly True
  - 0.50: Uncertain
  - 0.10-0.30: Mostly False
  - 0.00-0.09: Definitely False
- `reasoning`: Explanation for the verdict based on retrieved evidence
- `references`: List of web sources found supporting/contradicting the claim

### Frontend Usage

1. Open the application in your browser at `http://localhost:3000`
2. Paste or type the text you want to verify
3. Click "Submit" or the appropriate button to send the text for analysis
4. The system will:
   - Extract individual claims from your text
   - Retrieve relevant sources for each claim
   - Calculate credibility scores based on evidence
5. View the analysis results including verdicts, truth scores, and supporting/contradicting sources

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: <http://localhost:7860/docs>
- **ReDoc**: <http://localhost:7860/redoc>

## 🔧 Development

### Running Tests

**Backend Tests**

```bash
cd backend
pytest app/tests/
```

**Frontend Tests**

```bash
cd frontend
npm test
```

### Code Style

- Backend: Follow PEP 8 style guide
- Frontend: Use ESLint and Prettier

## 👥 Team Members

- **Technical Core Group**: Backend + NLP modules development
- **UI/UX Group**: Frontend development and user experience design

## 📝 License

This project is part of COMP2002 course at the University of Nottingham.

## 🤝 Contributing

This is a course project. For contributions, please contact the project maintainers.

## 📧 Contact

For questions or issues, please contact the development team.

---

**Note**: This project is under active development. Some features may be incomplete or subject to change.
