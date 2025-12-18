# Quick Start Guide

Get up and running with Resume Adapter in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd resume-adapter
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# On macOS/Linux:
nano .env

# On Windows:
notepad .env
```

Add your API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Build and Run with Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d
```

Wait for the services to start (usually 1-2 minutes).

### 4. Open the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

## Using the Application

### Step-by-Step Usage

1. **Prepare Your CV**
   - Save your CV as a PDF file
   - Ensure it's text-based (not scanned)

2. **Find a Job Posting**
   - Go to LinkedIn Jobs
   - Find a job you're interested in
   - Copy the full URL (e.g., `https://www.linkedin.com/jobs/view/1234567890`)

3. **Generate Your Resume**
   - Click the upload area and select your CV PDF
   - Paste the LinkedIn job URL in the text field
   - Click "Generate Adapted Resume"
   - Wait 15-30 seconds for processing

4. **Use the LaTeX Code**
   - Copy the generated LaTeX code
   - Paste it into a LaTeX editor:
     - **Online**: [Overleaf](https://www.overleaf.com) (recommended)
     - **Desktop**: TeXShop (Mac), TeXworks (Windows), TeXstudio (all platforms)
   - Compile to PDF
   - Download your tailored resume!

## Troubleshooting

### Common Issues

#### "Could not extract text from PDF"
**Cause**: Your PDF might be scanned or image-based

**Solution**:
1. Try exporting your CV as PDF from a word processor
2. Use "Print to PDF" instead of "Save as PDF"
3. Ensure the PDF has selectable text

#### "Failed to fetch job description"
**Cause**: LinkedIn's anti-scraping measures or invalid URL

**Solution**:
1. Verify the URL is a direct job posting link
2. Try a different job posting
3. Check if you can access the URL in a browser

#### "OpenAI API error"
**Cause**: Invalid API key or insufficient credits

**Solution**:
1. Check your API key in `.env` is correct
2. Verify your OpenAI account has credits
3. Check [OpenAI status page](https://status.openai.com)

#### Backend won't start
**Cause**: Port already in use or Docker issues

**Solution**:
```bash
# Stop all containers
docker-compose down

# Check what's using port 8000
# On macOS/Linux:
lsof -i :8000

# On Windows:
netstat -ano | findstr :8000

# Start again
docker-compose up
```

## Alternative: Local Development

If you prefer running without Docker:

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Access at:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical deep dive
- Review [PROMPT_DOCUMENTATION.md](PROMPT_DOCUMENTATION.md) for prompt engineering details

## Getting Help

If you encounter issues:

1. Check the logs:
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. Verify services are running:
   ```bash
   docker-compose ps
   ```

3. Check backend health:
   ```bash
   curl http://localhost:8000/health
   ```

4. Restart services:
   ```bash
   docker-compose restart
   ```

## Tips for Best Results

### CV Preparation
- Use clear section headers (Experience, Education, Skills)
- Include quantifiable achievements
- Keep formatting simple
- Ensure all text is selectable

### Job URL Selection
- Use direct LinkedIn job URLs
- Avoid shortened URLs
- Make sure the job is still active
- LinkedIn is preferred, but other job sites may work

### LaTeX Compilation
- Overleaf is the easiest option (no installation needed)
- First compilation might take a few seconds
- Check for any LaTeX errors (rare, but possible)
- Feel free to customize the generated code

## Example Workflow

```
1. Export CV from Word/Google Docs as PDF
   ↓
2. Save to Desktop/Downloads
   ↓
3. Find job on LinkedIn
   ↓
4. Copy job URL (right-click → Copy Link)
   ↓
5. Open http://localhost:3000
   ↓
6. Upload PDF
   ↓
7. Paste URL
   ↓
8. Click Generate
   ↓
9. Wait 20 seconds
   ↓
10. Copy LaTeX code
   ↓
11. Open Overleaf.com
   ↓
12. Create new project → Blank Project
   ↓
13. Replace main.tex content
   ↓
14. Click Recompile
   ↓
15. Download PDF
   ↓
16. Your tailored resume is ready! 🎉
```

## Stopping the Application

```bash
# Stop containers (keep data)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove, and clean up everything
docker-compose down -v
```

## Updating

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose up --build
```

---

**Happy job hunting! 🚀**
