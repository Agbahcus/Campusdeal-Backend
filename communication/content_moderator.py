"""
Content moderation utility for CampusDeal chat system.
Automatically detects and blocks sharing of contact information and locations.
"""
import re


class ContentModerator:
    """
    Automated chat moderation to prevent contact info sharing
    Implements 3-strike system for violations
    """
    
    # Regex patterns for detection
    PHONE_PATTERNS = [
        r'\b\d{11}\b',  # Nigerian 11-digit format: 08012345678
        r'\b0\d{10}\b',  # 0 followed by 10 digits
        r'\+234\d{10}\b',  # International format: +2348012345678
        r'\b234\d{10}\b',  # Without plus: 2348012345678
        r'\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b',  # Formatted: 080-123-4567
        r'\b\d{4}[-\s]?\d{3}[-\s]?\d{4}\b',  # Formatted: 0801-234-5678
    ]
    
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Keywords that suggest location/meetup sharing
    LOCATION_KEYWORDS = [
        'meet at', 'meet me at', 'come to', 'my place', 'my house', 'my room',
        'let\'s meet', 'lets meet', 'meetup', 'meet up',
        'my hostel', 'my dorm', 'room number', 'block', 'flat', 'apartment',
        'address is', 'located at', 'find me at',
        'whatsapp', 'telegram', 'call me', 'text me', 'dm me',
        'send location', 'share location', 'drop your number',
        'give me your number', 'what\'s your number', 'whats your number',
        'send your number', 'your contact', 'contact me at',
    ]
    
    def __init__(self):
        # Compile regex patterns for efficiency
        self.phone_regex_list = [re.compile(p, re.IGNORECASE) for p in self.PHONE_PATTERNS]
        self.email_regex = re.compile(self.EMAIL_PATTERN, re.IGNORECASE)
    
    def scan_message(self, text):
        """
        Scan message for violations
        
        Args:
            text: Message text to scan
        
        Returns:
            dict: {
                'is_clean': bool,
                'flags': list of violation types,
                'should_delete': bool,
                'warning_message': str or None
            }
        """
        if not text or not isinstance(text, str):
            return {
                'is_clean': True,
                'flags': [],
                'should_delete': False,
                'warning_message': None
            }
        
        text_lower = text.lower()
        flags = []
        
        # Check for phone numbers
        for pattern in self.phone_regex_list:
            if pattern.search(text):
                flags.append('PHONE_NUMBER')
                break  # Only flag once
        
        # Check for emails
        if self.email_regex.search(text):
            flags.append('EMAIL_ADDRESS')
        
        # Check for location/meetup keywords
        for keyword in self.LOCATION_KEYWORDS:
            if keyword in text_lower:
                flags.append('LOCATION_SHARING')
                break  # Only flag once
        
        is_clean = len(flags) == 0
        
        return {
            'is_clean': is_clean,
            'flags': flags,
            'should_delete': not is_clean,
            'warning_message': self._generate_warning(flags) if not is_clean else None
        }
    
    def _generate_warning(self, flags):
        """Generate user-friendly warning message"""
        violation_types = {
            'PHONE_NUMBER': 'phone number',
            'EMAIL_ADDRESS': 'email address',
            'LOCATION_SHARING': 'location or contact sharing attempt'
        }
        
        detected = ', '.join([violation_types.get(f, f) for f in flags])
        
        return (
            f"⚠️ Your message was blocked because it contained: {detected}. "
            "For your safety, all communication and transactions must stay on CampusDeal. "
            "Sharing contact details or arranging off-platform meetups violates our policy."
        )
    
    def get_strike_message(self, strike_number):
        """Get appropriate message based on strike number"""
        if strike_number == 1:
            return (
                "⚠️ STRIKE 1/3: This is your first warning. "
                "Please keep all communication on the platform. "
                "Do not share phone numbers, emails, or specific locations."
            )
        elif strike_number == 2:
            return (
                "⚠️ STRIKE 2/3: This is your second warning. "
                "One more violation will result in account suspension. "
                "All transactions and communication must remain on CampusDeal."
            )
        elif strike_number >= 3:
            return (
                "🚫 STRIKE 3/3: Your account has been suspended due to repeated violations "
                "of our communication policy. "
                "Contact support at support@campusdeal.ng if you believe this is an error."
            )
        else:
            return "Policy violation detected."
    
    def is_phone_number(self, text):
        """Quick check if text contains a phone number"""
        for pattern in self.phone_regex_list:
            if pattern.search(text):
                return True
        return False
    
    def is_email(self, text):
        """Quick check if text contains an email"""
        return bool(self.email_regex.search(text))
    
    def clean_test_messages(self):
        """
        Test the moderator with various messages
        Returns list of test results for debugging
        """
        test_messages = [
            # Should be blocked
            "Call me on 08012345678",
            "My number is +2348012345678",
            "Email me at test@example.com",
            "Meet me at my hostel room 23",
            "Let's meet outside the cafeteria",
            "Send me your WhatsApp number",
            "0801-234-5678 is my number",
            
            # Should pass
            "Is this still available?",
            "What's the condition?",
            "Can you deliver to Malete?",
            "How much is the shipping?",
            "Does it come with accessories?",
            "I'm interested in buying this",
        ]
        
        results = []
        for msg in test_messages:
            result = self.scan_message(msg)
            results.append({
                'message': msg,
                'is_clean': result['is_clean'],
                'flags': result['flags']
            })
        
        return results


# Singleton instance
moderator = ContentModerator()