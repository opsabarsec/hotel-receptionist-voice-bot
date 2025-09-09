"""
Voice Input Handler Module

This module handles voice input capture and preprocessing for the hotel receptionist voice bot.
It provides functionality to capture audio from various sources and prepare it for speech processing.

Author: Hotel Voice Bot Team
Date: September 2025
"""

import asyncio
import logging
import numpy as np
import sounddevice as sd
from typing import Optional, Callable, List
from dataclasses import dataclass
import threading
import queue


@dataclass
class AudioConfig:
    """Configuration for audio input settings."""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    dtype: str = 'float32'
    device_id: Optional[int] = None


class VoiceInputHandler:
    """
    Handles voice input capture and preprocessing.
    
    This class provides methods to capture audio input from microphone,
    preprocess the audio data, and manage audio streaming for real-time
    voice processing.
    """
    
    def __init__(self, config: AudioConfig = None):
        """
        Initialize the voice input handler.
        
        Args:
            config (AudioConfig): Audio configuration settings
        """
        self.config = config or AudioConfig()
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.callbacks: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        
    def add_callback(self, callback: Callable):
        """
        Add a callback function to be called when audio is captured.
        
        Args:
            callback (Callable): Function to call with audio data
        """
        self.callbacks.append(callback)
        
    def remove_callback(self, callback: Callable):
        """
        Remove a callback function.
        
        Args:
            callback (Callable): Function to remove
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _audio_callback(self, indata, frames, time, status):
        """
        Internal callback for audio input stream.
        
        Args:
            indata: Input audio data
            frames: Number of frames
            time: Timing information
            status: Stream status
        """
        if status:
            self.logger.warning(f"Audio input status: {status}")
            
        # Convert to float32 and normalize
        audio_data = indata.copy().astype(np.float32)
        
        # Add to queue
        try:
            self.audio_queue.put_nowait(audio_data)
        except queue.Full:
            self.logger.warning("Audio queue is full, dropping frames")
            
        # Call registered callbacks
        for callback in self.callbacks:
            try:
                callback(audio_data)
            except Exception as e:
                self.logger.error(f"Error in audio callback: {e}")
    
    def start_recording(self) -> bool:
        """
        Start recording audio from the microphone.
        
        Returns:
            bool: True if recording started successfully, False otherwise
        """
        if self.is_recording:
            self.logger.warning("Already recording")
            return False
            
        try:
            self.stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                blocksize=self.config.chunk_size,
                dtype=self.config.dtype,
                device=self.config.device_id,
                callback=self._audio_callback
            )
            
            self.stream.start()
            self.is_recording = True
            self.logger.info("Audio recording started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self):
        """
        Stop recording audio.
        """
        if not self.is_recording:
            return
            
        try:
            self.stream.stop()
            self.stream.close()
            self.is_recording = False
            self.logger.info("Audio recording stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
    
    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Get the next audio chunk from the queue.
        
        Args:
            timeout (float): Timeout in seconds
            
        Returns:
            Optional[np.ndarray]: Audio data or None if timeout
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def clear_audio_queue(self):
        """
        Clear all pending audio data from the queue.
        """
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
    
    def get_available_devices(self) -> List[dict]:
        """
        Get list of available audio input devices.
        
        Returns:
            List[dict]: List of device information dictionaries
        """
        try:
            devices = sd.query_devices()
            input_devices = []
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate']
                    })
                    
            return input_devices
            
        except Exception as e:
            self.logger.error(f"Error querying devices: {e}")
            return []
    
    def test_microphone(self, duration: float = 2.0) -> bool:
        """
        Test if microphone is working by recording for a short duration.
        
        Args:
            duration (float): Test duration in seconds
            
        Returns:
            bool: True if microphone is working, False otherwise
        """
        try:
            recording = sd.rec(
                int(duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype=self.config.dtype,
                device=self.config.device_id
            )
            sd.wait()
            
            # Check if we got actual audio data
            if np.max(np.abs(recording)) > 0.001:  # Threshold for detecting audio
                self.logger.info("Microphone test successful")
                return True
            else:
                self.logger.warning("Microphone test detected no audio")
                return False
                
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start_recording()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_recording()


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create voice input handler
    handler = VoiceInputHandler()
    
    # Test microphone
    print("Testing microphone...")
    if handler.test_microphone():
        print("✓ Microphone is working")
    else:
        print("✗ Microphone test failed")
    
    # List available devices
    print("\nAvailable input devices:")
    devices = handler.get_available_devices()
    for device in devices:
        print(f"  {device['id']}: {device['name']} ({device['channels']} channels)")
    
    # Example of using the handler
    def audio_callback(data):
        """Example callback function."""
        volume = np.sqrt(np.mean(data**2))
        if volume > 0.01:  # Threshold for voice activity
            print(f"Voice detected! Volume: {volume:.3f}")
    
    # Add callback and start recording
    handler.add_callback(audio_callback)
    
    print("\nStarting recording for 5 seconds...")
    with handler:
        import time
        time.sleep(5)
    
    print("Recording finished.")
