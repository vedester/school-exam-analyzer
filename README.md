# School Exam Analyzer SaaS 🚀

A full-stack SaaS platform that automates exam grading for Kenyan schools.
Teachers upload an Excel file, and the system auto-calculates ranks, means, and subject performance.

## Tech Stack
- **Backend:** Python (Django Rest Framework) + Pandas (Data Analysis).
- **Frontend:** Next.js (React) + Tailwind CSS.
- **Database:** SQLite (Dev) / PostgreSQL (Prod).

## Features
- Smart Column Detection (detects Math/Eng vs Phone Numbers).
- Instant Excel Report Generation.
- REST API architecture.

## How to Run Locally
1. Backend: `cd backend && python manage.py runserver`
2. Frontend: `cd frontend && npm run dev`