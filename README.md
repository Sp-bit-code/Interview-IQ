<div align="center">

# 🎙️ InterviewIQ

### AI-Powered Interview Preparation Platform

Practice interviews, learn from your notes, analyze resume gaps, and generate flashcards using AI.

<br/>

<a href="https://interview-iq-8c6r.onrender.com/" target="_blank">
  <img src="https://img.shields.io/badge/🚀_Live_Demo-Visit_Now-22c55e?style=for-the-badge" />
</a>

<a href="https://github.com/Sp-bit-code/Interview-IQ" target="_blank">
  <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github" />
</a>

</div>

---

## 📌 Overview

InterviewIQ is an AI-powered placement preparation platform designed for students, freshers, and job seekers.

The platform combines AI interview practice, Retrieval-Augmented Generation (RAG), resume analysis, and flashcard generation into a single application that helps users prepare more effectively for technical and HR interviews.

Users can practice mock interviews, study directly from PDF notes, identify resume gaps against job descriptions, and generate revision-friendly flashcards using modern AI technologies.

---

# ✨ Core Features

## 🎤 AI Mock Interview

Practice interviews with AI-generated questions.

### Features

- Voice-based interview experience
- Technical interview preparation
- HR interview preparation
- Custom Job Description interviews
- AI-generated interview feedback
- Session-based interview workflow

---

## 📘 Study Notes Assistant (RAG)

Upload study material and interact with it using natural language.

### Features

- PDF upload support
- Retrieval-Augmented Generation (RAG)
- Context-aware responses
- Intelligent document search
- Learning-focused question answering

---

## 📄 Resume Gap Finder

Compare your resume against a job description.

### Features

- Resume analysis
- JD comparison
- Missing skill identification
- Gap detection
- Improvement suggestions

---

## 🧠 Flashcard Generator

Generate revision material automatically.

### Features

- AI-generated flashcards
- MCQ creation
- Concept revision
- Quick learning workflow

---

# 🏗️ System Architecture

```text
Frontend (React)
       │
       ▼
FastAPI Backend
       │
       ├── Groq LLM
       │
       ├── LangChain
       │
       ├── RAG Pipeline
       │
       ├── PDF Processing
       │
       └── Resume Analysis
       │
       ▼
Supabase
(Authentication + Database)
