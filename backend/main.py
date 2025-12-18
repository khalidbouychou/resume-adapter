import os
import io
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Allow all Codespaces/app.github.dev origins; helpful for dev URLs
    allow_origin_regex=r"https://.*\.app\.github\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face configuration is provided per-request via env vars

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

def generate_latex_resume(cv_text: str, job_description: str) -> str:
    """
    Generate adapted LaTeX resume using selected provider with fallbacks.
    Supported providers: huggingface, openai, deepseek, grok (xAI). Configure with env vars.
    """

    prompt = f"""You are an expert resume writer and LaTeX specialist. Your task is to create a tailored, professional resume in LaTeX format.

**FULL CV CONTENT:**
{cv_text}

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

    def _is_rate_limit_error(exc: Exception) -> bool:
        msg = str(exc).upper()
        # Consider typical transient conditions (rate limit, model loading, 5xx)
        return (
            "429" in msg
            or "503" in msg
            or "RATE" in msg
            or "QUOTA" in msg
            or "MODEL IS CURRENTLY LOADING" in msg
            or "PLEASE TRY AGAIN" in msg
        )

    @retry(
        retry=retry_if_exception(_is_rate_limit_error),
        wait=wait_random_exponential(multiplier=2, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _generate_with_huggingface(p: str):
        hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        model_id = os.getenv("HUGGINGFACE_MODEL", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16")
        if not hf_api_key:
            raise RuntimeError("HUGGINGFACE_API_KEY is not set")

        url = f"https://router.huggingface.co/models/{model_id}"
        headers = {
            "Authorization": f"Bearer {hf_api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": p,
            "parameters": {
                "max_new_tokens": int(os.getenv("HF_MAX_NEW_TOKENS", "900")),
                "temperature": float(os.getenv("HF_TEMPERATURE", "0.7")),
                "return_full_text": False,
            },
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        # Handle common transient statuses
        if resp.status_code in (429, 503):
            # Bubble up for retry/backoff
            raise RuntimeError(f"HuggingFace transient error: {resp.status_code} {resp.text}")
        if not resp.ok:
            # Non-retryable error
            raise HTTPException(status_code=resp.status_code, detail=f"HuggingFace error: {resp.text}")

        try:
            data = resp.json()
        except Exception:
            # Fallback to raw text
            return (resp.text or "").strip()

        # Response formats: list of {generated_text: ...} or dicts
        if isinstance(data, list) and data and isinstance(data[0], dict) and "generated_text" in data[0]:
            return (data[0]["generated_text"] or "").strip()
        if isinstance(data, dict) and "generated_text" in data:
            return (data["generated_text"] or "").strip()

        # Some models return a list of tokens or alternative fields; fallback to string conversion
        return (str(data) or "").strip()

    @retry(
        retry=retry_if_exception(_is_rate_limit_error),
        wait=wait_random_exponential(multiplier=2, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _generate_with_openai_like(p: str, api_key: str, base_url: str, model_name: str):
        client = OpenAI(api_key=api_key, base_url=base_url)
        chat = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert resume writer and LaTeX specialist."},
                {"role": "user", "content": p},
            ],
            temperature=0.7,
        )
        return (chat.choices[0].message.content or "").strip()

    providers_order = [p.strip().lower() for p in os.getenv("PROVIDER_ORDER", "huggingface,openrouter,openai,deepseek,grok").split(",")]

    last_error: Optional[Exception] = None

    for provider in providers_order:
        try:
            print(f"[DEBUG] Attempting provider: {provider}")
            if provider == "huggingface":
                if not os.getenv("HUGGINGFACE_API_KEY"):
                    print(f"[DEBUG] Skipping {provider}: no API key")
                    continue
                latex_code = _generate_with_huggingface(prompt)
            elif provider in ("openrouter", "openai", "deepseek", "grok"):
                if provider == "openrouter":
                    api_key = os.getenv("OPENROUTER_API_KEY")
                    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
                    model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
                    headers = {}
                    if os.getenv("OPENROUTER_REFERER"):
                        headers["HTTP-Referer"] = os.getenv("OPENROUTER_REFERER")
                    if os.getenv("OPENROUTER_TITLE"):
                        headers["X-Title"] = os.getenv("OPENROUTER_TITLE")
                elif provider == "openai":
                    api_key = os.getenv("OPENAI_API_KEY")
                    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
                    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                    headers = None
                elif provider == "deepseek":
                    api_key = os.getenv("DEEPSEEK_API_KEY")
                    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
                    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
                    headers = None
                else:  # grok (xAI)
                    api_key = os.getenv("XAI_API_KEY")
                    base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
                    model_name = os.getenv("XAI_MODEL", "grok-2-mini")
                    headers = None

                if not api_key:
                    print(f"[DEBUG] Skipping {provider}: no API key")
                    continue

                latex_code = _generate_with_openai_like(prompt, api_key, base_url, model_name, headers)
            else:
                continue

            # Remove markdown code blocks if present
            if latex_code.startswith("```latex"):
                latex_code = latex_code.replace("```latex", "").replace("```", "").strip()
            elif latex_code.startswith("```"):
                latex_code = latex_code.replace("```", "").strip()

            if latex_code:
                print(f"[DEBUG] Successfully generated with {provider}")
                return latex_code
            last_error = ValueError("Empty response from model")
            print(f"[DEBUG] {provider} returned empty response")
        except Exception as e:
            last_error = e
            print(f"[DEBUG] {provider} failed: {type(e).__name__}: {str(e)[:200]}")
            # Try next provider on failure
            continue

    # If all providers failed, return generic busy message with hint
    error_msg = "The service is busy right now. Please try again in a minute."
    if last_error:
        print(f"[ERROR] All providers failed. Last error: {type(last_error).__name__}: {str(last_error)[:500]}")
    raise HTTPException(status_code=503, detail=error_msg)

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
        
        print(f"[DEBUG] Extracted CV text length: {len(cv_text.strip())} characters")
        if not cv_text or len(cv_text.strip()) < 100:
            raise HTTPException(status_code=400, detail=f"Could not extract sufficient text from PDF. Extracted {len(cv_text.strip()) if cv_text else 0} characters. Ensure the PDF is text-based (not scanned).")
        
        # Fetch job description
        job_description = fetch_linkedin_job_description(job_url)
        
        if len(job_description.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract sufficient job description")
        
        # Generate LaTeX resume directly with Gemini
        latex_code = generate_latex_resume(cv_text, job_description)
        
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
    return {
        "status": "healthy",
        "huggingface_api_key_set": bool(os.getenv("HUGGINGFACE_API_KEY")),
        "huggingface_model": os.getenv("HUGGINGFACE_MODEL", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"),
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "deepseek_api_key_set": bool(os.getenv("DEEPSEEK_API_KEY")),
        "xai_api_key_set": bool(os.getenv("XAI_API_KEY")),
    }
