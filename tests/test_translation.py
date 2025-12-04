"""Test script for the translation feature.

This script simulates a conversation to test the translation functionality
without requiring voice input.
"""

import asyncio
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bot_main import TranscriptLogger


async def test_translation():
    """Test the translation feature with simulated conversation data.

    Creates a simulated multilingual conversation and tests the translation
    functionality, generating sample transcript files for review.
    """
    print("=" * 80)
    print("Testing Multi-Language Transcript Translation Feature")
    print("=" * 80)
    print()

    # Create logger with translation enabled
    logger = TranscriptLogger(filename="test_conversation.txt", enable_translation=True)
    print(f"✓ TranscriptLogger initialized with translation enabled")
    print()

    # Simulate a multilingual conversation
    test_conversations = [
        ("SYSTEM", "Hotel receptionist agent started", "English"),
        ("USER", "Bonjour, je voudrais réserver une chambre", "French"),
        (
            "RECEPTIONIST",
            "Bonjour! I'd be happy to help you with a reservation. When would you like to check in?",
            "English",
        ),
        ("USER", "Je voudrais arriver le 15 décembre", "French"),
        ("RECEPTIONIST", "Perfect! And when will you be checking out?", "English"),
        ("USER", "El 20 de diciembre", "Spanish"),
        (
            "RECEPTIONIST",
            "Great! So that's December 15th to December 20th. How many guests will be staying?",
            "English",
        ),
        ("USER", "Dos personas", "Spanish"),
        (
            "RECEPTIONIST",
            "Wonderful! Two guests for 5 nights. What type of room would you prefer?",
            "English",
        ),
        ("USER", "Una habitación doble, por favor", "Spanish"),
        ("SYSTEM", "Session ended", "English"),
    ]

    print("Simulating conversation with multiple languages:")
    print("-" * 80)

    for speaker, message, expected_lang in test_conversations:
        logger.add_entry(speaker, message)
        print(f"[{speaker}]: {message}")
        if speaker in ["USER", "RECEPTIONIST"]:
            print(f"  (Expected language: {expected_lang})")

    print()
    print("-" * 80)
    print()

    # Save transcripts
    print("Saving transcripts...")
    original_file, bilingual_file = logger.save_full_transcript()
    json_file = logger.save_json_transcript()

    print(f"✓ Original transcript: {original_file}")
    print(f"✓ Bilingual transcript: {bilingual_file}")
    print(f"✓ JSON transcript: {json_file}")
    print()

    # Display sample from bilingual transcript
    if bilingual_file and os.path.exists(bilingual_file):
        print("=" * 80)
        print("Sample from Bilingual Transcript:")
        print("=" * 80)
        with open(bilingual_file, "r", encoding="utf-8") as f:
            content = f.read()
            # Show first 1500 characters
            print(content[:1500])
            if len(content) > 1500:
                print("\n... (truncated)")
        print()

    print("=" * 80)
    print("✓ Translation feature test completed successfully!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Review the generated transcript files")
    print("2. Verify translations are accurate")
    print("3. Test with the actual voice bot by running: python src/bot_main.py")
    print()


if __name__ == "__main__":
    asyncio.run(test_translation())
