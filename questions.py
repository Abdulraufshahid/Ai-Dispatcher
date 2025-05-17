"""
Questions for the AI Truck Dispatcher to ask during calls.
Each question is a tuple of (key, question_text) where:
- key: unique identifier for storing the response
- question_text: the actual question to be asked
"""

DISPATCH_QUESTIONS = [
    ("truck_id", "What is your truck ID or license plate number?"),
    ("current_location", "What is your current location?"),
    ("destination", "What is your destination?"),
    ("cargo_type", "What type of cargo are you carrying?"),
    ("estimated_arrival", "What is your estimated arrival time?"),
    ("special_requirements", "Do you have any special requirements or concerns?"),
    ("contact_number", "What is the best number to reach you during the trip?"),
]

def get_question_text(key):
    """Get the question text for a given key."""
    for q_key, text in DISPATCH_QUESTIONS:
        if q_key == key:
            return text
    return None

def get_all_questions():
    """Get all questions as a list of (key, text) tuples."""
    return DISPATCH_QUESTIONS 