"""
Configuration file for API keys and settings.
Replace the dummy values with your actual API keys and settings.
"""

# OpenAI Configuration
OPENAI_API_KEY = "sk-dummy-openai-api-key-123456789"

# Twilio Configuration
TWILIO_ACCOUNT_SID = "AC1234567890abcdef1234567890abcdef"
TWILIO_AUTH_TOKEN = "1234567890abcdef1234567890abcdef"
TWILIO_PHONE_NUMBER = "+1234567890"  # Format: +[country code][phone number]
DISPATCHER_PHONE_NUMBER = "+1987654321"  # Human dispatcher's phone number

# Notification Method
# Options: "email", "sms", "push", "webhook"
NOTIFICATION_METHOD = "sms"

# Optional: Add any additional configuration settings below
# For example:
# EMAIL_SETTINGS = {
#     "smtp_server": "smtp.example.com",
#     "smtp_port": 587,
#     "sender_email": "your-email@example.com"
# } 