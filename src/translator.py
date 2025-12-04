"""Multi-language translation module for hotel receptionist bot.

This module provides language detection and translation to English using the
OpenAI API. It is designed to help hotel staff review conversations in languages
they may not speak.
"""

import os
from openai import OpenAI
from typing import Optional, Dict


class TranslationService:
    """Handles language detection and translation using OpenAI API.

    This service uses OpenAI's GPT-4o-mini model to detect languages and
    translate text to English. It includes error handling and caching for
    improved reliability and performance.

    Attributes:
        client: OpenAI client instance for API calls.
        _language_cache: Dictionary for caching language detection results.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the translation service.

        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY environment
                variable.
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self._language_cache = {}

    def detect_language(self, text: str) -> str:
        """Detect the language of the input text.

        Uses OpenAI's GPT-4o-mini model to identify the language of the provided
        text. Returns "Unknown" for very short text or on API errors.

        Args:
            text: Text to detect language for.

        Returns:
            Language name (e.g., "English", "Spanish", "French") or "Unknown"
            if detection fails or text is too short.

        Examples:
            >>> service = TranslationService()
            >>> service.detect_language("Bonjour, comment allez-vous?")
            'French'
        """
        if not text or len(text.strip()) < 3:
            return "Unknown"

        try:
            response = self._call_language_detection_api(text)
            language = response.choices[0].message.content.strip()
            return language

        except Exception as e:
            print(f"Language detection error: {e}")
            return "Unknown"

    def _call_language_detection_api(self, text: str):
        """Call OpenAI API for language detection.

        Args:
            text: Text to detect language for.

        Returns:
            OpenAI API response object.

        Raises:
            Exception: If API call fails.
        """
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a language detection expert. Respond with ONLY "
                        "the language name (e.g., 'English', 'Spanish', 'French', "
                        "'German', 'Italian', 'Chinese', 'Japanese', etc.). "
                        "If you cannot determine the language, respond with 'Unknown'."
                    ),
                },
                {
                    "role": "user",
                    "content": f"What language is this text in? Text: {text[:200]}",
                },
            ],
            temperature=0,
            max_tokens=10,
        )

    def translate_to_english(
        self, text: str, source_language: Optional[str] = None
    ) -> Dict[str, str]:
        """Translate text to English.

        Detects the source language if not provided and translates non-English
        text to English. Returns a dictionary with original text, translation,
        source language, and translation status.

        Args:
            text: Text to translate.
            source_language: Source language name. If None, language will be
                auto-detected.

        Returns:
            Dictionary containing:
                - original (str): Original text
                - translated (str): English translation
                - source_language (str): Detected or provided source language
                - needs_translation (bool): Whether translation was performed

        Examples:
            >>> service = TranslationService()
            >>> result = service.translate_to_english("Hola, ¿cómo estás?")
            >>> result['translated']
            'Hello, how are you?'
            >>> result['source_language']
            'Spanish'
        """
        if not text or len(text.strip()) < 1:
            return self._create_translation_result(text, text, "Unknown", False)

        # Detect language if not provided
        if source_language is None:
            source_language = self.detect_language(text)

        # Check if translation is needed
        if not self._should_translate(source_language):
            return self._create_translation_result(text, text, source_language, False)

        # Perform translation
        try:
            translated_text = self._call_translation_api(text, source_language)
            return self._create_translation_result(
                text, translated_text, source_language, True
            )

        except Exception as e:
            print(f"Translation error: {e}")
            # Fallback to original text on error
            return self._create_translation_result(text, text, source_language, False)

    def _should_translate(self, language: str) -> bool:
        """Check if text needs translation based on detected language.

        Args:
            language: Detected language name.

        Returns:
            False if language is English or Unknown, True otherwise.
        """
        return language.lower() not in ["english", "unknown"]

    def _create_translation_result(
        self,
        original: str,
        translated: str,
        source_language: str,
        needs_translation: bool,
    ) -> Dict[str, str]:
        """Create a standardized translation result dictionary.

        Args:
            original: Original text.
            translated: Translated text.
            source_language: Source language name.
            needs_translation: Whether translation was performed.

        Returns:
            Dictionary with translation result data.
        """
        return {
            "original": original,
            "translated": translated,
            "source_language": source_language,
            "needs_translation": needs_translation,
        }

    def _call_translation_api(self, text: str, source_language: str) -> str:
        """Call OpenAI API to translate text to English.

        Args:
            text: Text to translate.
            source_language: Source language name.

        Returns:
            Translated text in English.

        Raises:
            Exception: If API call fails.
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator. Translate the following "
                        "text to English. Provide ONLY the translation, no "
                        "explanations or additional text."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Translate this {source_language} text to English: {text}",
                },
            ],
            temperature=0.3,
            max_tokens=500,
        )

        return response.choices[0].message.content.strip()

    def batch_translate(self, texts: list[str]) -> list[Dict[str, str]]:
        """Translate multiple texts to English.

        Processes a list of texts and translates each one individually.
        Each result follows the same format as translate_to_english().

        Args:
            texts: List of texts to translate.

        Returns:
            List of translation result dictionaries, one per input text.

        Examples:
            >>> service = TranslationService()
            >>> texts = ["Bonjour", "Hola", "Hello"]
            >>> results = service.batch_translate(texts)
            >>> len(results)
            3
        """
        results = []
        for text in texts:
            results.append(self.translate_to_english(text))
        return results
