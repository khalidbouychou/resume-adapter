# Project Folder Structure

```
resume-adapter/
│
├── README.md                       # Main documentation
├── QUICKSTART.md                   # Quick start guide
├── ARCHITECTURE.md                 # Technical architecture documentation
├── PROMPT_DOCUMENTATION.md         # OpenAI prompt details
├── .gitignore                      # Git ignore rules
├── .env.example                    # Environment variables template
├── docker-compose.yml              # Docker orchestration
│
├── backend/                        # FastAPI backend service
│   ├── main.py                     # Main application file
│   │   ├── FastAPI app setup
│   │   ├── CORS middleware
│   │   ├── PDF extraction (pdfplumber)
│   │   ├── Web scraping (BeautifulSoup)
│   │   ├── RAG pipeline (LangChain + FAISS)
│   │   ├── OpenAI integration
│   │   └── API endpoints
│   │
│   ├── requirements.txt            # Python dependencies
│   │   ├── fastapi
│   │   ├── uvicorn
│   │   ├── pdfplumber
│   │   ├── openai
│   │   ├── langchain
│   │   ├── faiss-cpu
│   │   └── beautifulsoup4
│   │
│   ├── Dockerfile                  # Backend container config
│   └── .env.example                # Backend environment template
│
├── frontend/                       # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Button.jsx          # Reusable button component
│   │   │   ├── Input.jsx           # Reusable input component
│   │   │   └── Card.jsx            # Reusable card component
│   │   │
│   │   ├── lib/
│   │   │   └── utils.js            # Utility functions (cn helper)
│   │   │
│   │   ├── App.jsx                 # Main application component
│   │   │   ├── File upload handling
│   │   │   ├── Form validation
│   │   │   ├── API communication
│   │   │   ├── Loading states
│   │   │   └── Result display
│   │   │
│   │   ├── main.jsx                # React entry point
│   │   └── index.css               # Global styles (Tailwind)
│   │
│   ├── index.html                  # HTML template
│   ├── package.json                # Node dependencies
│   ├── vite.config.js              # Vite configuration
│   ├── tailwind.config.js          # Tailwind configuration
│   ├── postcss.config.js           # PostCSS configuration
│   ├── Dockerfile                  # Frontend container config
│   └── nginx.conf                  # Nginx configuration
│
└── [Generated at runtime]
    ├── backend/venv/               # Python virtual environment
    ├── frontend/node_modules/      # Node modules
    ├── frontend/dist/              # Built frontend assets
    └── .env                        # Actual environment variables (not in git)
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (React)                           │
│  ┌──────────────┐  ┌───────────┐  ┌──────────────┐            │
│  │   App.jsx    │──│ Button    │  │    Card      │            │
│  │              │  │ Input     │  │              │            │
│  └──────┬───────┘  └───────────┘  └──────────────┘            │
│         │                                                       │
│         │ HTTP POST /generate-resume                           │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │                   main.py                        │          │
│  │  ┌────────────────────────────────────────────┐ │          │
│  │  │  Endpoint: POST /generate-resume           │ │          │
│  │  └───┬────────────────────────────────────────┘ │          │
│  │      │                                           │          │
│  │      ├──► extract_text_from_pdf()              │          │
│  │      │    └─► pdfplumber                       │          │
│  │      │                                           │          │
│  │      ├──► fetch_linkedin_job_description()     │          │
│  │      │    └─► BeautifulSoup + requests         │          │
│  │      │                                           │          │
│  │      ├──► create_rag_retriever()                │          │
│  │      │    ├─► RecursiveCharacterTextSplitter   │          │
│  │      │    ├─► OpenAIEmbeddings                 │          │
│  │      │    └─► FAISS.from_documents()           │          │
│  │      │                                           │          │
│  │      ├──► retrieve_relevant_cv_sections()      │          │
│  │      │    └─► vectorstore.similarity_search()  │          │
│  │      │                                           │          │
│  │      └──► generate_latex_resume()              │          │
│  │           └─► OpenAI GPT-4 API                 │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                            │
│  ┌──────────────┐                  ┌──────────────┐            │
│  │   OpenAI     │                  │   LinkedIn   │            │
│  │   API        │                  │   (Scraping) │            │
│  │              │                  │              │            │
│  │ - Embeddings │                  │ - Job Desc   │            │
│  │ - GPT-4      │                  │              │            │
│  └──────────────┘                  └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Through Files

```
1. User uploads file
   ↓
   frontend/src/App.jsx (handleFileChange)
   ↓
   
