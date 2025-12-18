# Resume Adapter - Technical Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Breakdown](#component-breakdown)
4. [RAG Pipeline Deep Dive](#rag-pipeline-deep-dive)
5. [Data Flow](#data-flow)
6. [Technology Choices](#technology-choices)
7. [Security Considerations](#security-considerations)
8. [Performance Optimization](#performance-optimization)

## System Overview

Resume Adapter is a full-stack application that uses Retrieval-Augmented Generation (RAG) to create tailored resumes. It combines traditional information retrieval with large language models to intelligently adapt a user's CV to match specific job requirements.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                      (React + Tailwind)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      API Gateway                                │
│                      (FastAPI)                                  │
└─────┬───────────────┬────────────────┬──────────────────────────┘
      │               │                │
      │               │                │
┌─────▼──────┐  ┌────▼────────┐  ┌───▼──────────┐
│   PDF      │  │  Web        │  │   RAG        │
│ Processing │  │  Scraping   │  │   Pipeline   │
└────────────┘  └─────────────┘  └───┬──────────┘
                                     │
                          ┌──────────┴──────────┐
                          │                     │
                    ┌─────▼─────┐      ┌───────▼─────┐
                    │   Vector  │      │   OpenAI    │
                    │   Store   │      │     API     │
                    │  (FAISS)  │      │  (GPT-4)    │
                    └───────────┘      └─────────────┘
```

## Component Breakdown

### 1. Frontend (React + Vite)

**Purpose**: User interface for file upload and result display

**Key Components**:
- `App.jsx`: Main application container
  - File upload handling
  - Form validation
  - API communication
  - Loading states
  - Error handling

- `Button.jsx`: Reusable button component
  - Multiple variants (default, outline)
  - Size options
  - Disabled states
  - Loading indicators

- `Input.jsx`: Form input component
  - Validation styling
  - Focus states
  - Error states

- `Card.jsx`: Container component
  - Header/Title/Description
  - Content area
  - Consistent spacing

**Technologies**:
- React 18: Modern hooks-based approach
- Vite: Fast build tool with HMR
- Tailwind CSS: Utility-first styling
- Lucide React: Icon library

**Design Philosophy**:
- Minimalist black/white/gray palette
- No gradients or animations
- High contrast for accessibility
- Mobile-responsive layout

### 2. Backend (FastAPI)

**Purpose**: API server handling business logic, RAG pipeline, and LLM integration

**Key Modules**:

#### `main.py` - Core Application
```python
# Main endpoints
POST /generate-resume    # Generate adapted resume
GET /health             # Health check
GET /                   # API info
```

#### PDF Processing Module
```python
def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extracts text from PDF using pdfplumber
    - Opens PDF from bytes
    - Iterates through pages
    - Combines text with spacing
    """
```

**Why pdfplumber?**
- Accurate text extraction
- Preserves layout information
- Handles tables and complex structures
- Lightweight and fast

#### Web Scraping Module
```python
def fetch_linkedin_job_description(url: str) -> str:
    """
    Scrapes job description from LinkedIn
    - Uses multiple CSS selectors
    - Handles different page layouts
    - Fallback strategies
    - Error handling
    """
```

**Challenges**:
- LinkedIn's anti-scraping measures
- Dynamic content loading
- Varying page structures

**Solutions**:
- Multiple selector strategies
- User-Agent spoofing
- Graceful degradation

#### RAG Pipeline Module

**Step 1: Text Chunking**
```python
def create_rag_retriever(cv_text: str):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # Optimal for context window
        chunk_overlap=50,    # Prevents information loss
        length_function=len,
    )
```

**Why these parameters?**
- 500 chars: Balance between context and specificity
- 50 char overlap: Ensures sentences aren't split
- Recursive: Tries to split on natural boundaries

**Step 2: Embedding Generation**
```python
embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)
```

**Embedding Model**: text-embedding-ada-002
- 1536 dimensions
- Cost-effective
- Good semantic understanding

**Step 3: Vector Store Creation**
```python
vectorstore = FAISS.from_documents(documents, embeddings)
```

**Why FAISS?**
- Fast similarity search (O(log n))
- Memory efficient
- No external database needed
- Proven at scale (Facebook)

**Step 4: Similarity Search**
```python
def retrieve_relevant_cv_sections(vectorstore, job_description: str, k: int = 5):
    docs = vectorstore.similarity_search(job_description, k=k)
    return "\n\n".join([doc.page_content for doc in docs])
```

**Why k=5?**
- Balances coverage and focus
- ~2500 chars of relevant content
- Fits comfortably in GPT-4 context
- Tested empirically for best results

### 3. LLM Integration (OpenAI GPT-4)

#### Prompt Engineering

```python
def generate_latex_resume(cv_text: str, relevant_sections: str, job_description: str):
    prompt = f"""
    You are an expert resume writer and LaTeX specialist.
    
    **FULL CV CONTENT:**
    {cv_text}
    
    **MOST RELEVANT SECTIONS (from RAG retrieval):**
    {relevant_sections}
    
    **JOB DESCRIPTION:**
    {job_description}
    
    **INSTRUCTIONS:**
    [Detailed instructions...]
    """
```

**Prompt Design Rationale**:

1. **Role Definition**: "expert resume writer and LaTeX specialist"
   - Sets expectations for output quality
   - Activates relevant training data

2. **Context Hierarchy**:
   - Full CV (complete context)
   - Relevant sections (emphasize these)
   - Job description (target requirements)

3. **Explicit Instructions**:
   - Numbered list for clarity
   - Specific requirements
   - Output format constraints

4. **Output Constraints**:
   - "ONLY valid LaTeX code"
   - "NO markdown, NO explanations"
   - Prevents common GPT-4 behaviors

**Model Configuration**:
```python
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,      # Balance creativity/consistency
    max_tokens=4000       # Full resume length
)
```

**Why these settings?**
- GPT-4 Turbo: Best reasoning and instruction-following
- Temperature 0.7: Creative but not random
- Max tokens 4000: Ensures complete output

## RAG Pipeline Deep Dive

### Why Use RAG?

Traditional approaches to resume adaptation:
1. **Simple prompting**: Send entire CV to LLM
   - Problem: Information overload
   - Result: Generic output

2. **Keyword matching**: Basic text search
   - Problem: Misses semantic similarity
   - Result: Rigid matching

3. **RAG approach**: Semantic retrieval + LLM generation
   - Benefit: Finds relevant content intelligently
   - Result: Tailored, coherent resumes

### RAG Workflow

```
1. Indexing Phase (Per CV)
   ┌─────────────┐
   │  CV Text    │
   └──────┬──────┘
          │
   ┌──────▼──────────┐
   │   Text Split    │
   │  (500 chars)    │
   └──────┬──────────┘
          │
   ┌──────▼──────────┐
   │  Embed Chunks   │
   │  (OpenAI API)   │
   └──────┬──────────┘
          │
   ┌──────▼──────────┐
   │  Store Vectors  │
   │    (FAISS)      │
   └─────────────────┘

2. Retrieval Phase (Per Job)
   ┌──────────────────┐
   │ Job Description  │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │  Embed Query     │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Similarity Search│
   │   (k=5 chunks)   │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Relevant Sections│
   └──────────────────┘

3. Generation Phase
   ┌────────┬──────────┬────────┐
   │Full CV │ Relevant │  Job   │
   │        │ Sections │  Desc  │
   └────┬───┴────┬─────┴───┬────┘
        │        │         │
   ┌────▼────────▼─────────▼────┐
   │      GPT-4 Prompt           │
   └────────────┬────────────────┘
                │
   ┌────────────▼────────────────┐
   │    LaTeX Resume Output      │
   └─────────────────────────────┘
```

### Embedding Similarity

**How it works**:
```python
# Conceptual representation
cv_chunk = "5 years Python, Django, REST APIs"
job_desc = "Backend engineer with API experience"

# After embedding (simplified)
cv_vector = [0.2, 0.8, 0.1, ...]      # 1536 dimensions
job_vector = [0.3, 0.7, 0.15, ...]    # 1536 dimensions

# Cosine similarity
similarity = dot(cv_vector, job_vector) / (norm(cv_vector) * norm(job_vector))
# High similarity = Relevant match
```

**What gets matched**:
- Semantic meaning, not just keywords
- "Python developer" ≈ "Python engineer"
- "5 years experience" ≈ "senior level"
- "REST APIs" ≈ "web services"

## Data Flow

### Complete Request Flow

```
1. User Action
   [User uploads CV.pdf + enters job URL]
          │
          ▼
2. Frontend Validation
   - Check file type
   - Validate URL format
   - Display loading state
          │
          ▼
3. HTTP Request
   POST /generate-resume
   FormData: {cv_file, job_url}
          │
          ▼
4. Backend Reception
   - Parse multipart data
   - Validate inputs
          │
          ├──────────────────┐
          ▼                  ▼
5a. PDF Processing      5b. Web Scraping
    - Read bytes            - HTTP request
    - Extract text          - Parse HTML
    - Clean content         - Extract description
          │                  │
          └──────────────────┤
                             ▼
6. RAG Pipeline
   - Chunk CV text
   - Generate embeddings
   - Create vector store
   - Search for relevant sections
          │
          ▼
7. LLM Generation
   - Assemble prompt
   - Call GPT-4 API
   - Parse response
   - Clean LaTeX code
          │
          ▼
8. Response
   JSON: {success, latex_code, message}
          │
          ▼
9. Frontend Display
   - Show LaTeX code
   - Enable copy button
   - Format in code block
```

## Technology Choices

### Backend: FastAPI

**Reasons**:
- ✅ Modern, async framework
- ✅ Automatic API documentation (Swagger/OpenAPI)
- ✅ Fast development
- ✅ Type safety with Pydantic
- ✅ Excellent performance
- ✅ Built-in validation

**Alternatives considered**:
- Flask: Simpler but less features
- Django: Overkill for this project
- Express.js: Would require Node.js backend

### Frontend: React + Vite

**Reasons**:
- ✅ React: Industry standard, large ecosystem
- ✅ Vite: Lightning-fast HMR
- ✅ Modern build tooling
- ✅ Excellent developer experience

**Alternatives considered**:
- Next.js: Overkill (no SSR needed)
- Vue: Smaller ecosystem
- Plain HTML/JS: Limited interactivity

### Vector Store: FAISS

**Reasons**:
- ✅ Fast similarity search
- ✅ No external database
- ✅ Lightweight (CPU-only)
- ✅ Battle-tested at scale

**Alternatives considered**:
- Pinecone: Requires external service
- Chroma: More complex setup
- Weaviate: Infrastructure overhead

### LLM: OpenAI GPT-4

**Reasons**:
- ✅ Best-in-class reasoning
- ✅ Excellent instruction following
- ✅ LaTeX generation capability
- ✅ Reliable API

**Alternatives considered**:
- Claude: No fine-tuning for LaTeX
- Llama 2: Requires self-hosting
- GPT-3.5: Lower quality output

## Security Considerations

### API Key Protection

```python
# Load from environment, never hardcode
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

### Input Validation

```python
# File type checking
if not cv_file.filename.endswith('.pdf'):
    raise HTTPException(status_code=400, detail="Only PDF files")

# Content length validation
if len(cv_text.strip()) < 100:
    raise HTTPException(status_code=400, detail="Insufficient text")
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting (Future)

Consider adding:
- Request rate limits
- API key rotation
- User authentication
- Usage quotas

## Performance Optimization

### Current Optimizations

1. **Async I/O**: FastAPI's async support
2. **Efficient Chunking**: Optimal chunk sizes
3. **Vector Caching**: FAISS in-memory store
4. **Docker Caching**: Layer-based builds

### Performance Metrics

Typical request times:
- PDF extraction: 0.5-2s
- Web scraping: 1-3s
- Embedding generation: 2-4s
- Vector search: <0.1s
- GPT-4 generation: 10-20s
- **Total**: 15-30s

### Bottlenecks

1. **GPT-4 API**: Slowest step
   - Solution: Cannot optimize (external API)
   - Mitigation: Show progress to user

2. **Web Scraping**: Unreliable
   - Solution: Use LinkedIn API (future)
   - Mitigation: Fallback strategies

3. **Embedding Generation**: Batch calls
   - Solution: Process chunks in batches
   - Current: Sequential calls

### Future Optimizations

- [ ] Batch embedding requests
- [ ] Cache common job descriptions
- [ ] Parallel processing for CV chunks
- [ ] CDN for frontend assets
- [ ] Redis for session management
- [ ] Response caching for identical inputs

## Deployment Considerations

### Docker Architecture

```
docker-compose.yml
├── backend (FastAPI)
│   ├── Port: 8000
│   ├── Volumes: ./backend:/app
│   └── Env: OPENAI_API_KEY
│
└── frontend (Nginx + React)
    ├── Port: 3000 → 80
    ├── Build: Multi-stage
    └── Serve: Static files
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (with defaults)
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Production Deployment

For production, consider:
1. **Reverse Proxy**: Nginx for both services
2. **SSL/TLS**: HTTPS certificates
3. **Monitoring**: Application logs, metrics
4. **Scaling**: Multiple backend instances
5. **Database**: Store user sessions, resumes
6. **Caching**: Redis for embeddings

### Infrastructure as Code

Example using AWS:
- **ECS**: Container orchestration
- **ALB**: Load balancing
- **RDS**: PostgreSQL (if needed)
- **S3**: File storage
- **CloudFront**: CDN

## Conclusion

This architecture balances:
- **Simplicity**: Easy to understand and maintain
- **Performance**: Fast enough for real-time use
- **Accuracy**: RAG ensures relevant content
- **Scalability**: Can handle increased load
- **Maintainability**: Clear separation of concerns

The RAG pipeline is the core innovation, enabling intelligent resume adaptation rather than simple templating.
