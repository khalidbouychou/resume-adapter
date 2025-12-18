import os
import io
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file: bytes) -> str:
    """Extract text from uploaded PDF file"""
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_file)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    return text

def fetch_linkedin_job_description(url: str) -> str:
    """
    Fetch job description from LinkedIn URL
    Note: LinkedIn has anti-scraping measures. This is a basic implementation.
    For production, consider using LinkedIn API or browser automation.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find job description in common LinkedIn selectors
        job_desc = ""
        
        # Look for description in various possible containers
        selectors = [
            'div.description__text',
            'div.show-more-less-html__markup',
            'section.description',
            'div[class*="description"]',
            'div[class*="job-description"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                job_desc = elements[0].get_text(separator='\n', strip=True)
                break
        
        # Fallback: get all text if specific selectors don't work
        if not job_desc:
            # Get main content area
            main_content = soup.find('main') or soup.find('body')
            if main_content:
                job_desc = main_content.get_text(separator='\n', strip=True)
        
        return job_desc if job_desc else "Could not extract job description. Please check the URL."
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch job description: {str(e)}")

def create_rag_retriever(cv_text: str):
    """
    Create RAG retriever from CV text using FAISS and OpenAI embeddings
    """
    # Split CV into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    
    chunks = text_splitter.split_text(cv_text)
    documents = [Document(page_content=chunk) for chunk in chunks]
    
    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    return vectorstore

def retrieve_relevant_cv_sections(vectorstore, job_description: str, k: int = 5) -> str:
    """
    Retrieve relevant sections from CV based on job description
    """
    # Search for relevant CV sections
    docs = vectorstore.similarity_search(job_description, k=k)
    
    # Combine retrieved sections
    relevant_sections = "\n\n".join([doc.page_content for doc in docs])
    return relevant_sections

def generate_latex_resume(cv_text: str, relevant_sections: str, job_description: str) -> str:
    """
    Generate adapted LaTeX resume using OpenAI GPT-4
    """
    
    prompt = f"""You are an expert resume writer and LaTeX specialist. Your task is to create a tailored, professional resume in LaTeX format.

**FULL CV CONTENT:**
{cv_text}

**MOST RELEVANT SECTIONS (from RAG retrieval):**
{relevant_sections}

**JOB DESCRIPTION:**
{job_description}

**INSTRUCTIONS:**
1. Analyze the job description and identify key requirements, skills, and qualifications
2. Use the FULL CV content as your source material
3. Emphasize and prioritize experiences, skills, and achievements that match the job requirements
4. Reorganize and reword bullet points to align with the job description keywords
5. Keep the resume concise (1-2 pages maximum)
6. Output ONLY valid LaTeX code - no explanations, no markdown, no comments
7. Use a clean, professional LaTeX resume template
8. Include sections: Contact Info, Summary/Objective, Experience, Education, Skills, and any other relevant sections from the CV

**OUTPUT REQUIREMENTS:**
- Return ONLY the complete LaTeX document code
- Start with \\documentclass and end with \\end{{document}}
- Use standard LaTeX packages (geometry, enumitem, hyperref, etc.)
- Make it compile-ready
- NO markdown code blocks, NO explanations, NO preamble
- Just pure LaTeX code"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert LaTeX resume writer. Output only valid LaTeX code with no explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        latex_code = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if latex_code.startswith("```latex"):
            latex_code = latex_code.replace("```latex", "").replace("```", "").strip()
        elif latex_code.startswith("```"):
            latex_code = latex_code.replace("```", "").strip()
        
        return latex_code
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate resume: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Resume Adapter API", "status": "running"}

@app.post("/generate-resume")
async def generate_resume(
    cv_file: UploadFile = File(...),
    job_url: str = Form(...)
):
    """
    Main endpoint to generate adapted resume
    """
    try:
        # Validate file type
        if not cv_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Extract text from CV
        pdf_content = await cv_file.read()
        cv_text = extract_text_from_pdf(pdf_content)
        
        if not cv_text or len(cv_text.strip()) < 100:
            raise HTTPException(status_code=400, detail="Could not extract sufficient text from PDF")
        
        # Fetch job description
        job_description = fetch_linkedin_job_description(job_url)
        
        if len(job_description.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract sufficient job description")
        
        # Create RAG retriever
        vectorstore = create_rag_retriever(cv_text)
        
        # Retrieve relevant sections
        relevant_sections = retrieve_relevant_cv_sections(vectorstore, job_description)
        
        # Generate LaTeX resume
        latex_code = generate_latex_resume(cv_text, relevant_sections, job_description)
        
        return {
            "success": True,
            "latex_code": latex_code,
            "message": "Resume generated successfully"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "openai_key_set": bool(os.getenv("OPENAI_API_KEY"))}
