"""
Streamlit dashboard for viewing and filtering trucker leads.
"""

import streamlit as st
import json
from datetime import datetime
import pandas as pd
from leads_manager import get_all_leads
from sheets_sync import SheetsSync

def format_timestamp(timestamp):
    """Format ISO timestamp to a more readable format."""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def load_leads_data():
    """Load and format leads data for the dashboard."""
    leads = get_all_leads()
    
    # Transform leads into a format suitable for pandas DataFrame
    formatted_leads = []
    for lead in leads:
        # Extract responses into separate fields
        responses = lead['responses']
        formatted_lead = {
            'Score': lead.get('score', 0),  # Add score
            'Phone': lead['phone_number'],
            'Timestamp': format_timestamp(lead['timestamp']),
            'Truck ID': responses.get('truck_id', {}).get('response', ''),
            'Current Location': responses.get('current_location', {}).get('response', ''),
            'Destination': responses.get('destination', {}).get('response', ''),
            'Cargo Type': responses.get('cargo_type', {}).get('response', ''),
            'ETA': responses.get('estimated_arrival', {}).get('response', ''),
            'Special Requirements': responses.get('special_requirements', {}).get('response', ''),
            'Contact Number': responses.get('contact_number', {}).get('response', '')
        }
        formatted_leads.append(formatted_lead)
    
    return pd.DataFrame(formatted_leads)

def filter_dataframe(df, search_term):
    """Filter dataframe based on search term."""
    if not search_term:
        return df
    
    # Convert all columns to string and search case-insensitive
    mask = df.astype(str).apply(lambda x: x.str.lower().str.contains(search_term.lower())).any(axis=1)
    return df[mask]

def main():
    st.set_page_config(
        page_title="Trucker Leads Dashboard",
        page_icon="🚛",
        layout="wide"
    )
    
    # Title and description
    st.title("🚛 Trucker Leads Dashboard")
    st.markdown("View and filter trucker leads captured by the AI Dispatcher system.")
    
    try:
        # Load data
        df = load_leads_data()
        
        if df.empty:
            st.warning("No leads found in the database.")
            return
        
        # Sidebar filters and sync options
        st.sidebar.header("Filters")
        search_term = st.sidebar.text_input("Search leads", "")
        
        # Score filter
        min_score = st.sidebar.slider(
            "Minimum Score",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1
        )
        
        st.sidebar.header("Google Sheets Sync")
        spreadsheet_id = st.sidebar.text_input(
            "Google Sheet ID",
            help="Enter the ID from your Google Sheet URL (the long string between /d/ and /edit)"
        )
        
        if st.sidebar.button("Sync to Google Sheets"):
            if spreadsheet_id:
                with st.spinner("Syncing to Google Sheets..."):
                    sheets_sync = SheetsSync(spreadsheet_id)
                    leads = get_all_leads()
                    if sheets_sync.sync_leads(leads):
                        st.sidebar.success("✅ Successfully synced to Google Sheets!")
                        st.sidebar.markdown(f"[Open Google Sheet]({sheets_sync.get_sheet_url()})")
                    else:
                        st.sidebar.error("❌ Failed to sync to Google Sheets")
            else:
                st.sidebar.error("Please enter a Google Sheet ID")
        
        # Filter data
        filtered_df = filter_dataframe(df, search_term)
        filtered_df = filtered_df[filtered_df['Score'] >= min_score]
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Leads", len(df))
        with col2:
            st.metric("Filtered Leads", len(filtered_df))
        with col3:
            st.metric("Active Locations", df['Current Location'].nunique())
        with col4:
            st.metric("Average Score", f"{df['Score'].mean():.2f}")
        
        # Display data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name="trucker_leads.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

if __name__ == "__main__":
    main() 