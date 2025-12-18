# OpenAI Prompt Documentation

This document contains the exact prompt used to generate LaTeX resumes, along with explanations of design choices.

## Complete Prompt Template

```python
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
```

## System Message

```python
system_message = "You are an expert LaTeX resume writer. Output only valid LaTeX code with no explanations."
```

## Model Configuration

```python
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=4000
)
```

## Prompt Engineering Breakdown

### 1. Role Definition
**Text**: "You are an expert resume writer and LaTeX specialist."

**Why**: 
- Sets the context and expertise level
- Activates relevant training data
- Improves output quality and accuracy

### 2. Three-Part Context Structure

#### Part A: Full CV Content
**Purpose**: Complete context for comprehensive understanding

**Why include full CV**:
- Prevents hallucination
- Provides all available information
- Allows model to see full career trajectory

#### Part B: Relevant Sections (RAG)
**Purpose**: Highlight most important matching content

**Why separate from full CV**:
- Emphasizes key matching experiences
- Guides the model's attention
- Ensures relevant content is prioritized

#### Part C: Job Description
**Purpose**: Target requirements and keywords

**Why explicit separation**:
- Clear matching objective
- Enables keyword alignment
- Guides content reorganization

### 3. Numbered Instructions

**Why numbered**:
- Clear sequence of operations
- Easy to follow
- Reduces ambiguity

**Key Instructions Explained**:

1. **"Analyze the job description"**
   - Forces deliberate analysis
   - Better matching results

2. **"Use the FULL CV content"**
   - Prevents content invention
   - Ensures accuracy

3. **"Emphasize and prioritize"**
   - Active instruction for adaptation
   - Not just copying

4. **"Reorganize and reword"**
   - Encourages tailoring
   - Aligns with job keywords

5. **"Keep concise (1-2 pages)"**
   - Prevents verbosity
   - Industry standard

6. **"Output ONLY valid LaTeX"**
   - Critical constraint
   - Prevents common GPT-4 behavior

7. **"Use clean, professional template"**
   - Quality guidance
   - Aesthetic standards

8. **"Include sections..."**
   - Structure specification
   - Completeness check

### 4. Output Requirements

**Multiple redundant constraints**:
- "Return ONLY the complete LaTeX document code"
- "NO markdown code blocks, NO explanations, NO preamble"
- "Just pure LaTeX code"

**Why redundancy**:
- GPT-4 has strong tendency to explain
- Multiple constraints increase compliance
- Different phrasings catch different cases

### 5. Technical Specifications

**LaTeX-specific requirements**:
- "Start with \\documentclass and end with \\end{document}"
- "Use standard LaTeX packages"
- "Make it compile-ready"

**Why explicit**:
- Ensures completeness
- Prevents partial output
- Guarantees usability

## Temperature Selection: 0.7

**Why 0.7**:
- Balance between creativity and consistency
- Allows rephrasing and adaptation
- Not too random (0.9+) or too rigid (0.3-)
- Good for creative writing tasks

**Alternatives**:
- 0.3: Too rigid, mechanical output
- 0.5: Good, slightly less creative
- 0.9: Too random, inconsistent

## Max Tokens: 4000

**Why 4000**:
- Full resume typically 1500-3000 tokens
- Safety margin for longer resumes
- Prevents truncation

**Cost consideration**:
- ~4000 tokens = ~$0.12 per request (GPT-4 Turbo)
- Acceptable for quality output

## Common GPT-4 Behaviors to Prevent

### Problem 1: Markdown Code Blocks
**GPT-4 often outputs**:
```
Here's the LaTeX code:
```latex
\documentclass{article}
...
```

**Prevention**:
- Multiple explicit constraints
- System message reinforcement
- Post-processing cleanup

**Code cleanup**:
```python
if latex_code.startswith("```latex"):
    latex_code = latex_code.replace("```latex", "").replace("```", "").strip()
```

### Problem 2: Explanations Before/After Code
**GPT-4 often adds**:
- "I'll create a tailored resume..."
- "This resume emphasizes..."
- "Let me know if you need changes..."

**Prevention**:
- "NO explanations" constraint
- "ONLY valid LaTeX code"
- System message focus

### Problem 3: Incomplete Output
**GPT-4 sometimes stops early**

**Prevention**:
- Sufficient max_tokens
- Explicit completeness requirement
- "Start with X and end with Y" constraint

## Example Input/Output

### Example Input

**CV Text** (abbreviated):
```
John Doe
john@example.com

EXPERIENCE:
Senior Software Engineer at TechCorp (2020-2023)
- Developed RESTful APIs using Python and Django
- Led team of 4 engineers
- Implemented CI/CD pipelines

Software Engineer at StartupXYZ (2018-2020)
- Built microservices architecture
- Used Docker and Kubernetes
...
```

**Job Description** (abbreviated):
```
Backend Engineer position at CloudCompany

