# UNMAPPED Backend

FastAPI backend for skill extraction and job matching.

## Setup

git clone https://github.com/Feevel/unmapped.git
cd unmapped

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

## Run

python -m uvicorn app.main:app --reload

## API Docs

http://127.0.0.1:8000/docs