2. User clicks generate
   ↓
   frontend/src/App.jsx (handleGenerate)
   ↓
   
3. HTTP POST to backend
   ↓
   backend/main.py (@app.post("/generate-resume"))
   ↓
   
4. Extract PDF text
   ↓
   backend/main.py (extract_text_from_pdf)
   Uses: pdfplumber library
   ↓
   
5. Fetch job description
   ↓
   backend/main.py (fetch_linkedin_job_description)
   Uses: requests + BeautifulSoup
   ↓
   
6. Create RAG pipeline
   ↓
   backend/main.py (create_rag_retriever)
   Uses: LangChain + OpenAI Embeddings + FAISS
   ↓
   
7. Retrieve relevant sections
   ↓
   backend/main.py (retrieve_relevant_cv_sections)
   Uses: FAISS similarity search
   ↓
   
8. Generate LaTeX
   ↓
   backend/main.py (generate_latex_resume)
   Uses: OpenAI GPT-4 API
   ↓
   
9. Return to frontend
   ↓
   frontend/src/App.jsx (setLatexCode)
   ↓
   
10. Display in Card component
   ↓
   frontend/src/components/Card.jsx
```

## File Size Reference

Approximate file sizes:
- `main.py`: ~300 lines, ~12 KB
- `App.jsx`: ~150 lines, ~6 KB
- Component files: ~30-50 lines each, ~2 KB each
- `requirements.txt`: ~15 lines, <1 KB
- `package.json`: ~30 lines, ~1 KB
- Configuration files: ~20 lines each, <1 KB each

Total project size (excluding dependencies):
- Source code: ~50 KB
- Documentation: ~100 KB
- Configuration: ~10 KB
- **Total: ~160 KB**

With dependencies:
- Backend (Python packages): ~500 MB
- Frontend (node_modules): ~200 MB
- **Total with dependencies: ~700 MB**

## Key Files Summary

| File | Purpose | Technologies |
|------|---------|-------------|
| `backend/main.py` | API server & RAG pipeline | FastAPI, LangChain, FAISS |
| `frontend/src/App.jsx` | Main UI component | React, Fetch API |
| `frontend/src/components/*.jsx` | Reusable UI components | React, Tailwind |
| `docker-compose.yml` | Service orchestration | Docker Compose |
| `backend/requirements.txt` | Python dependencies | pip |
| `frontend/package.json` | Node dependencies | npm |
| `*.config.js` | Build configurations | Vite, Tailwind, PostCSS |
| `README.md` | Main documentation | Markdown |
| `ARCHITECTURE.md` | Technical details | Markdown |

## Configuration Files Explained

### Backend Configuration
- `Dockerfile`: Defines Python environment, installs dependencies, runs uvicorn
- `requirements.txt`: Lists Python packages and versions
- `.env`: Contains OPENAI_API_KEY (not in git)

### Frontend Configuration
- `Dockerfile`: Multi-stage build (Node build → Nginx serve)
- `package.json`: Lists npm packages and scripts
- `vite.config.js`: Development server settings
- `tailwind.config.js`: CSS utility configuration
- `postcss.config.js`: CSS processing pipeline
- `nginx.conf`: Production web server settings

### Root Configuration
- `docker-compose.yml`: Connects backend + frontend services
- `.env`: Shared environment variables
- `.gitignore`: Files to exclude from version control
