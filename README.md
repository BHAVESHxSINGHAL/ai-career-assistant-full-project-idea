# AI Career Assistant

A full-stack MVP for resume analysis, job matching, interview preparation, career chat, and cover letter generation.

## Features

- Resume upload or pasted text analysis
- Skill, education, and experience extraction
- Resume score with explanation
- Job role recommendations with match percentages
- Skill gap analysis and career roadmap hints
- Local career chatbot with optional Hugging Face API fallback
- Interview question generator
- Cover letter generator

## Tech Stack

- Frontend: React, Vite, lucide-react
- Backend: Python, FastAPI, Pydantic
- NLP: keyword and pattern extraction, with optional PDF parsing through `pypdf`
- LLM: optional Hugging Face Inference API via `HF_API_TOKEN`
- Database: ready to extend with MongoDB; current MVP uses stateless API responses

## Run Locally

Backend:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the frontend at `http://127.0.0.1:5173`.

## Optional Environment

Copy `backend/.env.example` to `backend/.env` and set:

```powershell
HF_API_TOKEN=your_hugging_face_token
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3
```

The app still works without these variables by using local deterministic responses.

## API

- `POST /api/resume/analyze`: upload `.txt` or `.pdf`
- `POST /api/resume/analyze-text`: analyze pasted resume text
- `POST /api/jobs/recommend`: return matched roles from skills
- `POST /api/chat`: ask career questions using resume context
- `POST /api/interview`: generate technical and HR interview questions
- `POST /api/cover-letter`: generate a role-specific cover letter

## Next Improvements

- Add MongoDB persistence for users, resumes, analyses, and chat history
- Add spaCy entity extraction for stronger NLP
- Add authentication and saved career plans
- Add multilingual resume support
- Add real job listings from an external API
