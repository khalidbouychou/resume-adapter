# Resume Adapter

A full-stack application that generates tailored LaTeX resumes by analyzing your CV and matching it to job descriptions using RAG (Retrieval-Augmented Generation) and OpenAI's GPT-4.

## Architecture Overview

### System Design

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ◄─────► │   Backend    │ ◄─────► │  OpenAI API │
│ React+Vite  │  HTTP   │   FastAPI    │  API    │    GPT-4    │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │   RAG    │
                        │ Pipeline │
                        └──────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              ┌──────────┐        ┌─────────┐
              │  FAISS   │        │ OpenAI  │
              │ Vector   │        │Embedding│
              │  Store   │        │   API   │
              └──────────┘        └─────────┘
```

### Data Flow

1. **User Input**: User uploads CV (PDF) and provides LinkedIn job URL
2. **CV Processing**: Backend extracts text from PDF using pdfplumber
3. **Job Scraping**: Backend fetches job description from LinkedIn URL
4. **RAG Pipeline**:
   - Split CV text into chunks (500 chars, 50 overlap)
   - Generate embeddings using OpenAI Embeddings
   - Store vectors in FAISS vector store
   - Retrieve top-K relevant chunks based on job description
5. **LLM Generation**: 
   - Send full CV, relevant sections, and job description to GPT-4
   - Prompt engineering to generate tailored LaTeX resume
6. **Output**: Return LaTeX code to frontend for display

## Project Structure

```
resume-adapter/
├── backend/
│   ├── main.py              # FastAPI application with RAG implementation
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Backend container config
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Button.jsx   # UI button component
│   │   │   ├── Input.jsx    # UI input component
│   │   │   └── Card.jsx     # UI card component
│   │   ├── lib/
│   │   │   └── utils.js     # Utility functions
│   │   ├── App.jsx          # Main application component
│   │   ├── main.jsx         # Entry point
│   │   └── index.css        # Global styles
│   ├── index.html           # HTML template
│   ├── package.json         # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── tailwind.config.js   # Tailwind configuration
│   ├── postcss.config.js    # PostCSS configuration
│   ├── Dockerfile           # Frontend container config
│   └── nginx.conf           # Nginx configuration
├── docker-compose.yml       # Docker orchestration
├── .env.example             # Root environment template
└── README.md                # This file
```

## RAG Implementation Details

### 1. Text Chunking
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Each chunk is ~500 characters
    chunk_overlap=50,    # 50 character overlap between chunks
    length_function=len,
)
```

### 2. Embeddings & Vector Store
```python
embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)
vectorstore = FAISS.from_documents(documents, embeddings)
```

### 3. Similarity Search
```python
docs = vectorstore.similarity_search(job_description, k=5)
```
Retrieves top 5 most relevant CV sections based on cosine similarity.

### 4. Context Assembly
- Full CV text (for comprehensive context)
- Top-K relevant sections (emphasized matching)
- Job description (requirements and keywords)

## OpenAI Prompt Engineering

### Prompt Structure

```python
prompt = f"""You are an expert resume writer and LaTeX specialist.

**FULL CV CONTENT:**
{cv_text}

**MOST RELEVANT SECTIONS (from RAG retrieval):**
{relevant_sections}

**JOB DESCRIPTION:**
{job_description}

**INSTRUCTIONS:**
1. Analyze job description for key requirements
2. Use FULL CV as source material
3. Emphasize experiences matching job requirements
4. Reorganize bullet points for job alignment
5. Keep concise (1-2 pages max)
6. Output ONLY LaTeX code

**OUTPUT REQUIREMENTS:**
- Pure LaTeX code only
- Start with \\documentclass
- End with \\end{{document}}
- Use standard packages
- No markdown, no explanations
"""
```

### Model Configuration
- **Model**: `gpt-4-turbo-preview`
- **Temperature**: 0.7 (balanced creativity/consistency)
- **Max Tokens**: 4000 (sufficient for full resume)

## Tech Stack

### Backend
- **Framework**: FastAPI (modern, async Python web framework)
- **PDF Processing**: pdfplumber (text extraction from PDFs)
- **Web Scraping**: BeautifulSoup4 + requests (LinkedIn job parsing)
- **LLM**: OpenAI GPT-4 Turbo (resume generation)
- **Embeddings**: OpenAI Embeddings (text-embedding-ada-002)
- **Vector Store**: FAISS (efficient similarity search)
- **Orchestration**: LangChain (RAG pipeline management)

