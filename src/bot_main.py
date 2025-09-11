from agents.realtime import RealtimeAgent, RealtimeRunner

from datetime import datetime

import asyncio


class TranscriptLogger:
    """Logs the conversation transcript to a text file"""

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
        """Save the complete transcript as text"""
        with open(self.filename, "w", encoding="utf-8") as f:
            for entry in self.transcript:
                f.write(
                    f"[{entry['timestamp']}] {entry['speaker']}: {entry['message']}\n"
                )

        return self.filename


async def bot() -> str:
    """Voice-activated hotel receptionist bot using RealtimeAgent and RealtimeRunner.
    The conversation is returned as text and logged into a file.

    Returns:
        str: The full conversation transcript as a string.
    """

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

    except KeyboardInterrupt:
        print("\nSession interrupted by user")
        logger.add_entry("SYSTEM", "Session interrupted by user")
    except Exception as e:
        print(f"Session error: {e}")
        logger.add_entry("SYSTEM", f"Session error: {e}")
    finally:
        # Save final transcript
        logger.add_entry("SYSTEM", "Session ended")
        text_file = logger.save_full_transcript()
        print(f"Full transcript saved to: {text_file}")

    # Return the transcript as a string variable
    transcript_str = "\n".join(
        f"[{entry['timestamp']}] {entry['speaker']}: {entry['message']}"
        for entry in logger.transcript
    )
    return transcript_str


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
