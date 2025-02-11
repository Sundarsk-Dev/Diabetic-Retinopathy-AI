import os
import google.generativeai as genai
from dotenv import load_dotenv
import pyttsx3
import speech_recognition as sr
import time

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("API key not found! Please check your .env file.")

# Configure the Gemini API
genai.configure(api_key=API_KEY)

# Model Configuration
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1024,
    "response_mime_type": "text/plain",
}

# System Instruction
system_instruction = """
You are a compassionate and knowledgeable virtual health companion designed to support older adults, especially those suffering from Alzheimer's, dementia, loneliness, and age-related mental health challenges.

## Key Responsibilities:
- Provide *emotional support, **cognitive exercises, and **daily reminders*.
- Engage users in *gentle, friendly conversations* to reduce loneliness.
- Offer *calming techniques* and *mental stimulation* for users experiencing memory loss.
- Guide users on *healthy habits, **sleep routines, and **stress management*.
- Ask *a maximum of 3 questions* per response to keep the conversation simple and engaging.
- *DO NOT* provide medical diagnoses or complex medical advice.
- If a symptom is reported, ask *3-4 relevant questions* before suggesting the next step.
- *If a critical emergency is detected, print 'TRIGGER' to notify a guardian.*
"""

# Initialize the Model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-thinking-exp-01-21",  # Or your preferred model
    generation_config=generation_config,
    system_instruction=system_instruction,
)

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Initialize Speech-to-Text recognizer
r = sr.Recognizer()

# Function to speak the chatbot's response
def speak_response(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen for user input with timeout
def listen_for_input():
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source) # Adjust for ambient noise
        try:
            audio = r.listen(source, phrase_time_limit=10, timeout=5)  
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None
        except Exception as e: # Catch other potential errors
            print(f"An unexpected error occurred: {e}")
            return None

        try:
            user_input = r.recognize_google(audio)
            print(f"You: {user_input}")
            return user_input
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None


# Function to Start or Continue a Chat Session
def get_chat_response(user_input, chat_session):
    response = chat_session.send_message(user_input)

    # Detect potential emergencies (same as before)
    emergency_keywords = ["suicidal", "harm myself", "feel hopeless", "severe pain", "chest pain"]
    if any(word in user_input.lower() for word in emergency_keywords):
        print("TRIGGER")
        return "I'm really concerned about your safety. Please reach out to a loved one or a healthcare provider immediately. You're not alone."

    return response.text

# Start Chat Session
chat_session = model.start_chat(history=[])

# Example Interaction (Voice-only)
while True:
    user_input = listen_for_input()

    if user_input is None:  # Handle timeouts or recognition failures
        continue  # Go back to listening

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Chatbot: Take care! I'm always here if you need me. 😊")
        speak_response("Take care! I'm always here if you need me. 😊")
        break

    chatbot_response = get_chat_response(user_input, chat_session)
    print(f"Chatbot: {chatbot_response}")
    speak_response(chatbot_response)

