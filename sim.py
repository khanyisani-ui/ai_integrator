import os
import time
import pyaudio
import wave
import language_tool_python
from google.cloud import speech
from transformers import pipeline
from fpdf import FPDF
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from fastapi import UploadFile, File

# Load environment variables
load_dotenv()

# Set up Google Speech-to-Text
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv("GOOGLE_CREDENTIALS_PATH")
client = speech.SpeechClient()

speech_config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code="en-US",
)

# Set up Hugging Face API Key
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
gpt_model = pipeline("text-generation", model="distilgpt2")

grammar_tool = language_tool_python.LanguageTool('en-US')

app = FastAPI()  # FastAPI instance

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://glowing-halibut-r6rxvvr4gw4fppq-3000.app.github.dev"],  # Modify as needed for your production app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AudioInput(BaseModel):
    user_input: str

# Function to list audio devices
def list_audio_devices():
    audio = pyaudio.PyAudio()
    devices = []
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            devices.append(device_info)
    audio.terminate()
    return devices

# Function to record audio
def record_audio():
    devices = list_audio_devices()
    if not devices:
        raise HTTPException(status_code=404, detail="No audio input devices found!")

    input_device_index = devices[0]['index']
    
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, input_device_index=input_device_index, frames_per_buffer=1024)
    frames = []

    print("Recording... Speak now!")
    for _ in range(0, int(16000 / 1024 * 5)):
        data = stream.read(1024)
        frames.append(data)

    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open("audio.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))

# Function to transcribe audio
def transcribe_audio():
    with open("audio.wav", "rb") as audio_file:
        audio_content = audio_file.read()

    audio = speech.RecognitionAudio(content=audio_content)
    response = client.recognize(config=speech_config, audio=audio)

    if response.results:
        return response.results[0].alternatives[0].transcript
    else:
        return "Sorry, I didn't catch that."

# Function to generate response using GPT
def generate_response(user_input):
    response = gpt_model(user_input, max_length=100, truncation=True)
    return response[0]['generated_text']

# Function to assess fluency and coherence
def assess_fluency_and_coherence(transcription):
    words = transcription.split()
    pauses = transcription.count('...')
    total_words = len(words)
    
    fluency_score = max(10 - pauses, 1)
    coherence_score = 10 if total_words > 20 else 5
    
    return fluency_score, coherence_score

# Function to assess pronunciation (based on confidence)
def assess_pronunciation(transcription):
    confidence_score = get_transcription_confidence(transcription)
    return "Pronunciation seems fine." if confidence_score > 0.85 else "Pronunciation might need improvement."

def get_transcription_confidence(transcription):
    return 0.9  # Simulated confidence score

# Function to assess lexical resource
def assess_lexical_resource(transcription):
    words = transcription.split()
    unique_words = set(words)
    lexical_score = min(len(unique_words), 10)
    
    vocabulary_suggestions = []
    if len(unique_words) < 5:
        vocabulary_suggestions.append("Try using more complex words.")
    
    return lexical_score, vocabulary_suggestions

# Function to calculate overall IELTS score
def calculate_ielts_score(fluency_score, coherence_score, lexical_score, grammatical_score):
    total_score = (fluency_score + coherence_score + lexical_score + grammatical_score) / 4
    return round(total_score, 2)

# Function to run conversation (real-time simulation)
async def start_conversation():
    conversation_in_progress = True
    while conversation_in_progress:
        await record_audio()
        transcription = transcribe_audio()
        
        if transcription.lower() == 'exit':
            conversation_in_progress = False
            continue
        
        response = generate_response(transcription)
        
        fluency_score, coherence_score = assess_fluency_and_coherence(transcription)
        lexical_score, vocabulary_suggestions = assess_lexical_resource(transcription)
        pronunciation_feedback = assess_pronunciation(transcription)
        
        feedback = {
            "Fluency & Coherence": fluency_score,
            "Lexical Resource": lexical_score,
            "Pronunciation Feedback": pronunciation_feedback,
        }

        print("AI Response:", response)
        print("Feedback:", feedback)
        print("Vocabulary Suggestions:", vocabulary_suggestions)
        
        await asyncio.sleep(1)

# Function to run practice mode
def run_practice_mode():
    print("Practice Mode: Immediate feedback will be provided.")
    asyncio.run(start_conversation())

# Function to run test mode
def run_test_mode():
    print("Test Mode: Full test with 3 parts.")
    
    print("Part 1: Introduction")
    asyncio.run(start_conversation())
    
    print("Part 2: Long Turn (Cue Card)")
    print("Describe a memorable event in your life.")
    
    print("Part 3: Discussion")
    asyncio.run(start_conversation())
    
    feedback = {"Test Completed": "Final Feedback"}
    print("Final Feedback:", feedback)

# Endpoint to handle audio recording
@app.post("/record_audio/")
async def record_audio_endpoint():
    record_audio()
    return {"message": "Recording completed."}

# Endpoint to handle transcription
@app.post("/transcribe_audio/")
async def transcribe_audio_endpoint():
    """Endpoint to transcribe the recorded audio automatically."""
    # Check if audio file exists
    if not os.path.exists("audio.wav"):
        raise HTTPException(status_code=404, detail="No audio file found. Please record the audio first.")

    # Call the transcription function
    transcription = transcribe_audio()
    return {"transcription": transcription}

# Endpoint to handle GPT response generation
@app.post("/generate_response/")
async def generate_response_endpoint(input_data: AudioInput):
    response = generate_response(input_data.user_input)
    return {"response": response}

# Endpoint to handle feedback generation
@app.post("/generate_feedback/")
async def generate_feedback_endpoint(input_data: AudioInput):
    fluency_score, coherence_score = assess_fluency_and_coherence(input_data.user_input)
    lexical_score, vocabulary_suggestions = assess_lexical_resource(input_data.user_input)
    pronunciation_feedback = assess_pronunciation(input_data.user_input)
    
    feedback = {
        "Fluency & Coherence": fluency_score,
        "Lexical Resource": lexical_score,
        "Pronunciation Feedback": pronunciation_feedback,
    }
    return {"feedback": feedback}

# Endpoint to generate PDF report
@app.post("/generate_pdf_report/")
async def generate_pdf_report_endpoint(feedback: dict, filename: str = "IELTS_Report.pdf"):
    generate_pdf_report(feedback, filename)
    return {"message": "PDF report generated successfully."}

# Function to generate PDF report
def generate_pdf_report(feedback, filename="IELTS_Report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="IELTS Speaking Test Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)

    for key, value in feedback.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)

    pdf.output(filename)

# Main function
if __name__ == "__main__":
    mode = input("Enter mode (practice/test): ").strip().lower()
    if mode == "practice":
        run_practice_mode()
    elif mode == "test":
        run_test_mode()
    else:
        print("Invalid mode selected.")
