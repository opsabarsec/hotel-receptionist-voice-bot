# Hotel Receptionist Voice Bot - Technical Documentation

## Overview

This documentation provides comprehensive technical details for implementing and deploying the Hotel Receptionist Voice Bot, an AI-powered solution that leverages OpenAI's Realtime API to provide multilingual customer service for hotel operations.

## Architecture

### System Components

1. **Voice Interface Layer**
   - Audio input/output handling
   - Real-time audio streaming
   - WebSocket connections for bidirectional communication

2. **AI Processing Engine**
   - OpenAI Realtime API integration
   - Natural Language Understanding (NLU)
   - Multilingual conversation handling
   - Context management

3. **Hotel Integration Layer**
   - Property Management System (PMS) integration
   - Room availability checking
   - Booking system interface
   - Guest services coordination

4. **Data Layer**
   - Guest information database
   - Hotel services knowledge base
   - Conversation logs and analytics

### Technical Stack

- **Backend**: Python 3.8+
- **AI Service**: OpenAI Realtime API
- **Communication**: WebSocket (Real-time)
- **Audio Processing**: WebRTC
- **Database**: PostgreSQL/MongoDB
- **Deployment**: Docker containers
- **Monitoring**: Prometheus + Grafana

## Implementation Guide

### Prerequisites

- Python 3.8 or higher
- OpenAI API key with Realtime API access
- Audio input/output capabilities
- WebSocket support
- SSL certificate for production

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/opsabarsec/hotel-receptionist-voice-bot.git
cd hotel-receptionist-voice-bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Environment configuration:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export HOTEL_DB_URL="your-database-url"
export AUDIO_SAMPLE_RATE=16000
```

### Configuration

#### Audio Settings
```python
AUDIO_CONFIG = {
    'sample_rate': 16000,
    'channels': 1,
    'format': 'PCM',
    'chunk_size': 1024
}
```

#### Language Support
```python
SUPPORTED_LANGUAGES = [
    'en-US',  # English (US)
    'es-ES',  # Spanish
    'fr-FR',  # French
    'de-DE',  # German
    'it-IT',  # Italian
    'pt-BR',  # Portuguese (Brazil)
    'zh-CN',  # Chinese (Simplified)
    'ja-JP',  # Japanese
    'ko-KR',  # Korean
    'ar-SA'   # Arabic
]
```

## API Reference

### Core Functions

#### `initialize_bot()`
Initializes the voice bot with required configurations.

**Returns**: `VoiceBot` instance

#### `handle_voice_input(audio_data)`
Processes incoming voice data through OpenAI Realtime API.

**Parameters**:
- `audio_data` (bytes): Raw audio data

**Returns**: `BotResponse` object

#### `generate_response(text, language, context)`
Generates appropriate response based on hotel context.

**Parameters**:
- `text` (str): Processed speech-to-text
- `language` (str): Detected language code
- `context` (dict): Conversation context

**Returns**: Response text and audio

### Hotel Service Handlers

#### Room Booking
```python
class RoomBookingHandler:
    def check_availability(self, check_in, check_out, guests):
        """Check room availability for given dates"""
        pass
    
    def make_reservation(self, guest_info, room_type, dates):
        """Create new room reservation"""
        pass
```

#### Guest Services
```python
class GuestServicesHandler:
    def handle_concierge_request(self, request_type, details):
        """Handle concierge service requests"""
        pass
    
    def room_service_order(self, room_number, items):
        """Process room service orders"""
        pass
```

## Multilingual Prompt Templates

### English Template
```python
ENGLISH_PROMPTS = {
    "greeting": "Hello! Welcome to our hotel. How may I assist you today?",
    "booking_inquiry": "I'd be happy to help you with your reservation. What dates are you looking for?",
    "room_service": "I can help you with room service. What would you like to order?",
    "checkout": "I can assist with your checkout. May I have your room number?"
}
```

### Spanish Template
```python
SPANISH_PROMPTS = {
    "greeting": "¡Hola! Bienvenido a nuestro hotel. ¿Cómo puedo ayudarle hoy?",
    "booking_inquiry": "Me complace ayudarle con su reserva. ¿Qué fechas está buscando?",
    "room_service": "Puedo ayudarle con el servicio a la habitación. ¿Qué le gustaría ordenar?",
    "checkout": "Puedo ayudarle con su salida. ¿Me puede dar su número de habitación?"
}
```

### French Template
```python
FRENCH_PROMPTS = {
    "greeting": "Bonjour ! Bienvenue dans notre hôtel. Comment puis-je vous aider aujourd'hui ?",
    "booking_inquiry": "Je serais ravi de vous aider avec votre réservation. Quelles dates recherchez-vous ?",
    "room_service": "Je peux vous aider avec le service en chambre. Que souhaiteriez-vous commander ?",
    "checkout": "Je peux vous aider avec votre départ. Puis-je avoir votre numéro de chambre ?"
}
```

## Deployment

### Docker Configuration

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "bot_main.py"]
```

### Production Deployment

1. **Load Balancing**: Use NGINX for load balancing multiple bot instances
2. **SSL/TLS**: Enable HTTPS for secure audio transmission
3. **Monitoring**: Implement health checks and performance monitoring
4. **Scaling**: Use Kubernetes for horizontal scaling

### Performance Monitoring

#### Key Metrics
- Response latency (target: < 2 seconds)
- Audio quality (signal-to-noise ratio)
- Language detection accuracy
- Conversation completion rate
- Error rate (target: < 2%)

#### Monitoring Setup
```python
import prometheus_client

# Response time tracking
response_time = prometheus_client.Histogram(
    'bot_response_seconds',
    'Time spent processing requests'
)

# Language detection accuracy
language_accuracy = prometheus_client.Counter(
    'language_detection_accuracy',
    'Successful language detections'
)
```

## Security Considerations

### Data Protection
- Encrypt all audio data in transit and at rest
- Implement proper authentication for API access
- Regular security audits and updates
- GDPR compliance for guest data handling

### Access Control
```python
class SecurityManager:
    def authenticate_request(self, api_key):
        """Validate API key and permissions"""
        pass
    
    def encrypt_audio_data(self, audio_bytes):
        """Encrypt audio data for secure transmission"""
        pass
```

## Testing

### Unit Tests
```bash
python -m pytest tests/unit/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Load Testing
```bash
python -m pytest tests/load/ --concurrent-users=100
```

## Troubleshooting

### Common Issues

1. **Audio Quality Problems**
   - Check microphone settings
   - Verify sample rate configuration
   - Ensure proper codec settings

2. **API Connection Issues**
   - Validate OpenAI API key
   - Check network connectivity
   - Verify WebSocket connection

3. **Language Detection Errors**
   - Review audio quality
   - Check supported language list
   - Validate input format

### Debug Mode
```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
python bot_main.py
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For technical support or questions, please open an issue on GitHub or contact the development team.