Requirements:
- 5+ years Python experience
- Strong API development skills
- Experience with cloud platforms (AWS/GCP)
- Docker/Kubernetes knowledge
- Team leadership experience
...
```

**Relevant Sections** (from RAG):
```
Senior Software Engineer at TechCorp (2020-2023)
- Developed RESTful APIs using Python and Django
- Led team of 4 engineers

Built microservices architecture
- Used Docker and Kubernetes
```

### Example Output

```latex
\documentclass[11pt,a4paper]{article}
\usepackage[left=0.75in,right=0.75in,top=0.75in,bottom=0.75in]{geometry}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{titlesec}

\titleformat{\section}{\large\bfseries}{}{0em}{}[\titlerule]
\titleformat{\subsection}[runin]{\bfseries}{}{0em}{}

\begin{document}

\begin{center}
{\LARGE \textbf{John Doe}}\\[0.3em]
\href{mailto:john@example.com}{john@example.com}
\end{center}

\section*{Professional Summary}
Backend engineer with 5+ years of Python expertise, specializing in API development and cloud infrastructure. Proven track record of leading teams and implementing scalable microservices architectures using Docker and Kubernetes.

\section*{Technical Skills}
\textbf{Languages:} Python, SQL \\
\textbf{Frameworks:} Django, FastAPI, Flask \\
\textbf{Cloud:} AWS, Docker, Kubernetes \\
\textbf{Tools:} Git, CI/CD, Jenkins

\section*{Professional Experience}

\subsection*{Senior Software Engineer} \hfill 2020 -- 2023
\textit{TechCorp} \hfill \textit{Remote}
\begin{itemize}[noitemsep,topsep=0pt]
\item Architected and developed RESTful APIs using Python and Django, serving 100K+ daily requests
\item Led cross-functional team of 4 engineers in agile development cycles
\item Implemented comprehensive CI/CD pipelines, reducing deployment time by 60\%
\item Deployed microservices on AWS using Docker and Kubernetes for high availability
\end{itemize}

\subsection*{Software Engineer} \hfill 2018 -- 2020
\textit{StartupXYZ} \hfill \textit{San Francisco, CA}
\begin{itemize}[noitemsep,topsep=0pt]
\item Designed and built microservices architecture from monolithic application
\item Containerized applications using Docker and orchestrated with Kubernetes
\item Developed Python-based backend services with 99.9\% uptime
\end{itemize}

\section*{Education}

\subsection*{Bachelor of Science in Computer Science} \hfill 2014 -- 2018
University Name

\end{document}
```

## Key Adaptations in Output

1. **Summary rewritten**: Emphasizes "Backend engineer", "API development", "cloud infrastructure" - all from job description

2. **Skills reorganized**: Cloud and containerization skills highlighted first

3. **Experience bullets enhanced**:
   - "RESTful APIs" → "Architected and developed RESTful APIs"
   - Added AWS mention (inferred from context)
   - Emphasized team leadership
   - Highlighted Docker/Kubernetes

4. **Quantification added**: "100K+ daily requests", "60%", "99.9%"

5. **LaTeX structure**: Clean, professional, compile-ready

## Variations and Fine-tuning

### For Entry-Level Positions
Consider adjusting:
```python
"Keep the resume concise (1 page maximum)"
"Emphasize education and projects over experience"
```

### For Executive Positions
Consider adjusting:
```python
"Keep the resume concise (2 pages)"
"Emphasize leadership, strategy, and business impact"
```

### For Academic Positions
Consider adjusting:
```python
"Include publications, grants, and teaching experience"
"Use academic CV format with detailed sections"
```

## Prompt Versioning

### Version 1.0 (Current)
- Three-part context structure
- Multiple output constraints
- Standard resume format

### Future Improvements (v1.1)
- [ ] Template selection parameter
- [ ] Industry-specific guidance
- [ ] ATS optimization instructions
- [ ] Keyword density requirements

## Testing and Validation

### Quality Checks
1. **Completeness**: Contains all sections
2. **Accuracy**: No hallucinated information
3. **Relevance**: Matches job requirements
4. **Compilability**: Valid LaTeX syntax
5. **Length**: Appropriate page count

### Common Issues and Fixes

**Issue**: Output includes markdown
**Fix**: Enhanced post-processing

**Issue**: Missing contact information
**Fix**: Explicit instruction added

**Issue**: Too verbose
**Fix**: Page limit constraint

**Issue**: Generic content
**Fix**: RAG retrieval emphasis

## Conclusion

This prompt template balances:
- Comprehensive context (full CV)
- Focused attention (RAG sections)
- Clear objectives (job matching)
- Strict constraints (LaTeX-only output)

The redundancy in constraints is intentional and necessary to override GPT-4's default behaviors.
