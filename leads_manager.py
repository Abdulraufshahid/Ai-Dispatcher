"""
Module for managing trucker leads and their responses.
Handles saving and loading leads from a JSON file.
"""

import json
import os
from datetime import datetime
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, DISPATCHER_PHONE_NUMBER
from lead_scorer import add_score_to_lead

LEADS_FILE = "leads.json"

def send_sms_notification():
    """
    Send SMS notification to the human dispatcher about a new lead.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body="New trucker lead captured. Check leads.json.",
            from_=TWILIO_PHONE_NUMBER,
            to=DISPATCHER_PHONE_NUMBER
        )
        
        print(f"\n📱 SMS notification sent to dispatcher (SID: {message.sid})")
        return True
        
    except Exception as e:
        print(f"\n❌ Error sending SMS notification: {str(e)}")
        return False

def load_leads():
    """Load existing leads from the JSON file."""
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Error reading leads file. Creating new file.")
            return []
    return []

def save_lead(responses, phone_number):
    """
    Save a new lead to the leads file and notify the dispatcher.
    
    Args:
        responses (dict): Dictionary of question keys and responses
        phone_number (str): Trucker's phone number
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load existing leads
        leads = load_leads()
        
        # Create new lead entry
        new_lead = {
            "phone_number": phone_number,
            "timestamp": datetime.now().isoformat(),
            "responses": responses
        }
        
        # Add score to the lead
        new_lead = add_score_to_lead(new_lead)
        
        # Append new lead
        leads.append(new_lead)
        
        # Sort leads by score (highest first)
        leads.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Save updated leads
        with open(LEADS_FILE, 'w') as f:
            json.dump(leads, f, indent=4)
        
        print(f"\n💾 Lead saved to {LEADS_FILE}")
        print(f"📊 Lead score: {new_lead['score']}")
        
        # Send SMS notification
        if send_sms_notification():
            print("✅ Dispatcher notified via SMS")
        else:
            print("⚠️ Failed to send SMS notification")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error saving lead: {str(e)}")
        return False

def get_all_leads():
    """Get all saved leads."""
    return load_leads()

def get_lead_count():
    """Get the total number of leads."""
    return len(load_leads()) 