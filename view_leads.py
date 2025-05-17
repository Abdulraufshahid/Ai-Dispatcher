"""
Script to view and display leads from leads.json in a formatted table.
"""

from leads_manager import get_all_leads
from tabulate import tabulate
from datetime import datetime
import json
import os

def format_timestamp(timestamp):
    """Format ISO timestamp to a more readable format."""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def format_responses(responses):
    """Format responses into a readable string."""
    formatted = []
    for key, data in responses.items():
        formatted.append(f"{key}: {data['response']}")
    return "\n".join(formatted)

def display_leads():
    """Display all leads in a formatted table."""
    leads = get_all_leads()
    
    if not leads:
        print("\n❌ No leads found in leads.json")
        return
    
    # Prepare table data
    headers = ["#", "Phone", "Timestamp", "Responses"]
    table_data = []
    
    for idx, lead in enumerate(leads, 1):
        row = [
            idx,
            lead["phone_number"],
            format_timestamp(lead["timestamp"]),
            format_responses(lead["responses"])
        ]
        table_data.append(row)
    
    # Print summary
    print("\n" + "="*80)
    print(f"📊 Lead Summary - Total Leads: {len(leads)}")
    print("="*80)
    
    # Print table
    print("\n" + tabulate(
        table_data,
        headers=headers,
        tablefmt="grid",
        numalign="left",
        stralign="left"
    ))
    
    # Print file info
    file_size = os.path.getsize("leads.json") / 1024  # Size in KB
    print(f"\n💾 leads.json size: {file_size:.1f} KB")

def main():
    try:
        display_leads()
    except Exception as e:
        print(f"\n❌ Error displaying leads: {str(e)}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main() 