### Frontend
- **Framework**: React 18 (declarative UI)
- **Build Tool**: Vite (fast development and builds)
- **Styling**: Tailwind CSS (utility-first CSS)
- **Components**: shadcn/ui patterns (accessible UI primitives)
- **Icons**: Lucide React (clean, consistent icons)
- **Design**: Black/White/Gray minimalist theme

### Infrastructure
- **Containerization**: Docker (isolated environments)
- **Orchestration**: Docker Compose (multi-container setup)
- **Web Server**: Nginx (production frontend serving)

## Setup & Installation

### Prerequisites
- Docker & Docker Compose
- OpenAI API key
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Quick Start (Docker)

1. **Clone the repository**
```bash
git clone <repository-url>
cd resume-adapter
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
uvicorn main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Usage

1. **Upload CV**: Click the upload area and select your CV PDF file
2. **Enter Job URL**: Paste a LinkedIn job posting URL
3. **Generate**: Click "Generate Adapted Resume"
4. **Wait**: The system will process (typically 10-30 seconds)
5. **Copy**: Copy the generated LaTeX code
6. **Compile**: Paste into a LaTeX editor (Overleaf, TeXShop, etc.) and compile

## API Endpoints

### `POST /generate-resume`
Generate an adapted resume from CV and job description.

**Request:**
- `cv_file`: PDF file (multipart/form-data)
- `job_url`: LinkedIn job URL (form field)

**Response:**
```json
{
  "success": true,
  "latex_code": "\\documentclass{article}...",
  "message": "Resume generated successfully"
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "openai_key_set": true
}
```

## Design Decisions

### Why RAG?
- **Context Relevance**: RAG retrieves only relevant CV sections, reducing noise
- **Token Efficiency**: Focuses LLM attention on matching experiences
- **Better Matching**: Semantic search finds related skills even with different wording
- **Scalability**: Handles long CVs efficiently

### Why FAISS?
- **Fast**: Optimized for similarity search on large vector sets
- **Lightweight**: CPU-only version, no GPU required
- **Reliable**: Battle-tested by Facebook AI Research

### Why Minimalist Design?
- **Professional**: Clean aesthetics appropriate for resume tools
- **Accessibility**: High contrast (black/white) improves readability
- **Focus**: No distractions from the core functionality
- **Timeless**: Won't look dated compared to trendy designs

## Limitations & Future Improvements

### Current Limitations
1. **LinkedIn Scraping**: LinkedIn has anti-scraping measures; may not always work
2. **PDF Parsing**: Complex layouts or scanned PDFs may not parse well
3. **LaTeX Compilation**: Users need LaTeX knowledge to compile output
4. **Single Template**: Generates one LaTeX style only

### Potential Improvements
- [ ] Use LinkedIn API for reliable job fetching
- [ ] Support multiple resume templates/styles
- [ ] Add PDF preview of compiled resume
- [ ] OCR support for scanned CVs
- [ ] Support for other job boards (Indeed, Glassdoor)
- [ ] Resume scoring and optimization suggestions
- [ ] Multi-language support
- [ ] Save/load resume versions
- [ ] ATS (Applicant Tracking System) compatibility check

## Troubleshooting

### Backend Issues

**"Could not extract text from PDF"**
- Ensure PDF is text-based, not scanned
- Try a different PDF reader to save your CV

**"Failed to fetch job description"**
- LinkedIn may be blocking requests
- Try a different job URL
- Consider using job description text directly (future feature)

**"OpenAI API error"**
- Check your API key is valid
- Ensure you have sufficient credits
- Check OpenAI service status

### Frontend Issues

**"Network error"**
- Ensure backend is running on port 8000
- Check CORS settings
- Verify Docker containers are up

**Build fails**
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (should be 18+)

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- OpenAI for GPT-4 and embedding APIs
- LangChain for RAG framework
- shadcn/ui for component patterns
- FastAPI for excellent Python web framework
- The open-source community

---

**Note**: This project is for educational and personal use. Be mindful of LinkedIn's Terms of Service when scraping job postings. For production use, consider using official APIs.
