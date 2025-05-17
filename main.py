from config import OPENAI_API_KEY, NOTIFICATION_METHOD, TWILIO_PHONE_NUMBER
from voice_utils import record_audio, transcribe_audio, make_call
from questions import DISPATCH_QUESTIONS, get_question_text
from leads_manager import save_lead, get_lead_count
import time
import json
from datetime import datetime

def mask_api_key(api_key, visible_chars=4):
    """Mask an API key showing only the first few characters."""
    if len(api_key) <= visible_chars:
        return '*' * len(api_key)
    return api_key[:visible_chars] + '*' * (len(api_key) - visible_chars)

def print_boot_message():
    """Print the system boot message with masked API key."""
    print("\n" + "="*50)
    print("🤖 AI Truck Dispatcher System - Booting Up")
    print("="*50)
    print(f"OpenAI API Key: {mask_api_key(OPENAI_API_KEY)}")
    print(f"Notification Method: {NOTIFICATION_METHOD}")
    print(f"Total Leads Collected: {get_lead_count()}")
    print("="*50 + "\n")

def check_dispatch_keywords(text):
    """Check if the transcribed text contains dispatch-related keywords."""
    keywords = ["dispatch", "truck", "delivery", "shipment", "cargo"]
    return any(keyword.lower() in text.lower() for keyword in keywords)

def save_responses(responses, trucker_id):
    """Save the responses to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dispatch_responses_{trucker_id}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(responses, f, indent=4)
    
    print(f"\n💾 Responses saved to {filename}")
    return filename

def conduct_interview(phone_number):
    """Conduct an interview with the trucker using the predefined questions."""
    responses = {}
    
    try:
        # Initial greeting
        greeting = "Hello, I'm your AI dispatcher. I'll be asking you a few questions about your trip."
        print(f"\n📞 Initiating call to {phone_number}...")
        make_call(phone_number, greeting)
        time.sleep(2)  # Wait for the greeting to finish
        
        # Ask each question and record responses
        for key, question in DISPATCH_QUESTIONS:
            print(f"\n❓ Asking: {question}")
            
            # Ask the question
            make_call(phone_number, question)
            time.sleep(1)  # Wait for the question to finish
            
            # Record response
            print("🎤 Recording response...")
            audio_file = record_audio(duration=15, output_file=f"response_{key}.wav")
            
            # Transcribe response
            print("📝 Transcribing response...")
            response = transcribe_audio(audio_file)
            print(f"✅ Response: {response}")
            
            # Store response
            responses[key] = {
                "question": question,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            # Acknowledge response
            acknowledgment = "Thank you for that information."
            make_call(phone_number, acknowledgment)
            time.sleep(1)
        
        # Final message
        conclusion = "Thank you for providing all the information. Your dispatch details have been recorded."
        make_call(phone_number, conclusion)
        
        # Save responses to individual file
        save_responses(responses, phone_number)
        
        # Save to leads file
        if save_lead(responses, phone_number):
            print("\n✅ Lead successfully added to leads database")
        else:
            print("\n⚠️ Failed to save lead to database")
        
        return responses
        
    except Exception as e:
        print(f"\n❌ Error during interview: {str(e)}")
        return None

def main():
    # Print boot message
    print_boot_message()
    
    try:
        # Step 1: Record initial audio
        print("\n🎤 Recording initial audio input...")
        audio_file = record_audio(output_file="input.wav")
        print("✅ Audio recording completed")
        
        # Step 2: Transcribe audio
        print("\n📝 Transcribing audio...")
        transcription = transcribe_audio(audio_file)
        print(f"✅ Transcription: {transcription}")
        
        # Step 3: Check for dispatch keywords and conduct interview if found
        if check_dispatch_keywords(transcription):
            print("\n🚛 Dispatch keywords detected!")
            test_number = "+1234567890"  # Replace with actual test number
            
            print("\n📋 Starting dispatch interview...")
            responses = conduct_interview(test_number)
            
            if responses:
                print("\n✅ Interview completed successfully")
                print("\n📊 Collected Information:")
                for key, data in responses.items():
                    print(f"\n{data['question']}")
                    print(f"Response: {data['response']}")
            else:
                print("❌ Interview failed")
        else:
            print("\nℹ️ No dispatch keywords detected in transcription")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "="*50)
    print("System shutdown complete")
    print("="*50)

if __name__ == "__main__":
    main() 