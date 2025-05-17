"""
Module for syncing leads data with Google Sheets.
"""

import os
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class SheetsSync:
    def __init__(self, spreadsheet_id):
        """
        Initialize Google Sheets sync.
        
        Args:
            spreadsheet_id (str): The ID of the Google Sheet to sync with
        """
        self.spreadsheet_id = spreadsheet_id
        self.creds = None
        self.service = None
        self.initialize_service()
    
    def initialize_service(self):
        """Initialize the Google Sheets service."""
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('sheets', 'v4', credentials=self.creds)
    
    def format_leads_for_sheets(self, leads):
        """
        Format leads data for Google Sheets.
        
        Args:
            leads (list): List of lead dictionaries
        
        Returns:
            list: Formatted data for sheets
        """
        # Headers
        headers = [
            'Phone', 'Timestamp', 'Truck ID', 'Current Location',
            'Destination', 'Cargo Type', 'ETA', 'Special Requirements',
            'Contact Number'
        ]
        
        # Format data
        rows = [headers]
        for lead in leads:
            responses = lead['responses']
            row = [
                lead['phone_number'],
                datetime.fromisoformat(lead['timestamp']).strftime("%Y-%m-%d %H:%M:%S"),
                responses.get('truck_id', {}).get('response', ''),
                responses.get('current_location', {}).get('response', ''),
                responses.get('destination', {}).get('response', ''),
                responses.get('cargo_type', {}).get('response', ''),
                responses.get('estimated_arrival', {}).get('response', ''),
                responses.get('special_requirements', {}).get('response', ''),
                responses.get('contact_number', {}).get('response', '')
            ]
            rows.append(row)
        
        return rows
    
    def sync_leads(self, leads):
        """
        Sync leads to Google Sheets.
        
        Args:
            leads (list): List of lead dictionaries
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Format data
            values = self.format_leads_for_sheets(leads)
            
            # Clear existing data
            range_name = 'Leads!A1:Z1000'  # Adjust range as needed
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            # Update with new data
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"\n✅ Synced {len(leads)} leads to Google Sheets")
            return True
            
        except Exception as e:
            print(f"\n❌ Error syncing to Google Sheets: {str(e)}")
            return False
    
    def get_sheet_url(self):
        """Get the URL of the Google Sheet."""
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}" 