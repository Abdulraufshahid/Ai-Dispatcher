"""
Module for scoring and ranking trucker leads based on various criteria.
"""

from datetime import datetime, timedelta
import re

# Scoring weights
WEIGHTS = {
    'truck_type': 0.3,
    'availability': 0.4,
    'route': 0.3
}

# Preferred truck types and their scores
TRUCK_TYPES = {
    'reefer': 1.0,  # Refrigerated trucks
    'flatbed': 0.9,
    'box': 0.8,
    'dry van': 0.8,
    'tanker': 0.7,
    'step deck': 0.7
}

# Preferred routes (origin -> destination) and their scores
PREFERRED_ROUTES = {
    ('los angeles', 'new york'): 1.0,
    ('chicago', 'miami'): 0.9,
    ('dallas', 'seattle'): 0.8,
    ('atlanta', 'chicago'): 0.8,
    ('houston', 'denver'): 0.7
}

def normalize_location(location):
    """Normalize location string for comparison."""
    return location.lower().strip()

def score_truck_type(cargo_type):
    """
    Score based on truck type/cargo type.
    
    Args:
        cargo_type (str): Type of cargo being transported
    
    Returns:
        float: Score between 0 and 1
    """
    cargo_type = cargo_type.lower()
    
    # Check for refrigerated cargo
    if any(word in cargo_type for word in ['refrigerated', 'reefer', 'cold', 'frozen']):
        return TRUCK_TYPES['reefer']
    
    # Check for other truck types
    for truck_type, score in TRUCK_TYPES.items():
        if truck_type in cargo_type:
            return score
    
    return 0.5  # Default score for unknown types

def score_availability(eta):
    """
    Score based on availability timing.
    
    Args:
        eta (str): Estimated arrival time
    
    Returns:
        float: Score between 0 and 1
    """
    try:
        # Try to parse the ETA
        if 'today' in eta.lower():
            return 1.0
        
        # Try to extract date and time
        now = datetime.now()
        
        # Try different date formats
        for fmt in ['%Y-%m-%d %H:%M', '%m/%d/%Y %H:%M', '%Y-%m-%d']:
            try:
                eta_date = datetime.strptime(eta, fmt)
                # Score higher for availability within 24 hours
                if eta_date - now <= timedelta(hours=24):
                    return 0.9
                elif eta_date - now <= timedelta(days=3):
                    return 0.7
                else:
                    return 0.5
            except ValueError:
                continue
        
        return 0.5  # Default score if parsing fails
        
    except Exception:
        return 0.5  # Default score for any errors

def score_route(origin, destination):
    """
    Score based on route preferences.
    
    Args:
        origin (str): Starting location
        destination (str): Ending location
    
    Returns:
        float: Score between 0 and 1
    """
    origin = normalize_location(origin)
    destination = normalize_location(destination)
    
    # Check for exact route match
    route = (origin, destination)
    if route in PREFERRED_ROUTES:
        return PREFERRED_ROUTES[route]
    
    # Check for partial matches (e.g., "Los Angeles, CA" matches "los angeles")
    for (pref_origin, pref_dest), score in PREFERRED_ROUTES.items():
        if pref_origin in origin and pref_dest in destination:
            return score * 0.9  # Slightly lower score for partial matches
    
    return 0.5  # Default score for unknown routes

def calculate_lead_score(lead):
    """
    Calculate overall score for a lead.
    
    Args:
        lead (dict): Lead dictionary containing responses
    
    Returns:
        float: Overall score between 0 and 1
    """
    responses = lead['responses']
    
    # Get individual scores
    truck_score = score_truck_type(
        responses.get('cargo_type', {}).get('response', '')
    )
    
    availability_score = score_availability(
        responses.get('estimated_arrival', {}).get('response', '')
    )
    
    route_score = score_route(
        responses.get('current_location', {}).get('response', ''),
        responses.get('destination', {}).get('response', '')
    )
    
    # Calculate weighted score
    overall_score = (
        truck_score * WEIGHTS['truck_type'] +
        availability_score * WEIGHTS['availability'] +
        route_score * WEIGHTS['route']
    )
    
    return round(overall_score, 2)

def add_score_to_lead(lead):
    """
    Add score to lead dictionary.
    
    Args:
        lead (dict): Lead dictionary
    
    Returns:
        dict: Lead dictionary with added score
    """
    lead['score'] = calculate_lead_score(lead)
    return lead 