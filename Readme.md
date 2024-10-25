# Real-Time Audio Analysis Application

A sophisticated web application that provides real-time audio transcription, sentiment analysis, topic detection, and conversation assessment capabilities using Flask, Socket.IO, Deepgram, and OpenAI APIs.

## 🌟 Features

### Core Functionality
- **Live Audio Transcription**: Real-time speech-to-text conversion using Deepgram's Nova-2 model
- **Sentiment Analysis**: Continuous emotion detection in the conversation
- **Topic Detection**: Automatic identification of conversation topics
- **Action Item Extraction**: Real-time generation of action points from the conversation
- **Custom Assessment Criteria**: Define and track specific phrases or requirements in conversations

### Analytics Dashboard
- **Audio Level Monitoring**: Visual representation of audio input levels
- **Word Count Tracking**: Real-time word count statistics
- **Speaking Rate Analysis**: Words per minute (WPM) calculation
- **Topic Timeline**: Historical view of conversation topics
- **Word Cloud**: Frequently used words visualization

### Assessment Tools
- **Custom Criteria Creation**: Add specific phrases to track during conversations
- **Phrase Detection**: Real-time counting of specified phrases
- **Assessment Results**: Live updates of criteria matches
- **Results Export**: Export conversation data and assessment results to JSON

## 🛠 Technical Stack

### Backend
- **Flask**: Web application framework
- **Flask-SocketIO**: Real-time bidirectional communication
- **Deepgram SDK**: Speech-to-text conversion
- **PyAudio**: Audio input handling
- **OpenAI API**: Natural language processing for analytics

### Frontend
- **Socket.IO**: Real-time client-server communication
- **Vanilla JavaScript**: Client-side functionality
- **Custom CSS**: Responsive and modern UI design

## 📋 Prerequisites

Before running the application, ensure you have:

1. Python 3.7 or higher installed
2. Node.js and npm (for Socket.IO client)
3. A Deepgram API key
4. An OpenAI API key
5. PyAudio and its dependencies

## ⚙️ Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install Python dependencies:
```bash
pip install flask flask-socketio deepgram-sdk pyaudio requests
```

3. Set up environment variables:
```bash
export DEEPGRAM_API_KEY='your-deepgram-api-key'
export OPENAI_API_KEY='your-openai-api-key'
```

## 🚀 Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Access the application:
- Open your browser and navigate to `http://localhost:5000`
- Allow microphone access when prompted

## 💡 Usage Guide

### Recording Controls
1. Click "Start Recording" to begin audio capture
2. The status indicator will show "Recording Active"
3. Audio levels will be displayed in real-time
4. Click "Stop Recording" to end the session

### Assessment Criteria
1. Add new criteria:
   - Enter a question (e.g., "Did the agent give a proper greeting?")
   - Enter comma-separated phrases to track (e.g., "hello, good morning, welcome")
   - Click "Add Criterion"
2. Monitor criteria matches in real-time
3. Clear all criteria using the "Clear Results" button

### Analysis Features
- **Transcript**: View real-time transcription in the main panel
- **Sentiment**: Monitor conversation tone through emoji indicators
- **Topics**: Track conversation topics in the side panel
- **Action Items**: View automatically generated action points
- **Word Cloud**: See frequently used words

### Exporting Data
1. Click the "Export Session" button
2. A JSON file will be downloaded containing:
   - Word count statistics
   - Speaking rate data
   - Topics and action items
   - Complete transcript
   - Assessment criteria results

## 🔧 Configuration

### Audio Settings
```python
CHUNK = 8000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
```

### Deepgram Settings
```python
options = LiveOptions(
    smart_format=True,
    model="nova-2",
    language="en-GB",
    encoding="linear16",
    sample_rate=RATE
)
```

## 🔒 Security Considerations

1. API Keys:
   - Store API keys in environment variables
   - Never commit API keys to version control
   - Use appropriate key rotation practices

2. Audio Data:
   - Audio is processed in real-time and not stored
   - Only transcribed text is retained in memory
   - Clear data using the "Clear Results" button

## 🐛 Troubleshooting

### Common Issues

1. **Microphone Access**
   - Ensure browser has microphone permissions
   - Check system microphone settings
   - Verify default input device

2. **Connection Issues**
   - Check internet connectivity
   - Verify WebSocket connection
   - Ensure server is running

3. **API Errors**
   - Verify API keys are set correctly
   - Check API quotas and limits
   - Monitor server logs for errors

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For support, please:
1. Check the troubleshooting guide
2. Review server logs
3. Submit an issue on GitHub
4. Contact the development team

## 🙏 Acknowledgments

- Deepgram for speech-to-text capabilities
- OpenAI for natural language processing
- Flask and Socket.IO communities