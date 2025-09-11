from agents.realtime import RealtimeAgent, RealtimeRunner

from pydantic import BaseModel, Field
from datetime import datetime
import json
import asyncio
import os


# Define the Pydantic model for hotel requests
class HotelRequest(BaseModel):
    Available: bool = Field(
        ..., description="True if room is available, False otherwise"
    )
    CheckInDate: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    CheckoutDate: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    NumberOfGuests: int = Field(..., description="Number of guests for the reservation")
    guest_name: str = Field(..., description="Name of the guest")
    room_type: str = Field(..., description="Requested room type")
    special_requests: str = Field("", description="Any special requests")


def save_request_to_json(request: HotelRequest, filename: str = "hotel_requests.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    data.append(request.model_dump())
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


class TranscriptLogger:
    def __init__(self, filename: str = None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hotel_conversation_{timestamp}.txt"
        self.filename = filename
        self.transcript = []

    def add_entry(self, speaker: str, message: str, timestamp: datetime = None):
        if timestamp is None:
            timestamp = datetime.now()

        entry = {
            "timestamp": timestamp.isoformat(),
            "speaker": speaker,
            "message": message,
        }
        self.transcript.append(entry)

        # Also write immediately to file
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp.strftime('%H:%M:%S')}] {speaker}: {message}\n")

    def save_full_transcript(self):
        """Save the complete transcript as JSON"""
        json_filename = self.filename.replace(".txt", ".json")
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(self.transcript, f, indent=2, ensure_ascii=False)
        return json_filename


async def bot():
    # Initialize transcript logger
    logger = TranscriptLogger()
    print(f"Transcript will be saved to: {logger.filename}")

    # ---- INTEGRATE MCP (Supabase, WhatsApp) ----
    agent = RealtimeAgent(
        name="Hotel Receptionist",
        instructions=(
            "You are a friendly hotel receptionist. "
            "Your job is to collect from the guest: name, check-in and check-out dates, "
            "preferred room type, number of guests, and any special requests. "
            "Confirm the reservation details succinctly.\n"
            "You also have access to Supabase and WhatsApp tools via MCP for handling data and sending confirmations."
        ),
        # <<<< ADD THIS: list MCP servers here! >>>>
        mcp_servers=["supabase", "whatsapp"],
    )
    # --------------------------------------------

    runner = RealtimeRunner(
        starting_agent=agent,
        config={
            "model_settings": {
                "model_name": "gpt-realtime",
                "voice": "alloy",
                "modalities": ["text", "audio"],
                "input_audio_transcription": {"model": "whisper-1"},
            },
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 200,
            },
        },
    )

    # Start the voice session
    session = await runner.run()

    try:
        async with session:
            print("Hotel receptionist agent ready for voice input.")
            logger.add_entry("SYSTEM", "Hotel receptionist agent started")

            reservation = {}

            async for event in session:
                # Log different types of events
                if (
                    event.type
                    == "conversation.item.input_audio_transcription.completed"
                ):
                    user_message = event.transcript
                    print(f"User: {user_message}")
                    logger.add_entry("USER", user_message)

                elif event.type == "response.audio_transcript.done":
                    agent_message = event.transcript
                    print(f"Receptionist: {agent_message}")
                    logger.add_entry("RECEPTIONIST", agent_message)

                elif event.type == "response.audio_transcript.delta":
                    # Optional: log partial responses as they come in
                    # print(f"Receptionist (partial): {event.delta}")
                    pass

                elif event.type == "conversation.item.input_audio_transcription.failed":
                    error_msg = f"Transcription failed: {getattr(event, 'error', 'Unknown error')}"
                    print(error_msg)
                    logger.add_entry("SYSTEM", error_msg)

                elif event.type == "error":
                    error_msg = (
                        f"Session error: {getattr(event, 'error', 'Unknown error')}"
                    )
                    print(error_msg)
                    logger.add_entry("SYSTEM", error_msg)

                # You can add more event types as needed
                # Common event types include:
                # - session.created, session.updated
                # - conversation.item.created
                # - response.created, response.done
                # - rate_limits.updated

    except KeyboardInterrupt:
        print("\nSession interrupted by user")
        logger.add_entry("SYSTEM", "Session interrupted by user")
    except Exception as e:
        print(f"Session error: {e}")
        logger.add_entry("SYSTEM", f"Session error: {e}")
    finally:
        # Save final transcript
        logger.add_entry("SYSTEM", "Session ended")
        json_file = logger.save_full_transcript()
        print(f"Full transcript saved to: {logger.filename}")
        print(f"JSON transcript saved to: {json_file}")


async def get_existing_transcript(filename: str):
    """Helper function to read and display an existing transcript"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Transcript file {filename} not found"


# Example usage to retrieve transcript
async def main():
    # Run the bot
    await bot()

    # Or if you want to read an existing transcript:
    # transcript_content = await get_existing_transcript("hotel_conversation_20241201_143022.txt")
    # print("Existing transcript:")
    # print(transcript_content)


if __name__ == "__main__":
    asyncio.run(main())
