from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import pyaudio
import threading
import requests
import json
import time
import os
from collections import deque
from datetime import datetime


"""
Application Initialization
"""

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# API keys
DEEPGRAM_API_KEY=''
OPENAI_API_KEY=''
# Audio recording parameters
CHUNK = 8000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


# Global variables and state management
class AudioState:
    def __init__(self):
        self.is_recording = False
        self.last_openai_query_time = time.time()
        self.stream = None
        self.p = None
        self.dg_connection = None
        self.transcript_buffer = deque(maxlen=5)
        self.topic_buffer = deque(maxlen=5)
        self.action_buffer = deque(maxlen=5)
        self.deepgram_client = None
        self.lock = threading.Lock()
        self.assessment_criteria = []
        self.assessment_results = {}


audio_state = AudioState()

"""
Application Routes
"""


@app.route("/")
def index():
    return render_template("index.html")


# Add scoring criteria endpoint
@app.route("/api/criteria", methods=["POST"])
def add_criteria():
    try:
        data = request.get_json()
        print("Received criteria data:", data)  # Debug log
        criterion = {
            "id": len(audio_state.assessment_criteria),
            "question": data["question"],
            "phrases": data["phrases"],
        }
        audio_state.assessment_criteria.append(criterion)
        audio_state.assessment_results[criterion["id"]] = 0
        print("Added criterion:", criterion)  # Debug log
        return jsonify(criterion)
    except Exception as e:
        print("Error adding criteria:", str(e))  # Debug log
        return jsonify({"error": str(e)}), 400


# Get criteria endpoint
@app.route("/api/criteria", methods=["GET"])
def get_criteria():
    return jsonify(audio_state.assessment_criteria)


# Clear criteria endpoint
@app.route("/api/criteria/clear", methods=["POST"])
def clear_criteria():
    audio_state.assessment_criteria.clear()
    audio_state.assessment_results.clear()
    return jsonify({"status": "success"})


"""
Application Helper Functions
"""


def check_phrases_in_transcript(transcript, phrases):
    transcript_lower = transcript.lower()
    return any(phrase.lower() in transcript_lower for phrase in phrases)


def get_llm_response(query, question):
    try:
        endpoint = "https://analyticsrg.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview"
        headers = {
            "Content-Type": "application/json",
            "api-key": OPENAI_API_KEY,
        }
        data = {
            "messages": [
                {"role": "system", "content": query},
                {"role": "user", "content": question},
            ],
            "max_tokens": 400,
        }
        response = requests.post(endpoint, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        print(f"Error in get_llm_response: {e}")
        return "Error processing request"


# Main function to obtain transcriptions & analysis
def initialize_deepgram():
    try:
        audio_state.deepgram_client = DeepgramClient(DEEPGRAM_API_KEY)
        audio_state.dg_connection = audio_state.deepgram_client.listen.live.v("1")

        def on_message(self, result, **kwargs):
            
            # No recording event started
            with audio_state.lock:
                if not audio_state.is_recording:
                    return

                sentence = result.channel.alternatives[0].transcript
                if len(sentence.strip()) == 0:
                    return

                # Store transcript and emit to frontend
                audio_state.transcript_buffer.append(sentence)
                socketio.emit("new_transcript", {"text": sentence})

                # Check assessment criteria
                for criterion in audio_state.assessment_criteria:
                    if check_phrases_in_transcript(sentence, criterion["phrases"]):
                        audio_state.assessment_results[criterion["id"]] += 1
                        socketio.emit(
                            "criteria_update",
                            {
                                "id": criterion["id"],
                                "count": audio_state.assessment_results[
                                    criterion["id"]
                                ],
                            },
                        )

                current_time = time.time()

                # Only query OpenAI every 15 seconds
                if current_time - audio_state.last_openai_query_time >= 15:
                    try:
                        # Get sentiment
                        combined_text = " ".join(list(audio_state.transcript_buffer))
                        sentiment_query = "Analyze the following text and respond with exactly one word for the sentiment: Positive, Negative, or Neutral: "
                        sentiment = get_llm_response(sentiment_query, combined_text)
                        socketio.emit(
                            "sentiment_update", {"sentiment": sentiment.strip()}
                        )

                        # Get topic
                        topic_query = "What is the main topic being discussed? Respond in 3-4 words maximum:"
                        topic = get_llm_response(topic_query, combined_text)
                        audio_state.topic_buffer.append(topic)
                        socketio.emit(
                            "topic_update", {"topics": list(audio_state.topic_buffer)}
                        )

                        # Get action points
                        action_query = "Based on this conversation, what is one clear action item? Respond in 5 words maximum:"
                        action = get_llm_response(action_query, combined_text)
                        audio_state.action_buffer.append(action)
                        socketio.emit(
                            "action_update",
                            {"actions": list(audio_state.action_buffer)},
                        )

                        audio_state.last_openai_query_time = current_time
                    except Exception as e:
                        print(f"Error processing OpenAI queries: {e}")

        def on_error(self, error):
            print(f"Deepgram connection error: {error}")
            socketio.emit("error", {"message": "Audio processing error occurred"})

        # When message returned, call on message function
        audio_state.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        # When error is returned, call on error function
        audio_state.dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            smart_format=True,
            model="nova-2",
            language="en-GB",
            encoding="linear16",
            sample_rate=RATE,
        )

        # Start connection to DG -> continuously while true
        audio_state.dg_connection.start(options)
        return True
    except Exception as e:
        print(f"Error initializing Deepgram: {e}")
        return False


