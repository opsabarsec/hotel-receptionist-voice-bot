"""Hotel receptionist voice bot with transcript logging and translation.

This module implements a voice-activated hotel receptionist bot using OpenAI's
Realtime API. It logs conversations and optionally translates them to English
for staff review.
"""

from agents.realtime import RealtimeAgent, RealtimeRunner
from translator import TranslationService

from datetime import datetime
import json
import asyncio
from typing import Optional, Tuple, Dict, Any


class TranscriptLogger:
    """Logs conversation transcripts with optional translation support.

    This class manages conversation logging, including real-time translation
    to English when enabled. It supports multiple export formats: plain text,
    bilingual text, and JSON.

    Attributes:
        filename: Path to the main transcript file.
        base_filename: Filename without extension for generating related files.
        transcript: List of transcript entries with metadata.
        enable_translation: Whether translation is enabled.
        translator: TranslationService instance if translation is enabled.
    """

    def __init__(self, filename: Optional[str] = None, enable_translation: bool = True):
        """Initialize the transcript logger.

        Args:
            filename: Path to transcript file. If None, generates a timestamped
                filename automatically.
            enable_translation: Whether to enable automatic translation to English.
                Defaults to True.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hotel_conversation_{timestamp}.txt"
        self.filename = filename
        self.base_filename = filename.rsplit(".", 1)[0]
        self.transcript = []
        self.enable_translation = enable_translation
        self.translator = self._initialize_translator()

    def _initialize_translator(self) -> Optional[TranslationService]:
        """Initialize the translation service if enabled.

        Returns:
            TranslationService instance if successful, None otherwise.
        """
        if not self.enable_translation:
            return None

        try:
            translator = TranslationService()
            print("Translation service enabled")
            return translator
        except Exception as e:
            print(f"Warning: Could not initialize translation service: {e}")
            print("Continuing without translation...")
            self.enable_translation = False
            return None

    def add_entry(
        self, speaker: str, message: str, timestamp: Optional[datetime] = None
    ):
        """Add a conversation entry to the transcript.

        Creates a transcript entry with the message and optionally translates it
        if the speaker is USER or RECEPTIONIST and translation is enabled.

        Args:
            speaker: Speaker identifier (e.g., "USER", "RECEPTIONIST", "SYSTEM").
            message: The message text.
            timestamp: Message timestamp. If None, uses current time.
        """
        if timestamp is None:
            timestamp = datetime.now()

        entry = self._create_entry(speaker, message, timestamp)
        entry = self._add_translation_to_entry(entry, speaker, message)
        self.transcript.append(entry)
        self._write_entry_to_file(entry, timestamp)

    def _create_entry(
        self, speaker: str, message: str, timestamp: datetime
    ) -> Dict[str, Any]:
        """Create a basic transcript entry dictionary.

        Args:
            speaker: Speaker identifier.
            message: The message text.
            timestamp: Message timestamp.

        Returns:
            Dictionary with timestamp, speaker, and message.
        """
        return {
            "timestamp": timestamp.isoformat(),
            "speaker": speaker,
            "message": message,
        }

    def _add_translation_to_entry(
        self, entry: Dict[str, Any], speaker: str, message: str
    ) -> Dict[str, Any]:
        """Add translation data to a transcript entry if applicable.

        Args:
            entry: The transcript entry dictionary.
            speaker: Speaker identifier.
            message: The message text.

        Returns:
            Updated entry dictionary with translation data if applicable.
        """
        if not self.enable_translation or speaker not in ["USER", "RECEPTIONIST"]:
            return entry

        try:
            translation_result = self.translator.translate_to_english(message)
            entry["translated"] = translation_result["translated"]
            entry["source_language"] = translation_result["source_language"]
            entry["needs_translation"] = translation_result["needs_translation"]
        except Exception as e:
            print(f"Translation error for entry: {e}")
            entry["translated"] = message
            entry["source_language"] = "Unknown"
            entry["needs_translation"] = False

        return entry

    def _write_entry_to_file(self, entry: Dict[str, Any], timestamp: datetime):
        """Write a transcript entry to file immediately.

        Args:
            entry: The transcript entry dictionary.
            timestamp: Message timestamp for formatting.
        """
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(
                f"[{timestamp.strftime('%H:%M:%S')}] {entry['speaker']}: {entry['message']}\n"
            )

    def save_full_transcript(self) -> Tuple[str, Optional[str]]:
        """Save the complete transcript in text formats.

        Saves both the original transcript and a bilingual version if translation
        is enabled.

        Returns:
            Tuple of (original_file_path, bilingual_file_path). The bilingual
            path is None if translation is disabled.
        """
        original_file = self._save_original_transcript()
        bilingual_file = self._save_bilingual_transcript()
        return original_file, bilingual_file

    def _save_original_transcript(self) -> str:
        """Save the original transcript without translations.

        Returns:
            Path to the saved original transcript file.
        """
        with open(self.filename, "w", encoding="utf-8") as f:
            for entry in self.transcript:
                f.write(
                    f"[{entry['timestamp']}] {entry['speaker']}: {entry['message']}\n"
                )
        return self.filename

    def _save_bilingual_transcript(self) -> Optional[str]:
        """Save a bilingual transcript with original and English translation.

        Returns:
            Path to the bilingual transcript file, or None if translation is
            disabled.
        """
        if not self.enable_translation:
            return None

        bilingual_file = f"{self.base_filename}_bilingual.txt"
        with open(bilingual_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("BILINGUAL TRANSCRIPT - Original and English Translation\n")
            f.write("=" * 80 + "\n\n")

            for entry in self.transcript:
                formatted_entry = self._format_bilingual_entry(entry)
                f.write(formatted_entry)

        return bilingual_file

    def _format_bilingual_entry(self, entry: Dict[str, Any]) -> str:
        """Format a single entry for the bilingual transcript.

        Args:
            entry: The transcript entry dictionary.

        Returns:
            Formatted string for the bilingual transcript.
        """
        time_str = entry["timestamp"]
        speaker = entry["speaker"]
        message = entry["message"]

        formatted = f"[{time_str}] {speaker}:\n"
        formatted += f"  Original: {message}\n"

        # Add translation if available
        if "translated" in entry and entry.get("needs_translation", False):
            formatted += f"  English:  {entry['translated']}\n"
            formatted += f"  (Detected: {entry.get('source_language', 'Unknown')})\n"

        formatted += "\n"
        return formatted

    def save_json_transcript(self) -> str:
        """Save the complete transcript as JSON with all metadata.

        Returns:
            Path to the JSON transcript file.
        """
        json_file = f"{self.base_filename}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.transcript, f, indent=2, ensure_ascii=False)

        return json_file


async def bot() -> str:
    """Run the voice-activated hotel receptionist bot.

    Initializes the bot with OpenAI Realtime API, processes voice conversations,
    and logs transcripts with optional translation.

    Returns:
        The full conversation transcript as a formatted string.

    Raises:
        Exception: If there are errors during bot initialization or execution.
    """
    logger = TranscriptLogger()
    print(f"Transcript will be saved to: {logger.filename}")

    agent = _create_agent()
    runner = _create_runner(agent)
    session = await runner.run()

    try:
        await _handle_conversation_session(session, logger)
    except KeyboardInterrupt:
        print("\nSession interrupted by user")
        logger.add_entry("SYSTEM", "Session interrupted by user")
    except Exception as e:
        print(f"Session error: {e}")
        logger.add_entry("SYSTEM", f"Session error: {e}")
    finally:
        logger.add_entry("SYSTEM", "Session ended")
        _save_transcripts(logger)

    return _format_transcript_string(logger.transcript)


def _create_agent() -> RealtimeAgent:
    """Create and configure the RealtimeAgent.

    Returns:
        Configured RealtimeAgent instance for hotel reception.
    """
    return RealtimeAgent(
        name="Hotel Receptionist",
        instructions=(
            "You are a friendly hotel receptionist. "
            "Your job is to collect from the guest: name, check-in and check-out dates, "
            "preferred room type, number of guests, and any special requests. "
            "Confirm the reservation details succinctly.\n"
            "You also have access to Supabase and WhatsApp tools via MCP for handling data and sending confirmations."
        ),
        mcp_servers=["supabase", "whatsapp"],
    )


def _create_runner(agent: RealtimeAgent) -> RealtimeRunner:
    """Create and configure the RealtimeRunner.

    Args:
        agent: The RealtimeAgent to use for the session.

    Returns:
        Configured RealtimeRunner instance.
    """
    return RealtimeRunner(
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


async def _handle_conversation_session(session, logger: TranscriptLogger):
    """Handle the conversation session and log events.

    Args:
        session: The RealtimeRunner session.
        logger: TranscriptLogger instance for logging conversation.
    """
    async with session:
        print("Hotel receptionist agent ready for voice input.")
        logger.add_entry("SYSTEM", "Hotel receptionist agent started")

        async for event in session:
            _process_conversation_event(event, logger)


def _process_conversation_event(event, logger: TranscriptLogger):
    """Process a single conversation event and log it.

    Args:
        event: The conversation event from the RealtimeRunner.
        logger: TranscriptLogger instance for logging.
    """
    if event.type == "conversation.item.input_audio_transcription.completed":
        user_message = event.transcript
        print(f"User: {user_message}")
        logger.add_entry("USER", user_message)

    elif event.type == "response.audio_transcript.done":
        agent_message = event.transcript
        print(f"Receptionist: {agent_message}")
        logger.add_entry("RECEPTIONIST", agent_message)


def _save_transcripts(logger: TranscriptLogger):
    """Save all transcript formats and print file paths.

    Args:
        logger: TranscriptLogger instance with conversation data.
    """
    original_file, bilingual_file = logger.save_full_transcript()
    json_file = logger.save_json_transcript()

    print(f"\nTranscripts saved:")
    print(f"  - Original: {original_file}")
    if bilingual_file:
        print(f"  - Bilingual: {bilingual_file}")
    print(f"  - JSON: {json_file}")


def _format_transcript_string(transcript: list[Dict[str, Any]]) -> str:
    """Format transcript entries as a single string.

    Args:
        transcript: List of transcript entry dictionaries.

    Returns:
        Formatted transcript string with timestamps and speakers.
    """
    return "\n".join(
        f"[{entry['timestamp']}] {entry['speaker']}: {entry['message']}"
        for entry in transcript
    )


async def main():
    """Main entry point for running the hotel receptionist bot.

    Runs the bot and processes the conversation. Can be extended to handle
    existing transcript files.
    """
    await bot()


if __name__ == "__main__":
    asyncio.run(main())
