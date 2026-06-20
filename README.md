<div align="center">

# 🎙️ InterviewIQ

### AI-Powered Interview Preparation & Career Readiness Platform

[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-blue?style=for-the-badge)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-LLM-orange?style=for-the-badge)](https://groq.com/)

<br/>

<a href="https://interview-iq-8c6r.onrender.com/">
  <img src="https://img.shields.io/badge/LIVE_DEMO-VISIT_NOW-success?style=for-the-badge" />
</a>

<a href="https://github.com/Sp-bit-code/Interview-IQ">
  <img src="https://img.shields.io/badge/GITHUB-REPOSITORY-black?style=for-the-badge&logo=github" />
</a>

</div>

---

## 📌 Project Overview

InterviewIQ is a modern AI-powered interview preparation platform designed to help students, freshers, and job seekers prepare effectively for placements and technical interviews.

The platform combines Artificial Intelligence, Retrieval-Augmented Generation (RAG), resume analysis, flashcard generation, and voice-based mock interviews into a single ecosystem.

Users can:

- Practice AI-powered mock interviews
- Study directly from uploaded PDF notes
- Compare resumes against job descriptions
- Generate smart flashcards and MCQs
- Receive personalized interview feedback
- Improve technical and HR interview readiness

---

## 🚀 Live Deployment

### 🌐 Website

https://interview-iq-8c6r.onrender.com/

### 📂 GitHub Repository

https://github.com/Sp-bit-code/Interview-IQ

---

# ✨ Key Features

## 🎤 AI Mock Interview System

Conduct realistic interview sessions using AI.

### Features

- Voice-based interview interactions
- Technical interview practice
- HR interview simulation
- Custom Job Description interviews
- Dynamic question generation
- AI-generated performance feedback
- Session reports and analysis

---

## 📚 RAG Study Assistant

Upload your study materials and interact with them intelligently.

### Features

- PDF Upload Support
- Document Processing
- Text Chunking
- Embedding Generation
- Vector Search
- Semantic Retrieval
- Context-Aware Responses

### Technologies

- LangChain
- FAISS / Vector Store
- Embedding Models
- Retrieval-Augmented Generation (RAG)

---

## 📄 Resume Gap Finder

Analyze how well your resume matches a target role.

### Features

- Resume Upload
- Job Description Analysis
- Skill Gap Detection
- ATS Improvement Suggestions
- Missing Keywords Identification
- Resume Optimization Recommendations

---

## 🧠 Flashcard Generator

Generate smart revision content automatically.

### Features

- MCQ Generation
- Concept Revision
- AI-Based Question Creation
- Quick Learning Support
- Placement Preparation

---

# 🏗️ System Architecture

```text
Frontend (React + Vite)
          │
          ▼
     FastAPI APIs
          │
 ┌────────┼────────┐
 ▼        ▼        ▼
Groq     RAG    Supabase
LLM     Engine   Database
          │
          ▼
      Vector Store
          │
          ▼
      PDF Documents
```

---

# 🛠️ Tech Stack

## Frontend

- React.js
- Vite
- React Router
- Tailwind CSS
- JavaScript

## Backend

- FastAPI
- Python
- LangChain
- Groq API

## Database

- Supabase

## AI Technologies

- LLM Integration
- RAG Architecture
- Embeddings
- Semantic Search
- Prompt Engineering

---

# 📂 Project Structure

```text
Interview-IQ
│
├── frontend/
│   ├── src/
│   ├── pages/
│   ├── components/
│   ├── store/
│   └── assets/
│
├── backend/
│   ├── app/
│   ├── rag/
│   ├── routes/
│   ├── services/
│   └── utils/
│
├── uploads/
├── vector_store/
├── requirements.txt
└── README.md
```

---

# 🔄 Application Workflow

## Mock Interview Flow

```text
User
 ↓
Select Interview Type
 ↓
AI Generates Questions
 ↓
User Responds
 ↓
AI Evaluates Answers
 ↓
Performance Report
```

---

## RAG Workflow

```text
PDF Upload
 ↓
Text Extraction
 ↓
Chunking
 ↓
Embeddings
 ↓
Vector Database
 ↓
Semantic Search
 ↓
AI Response
```

---

## Resume Analysis Workflow

```text
Resume Upload
 ↓
Job Description Input
 ↓
Skill Comparison
 ↓
Gap Detection
 ↓
Improvement Suggestions
```

---

# 📸 Screenshots

## Landing Page

Add your screenshots inside:

```text
frontend/public/screenshots/
```

Example:

```md
![Landing Page](./screenshots/landing-page.png)

![Mock Interview](./screenshots/mock-interview.png)

![Study Assistant](./screenshots/study-assistant.png)

![Resume Gap Finder](./screenshots/resume-gap-finder.png)
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/Sp-bit-code/Interview-IQ.git

cd Interview-IQ
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## Backend Setup

```bash
cd backend

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

# 🔐 Environment Variables

Create a `.env` file.

```env
GROQ_API_KEY=your_groq_key

SUPABASE_URL=your_supabase_url

SUPABASE_KEY=your_supabase_key

OPENAI_API_KEY=optional
```

---

# 🎯 Use Cases

### Students

- Placement preparation
- Technical interview practice
- Resume improvement

### Freshers

- HR interview readiness
- Skill gap analysis
- Resume optimization

### Job Seekers

- Mock interviews
- ATS preparation
- Personalized feedback

---

# 📈 Future Enhancements

- Video Interview Analysis
- AI Career Guidance
- Multi-Language Interviews
- Coding Interview Simulator
- Analytics Dashboard
- Performance Tracking
- AI Resume Builder
- Company-Specific Interview Preparation

---

# 👨‍💻 Developers

## Sparsh Srivastava

**Full Stack Developer | AI Developer**

- React.js
- FastAPI
- Supabase
- LangChain
- RAG Systems
- Groq LLM Integration

### Links

<a href="https://github.com/Sp-bit-code">
<img src="https://img.shields.io/badge/GitHub-Profile-black?style=for-the-badge&logo=github"/>
</a>

<a href="https://www.linkedin.com/in/sparsh-srivastava-621882289/">
<img src="https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin"/>
</a>

---

## Ayushi Chauhan

**MERN Stack Developer**

- MongoDB
- Express.js
- React.js
- Node.js

### Links

<a href="https://github.com/Ayushi-2564">
<img src="https://img.shields.io/badge/GitHub-Profile-black?style=for-the-badge&logo=github"/>
</a>

<a href="https://www.linkedin.com/in/ayushi-chauhan-4b1514330/">
<img src="https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin"/>
</a>

---

# ⭐ Support

If you found this project useful:

⭐ Star the repository

🍴 Fork the project

🛠️ Contribute improvements

📢 Share with others

---

<div align="center">

### 🎯 Practice • Learn • Improve • Get Hired

Made with ❤️ using AI, RAG, React, FastAPI, Supabase & LangChain

</div>
