
def validate_coordinates(lat, lng):
    """Validate latitude and longitude"""
    try:
        lat = float(lat)
        lng = float(lng)
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90"
        
        if not (-180 <= lng <= 180):
            return False, "Longitude must be between -180 and 180"
        
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid coordinate format"

def validate_phone(phone):
    """Validate phone number"""
    if not phone:
        return False, "Phone number is required"
    
    # Remove common separators
    cleaned = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    
    if not cleaned.isdigit():
        return False, "Phone number must contain only digits"
    
    if len(cleaned) < 10:
        return False, "Phone number must be at least 10 digits"
    
    return True, None