# Start audio stream from microphone
def start_audio_stream():
    try:
        audio_state.p = pyaudio.PyAudio()
        audio_state.stream = audio_state.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        return True
    except Exception as e:
        print(f"Error starting audio stream: {e}")
        return False


# Send audio from stream to Deepgram
def audio_processing_thread():
    while True:
        with audio_state.lock:
            if audio_state.is_recording and audio_state.stream:
                try:
                    data = audio_state.stream.read(CHUNK, exception_on_overflow=False)
                    if audio_state.dg_connection:
                        audio_state.dg_connection.send(data)
                except Exception as e:
                    print(f"Error in audio processing: {e}")
                    socketio.emit(
                        "error", {"message": "Audio processing error occurred"}
                    )
        time.sleep(0.001)


# Start Recording button click event
@socketio.on("start_recording")
def handle_start_recording():
    with audio_state.lock:
        if not audio_state.is_recording:
            if initialize_deepgram() and start_audio_stream():
                
                # Set thread lock when recording initiated
                audio_state.is_recording = True
                emit("recording_status", {"status": "active"})
            else:
                emit("error", {"message": "Failed to start recording"})


# Stop Recording button click event
@socketio.on("stop_recording")
def handle_stop_recording():
    with audio_state.lock:
        audio_state.is_recording = False
        if audio_state.stream:
            audio_state.stream.stop_stream()
            audio_state.stream.close()
        if audio_state.p:
            audio_state.p.terminate()
        if audio_state.dg_connection:
            audio_state.dg_connection.finish()
        audio_state.stream = None
        audio_state.p = None
        audio_state.dg_connection = None
        emit("recording_status", {"status": "inactive"})


# Clear Results button click events
@socketio.on("clear_results")
def handle_clear_results():
    with audio_state.lock:
        audio_state.transcript_buffer.clear()
        audio_state.topic_buffer.clear()
        audio_state.action_buffer.clear()
        audio_state.assessment_criteria.clear()
        audio_state.assessment_results.clear()
        emit("clear_all")


# Indicates service is connected to backend app
@socketio.on("connect")
def handle_connect():
    print("Client connected")


# When disconnect, stop recording
@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")
    handle_stop_recording()


if __name__ == "__main__":
    audio_thread = threading.Thread(target=audio_processing_thread)
    audio_thread.daemon = True
    audio_thread.start()
    socketio.run(app, debug=True)
