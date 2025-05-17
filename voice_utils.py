import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import whisper
import os
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

def record_audio(duration=10, sample_rate=44100, output_file="recording.wav"):
    """
    Record audio from the microphone for a specified duration.
    
    Args:
        duration (int): Recording duration in seconds
        sample_rate (int): Audio sample rate
        output_file (str): Path to save the WAV file
    
    Returns:
        str: Path to the saved audio file
    """
    print(f"Recording {duration} seconds of audio...")
    
    # Record audio
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16'
    )
    sd.wait()  # Wait until recording is finished
    
    # Save to WAV file
    wav.write(output_file, sample_rate, recording)
    print(f"Audio saved to {output_file}")
    
    return output_file

def transcribe_audio(file_path):
    """
    Transcribe audio file using OpenAI's Whisper model.
    
    Args:
        file_path (str): Path to the audio file
    
    Returns:
        str: Transcribed text
    """
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    
    print("Transcribing audio...")
    result = model.transcribe(file_path)
    
    return result["text"]

def make_call(to_number, message):
    """
    Make an outbound call using Twilio and speak the message.
    
    Args:
        to_number (str): Phone number to call (in E.164 format)
        message (str): Message to speak during the call
    
    Returns:
        str: Call SID if successful
    """
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Create TwiML for the call
        twiml = f"""
        <Response>
            <Say>{message}</Say>
        </Response>
        """
        
        # Make the call
        call = client.calls.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            twiml=twiml
        )
        
        print(f"Call initiated to {to_number}")
        return call.sid
        
    except Exception as e:
        print(f"Error making call: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    # Record audio
    audio_file = record_audio()
    
    # Transcribe audio
    transcription = transcribe_audio(audio_file)
    print(f"Transcription: {transcription}")
    
    # Make a test call (uncomment to test)
    # call_sid = make_call("+1234567890", "This is a test message from the AI Truck Dispatcher.") 