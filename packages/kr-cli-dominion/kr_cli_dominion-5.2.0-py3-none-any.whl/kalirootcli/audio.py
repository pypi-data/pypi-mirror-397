"""
Audio Module for KaliRoot CLI
Handles Speech-to-Text using Groq Whisper API.
"""

import os
import time
import logging
import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
from .config import GROQ_API_KEY
from .ui.display import console, show_loading, print_error, print_success

logger = logging.getLogger(__name__)

class AudioHandler:
    """Handles audio recording and transcription."""
    
    def __init__(self):
        self.samplerate = 44100
        self.channels = 1
        
    def record_audio(self, duration: int = 5, filename: str = "command.wav") -> str:
        """
        Record audio from microphone.
        
        Args:
            duration: Seconds to record
            filename: Output filename
            
        Returns:
            Path to recorded file or None
        """
        try:
            print(f"🎙️ Escuchando... ({duration}s)")
            
            # Record
            recording = sd.rec(
                int(duration * self.samplerate), 
                samplerate=self.samplerate, 
                channels=self.channels,
                dtype='int16'
            )
            sd.wait()
            
            # Save
            filepath = os.path.join(os.getcwd(), filename)
            wav.write(filepath, self.samplerate, recording)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Recording error: {e}")
            print_error(f"Error grabando audio: {e}")
            return None

    def transcribe(self, filepath: str) -> str:
        """
        Transcribe audio using Groq Whisper.
        """
        if not GROQ_API_KEY:
            return "Error: API Key no configurada."
            
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        try:
            with open(filepath, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(filepath, file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                    language="es",  # Force Spanish context
                    temperature=0.0
                )
                return transcription.text
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return f"Error transcribiendo: {e}"
            
def listen_and_execute():
    """Main voice functionality."""
    handler = AudioHandler()
    
    # 1. Record
    filepath = handler.record_audio(duration=5)
    if not filepath:
        return
        
    # 2. Transcribe
    with show_loading("🧠 Transcribiendo voz..."):
        text = handler.transcribe(filepath)
        
    console.print(f"\n[bold cyan]🗣️ Dijiste:[/bold cyan] '{text}'\n")
    
    # Clean up
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except:
            pass
            
    # 3. Execute
    if text and "Error" not in text:
        # We pass this text to execute_and_analyze logic
        # But since we are in a standalone function, we import it or return
        return text
    return None
