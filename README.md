IELTS Speaking Test Simulation

Overview

This project is a real-time IELTS Speaking Test simulation tool that allows users to practice speaking English and receive performance assessments based on IELTS criteria. It runs locally and consists of:

A backend powered by DistilGPT-2 for generating responses.

Google's Speech-to-Text API for real-time transcription.

A frontend built with React, running on GitHub Codespaces.

Features

1. Real-Time Conversation

Uses Google's Speech-to-Text API for converting speech into text.

DistilGPT-2 generates responses based on user input.

Supports minimal delay for a smooth conversation experience.

2. IELTS Scoring Simulation

Fluency & Coherence: Evaluates timing, pauses, and logical flow.

Lexical Resource: Assesses vocabulary usage and provides suggestions.

Grammar & Accuracy: Checks sentence structure and correctness.

Pronunciation Feedback: Uses phoneme-level analysis (if applicable).

3. Session Modes

Practice Mode: Instant feedback after each response.

Test Mode: A full IELTS Speaking Test simulation with three parts:

Introduction (Personal Questions)

Long Turn (Cue Card Activity)

Two-Way Discussion

4. Custom Feedback

Users can download a PDF report with scores and improvement areas.

Installation and Setup

1. Clone the Repository

git clone https://github.com/khanyisani-ui/ai_integrator.git
cd iets_speaking_sim

2. Install Backend Dependencies

pip install -r requirements.txt

3. Run the Backend (Locally)

uvicorn main:app --host 0.0.0.0 --port 8000

4. Run the Frontend (on GitHub Codespaces or Locally)

npm install
npm run dev

Usage

Access the frontend at http://localhost:3000 (or Codespaces URL).

Speak into the microphone and receive real-time feedback.

Toggle between Practice Mode and Test Mode.

API Information

Google's Speech-to-Text API: Used for transcription.

DistilGPT-2: Generates examiner-like responses.

Local API Endpoints:

/transcribe/ → Handles speech-to-text conversion.

/generate_response/ → Processes input and generates responses.

/score_response/ → Evaluates fluency, grammar, and vocabulary.

Known Issues

Frontend must connect to the local backend via port 8000.

Google's Speech-to-Text API requires authentication (ensure credentials are set).

DistilGPT-2 runs locally (not deployed, may require GPU for faster inference).

Future Enhancements

Deploy DistilGPT-2 from hugging face as an API endpoint.

Improve pronunciation feedback.

Add progress tracking and historical reports.

Troubleshooting

Kill Running Uvicorn Server

tasklist | findstr "uvicorn"
taskkill /PID <PID> /F

Check API Logs

tail -f logs.txt

Contributing

Feel free to fork the repository and submit pull requests for improvements!

