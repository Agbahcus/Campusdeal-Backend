"""
Input validation utilities for CampusDeal
"""
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
import re


def validate_price(value):
    """Validate price is positive and reasonable"""
    try:
        price = Decimal(str(value))
        
        if price < 0:
            raise ValidationError("Price cannot be negative")
        
        if price < Decimal('100'):
            raise ValidationError("Minimum price is ₦100")
        
        if price > Decimal('10000000'):
            raise ValidationError("Maximum price is ₦10,000,000")
        
        if price.as_tuple().exponent < -2:
            raise ValidationError("Maximum 2 decimal places")
        
        return price
        
    except (InvalidOperation, ValueError):
        raise ValidationError("Invalid price format")


def validate_search_query(query):
    """Sanitize and validate search query"""
    if not query:
        return ""
    
    query = re.sub(r'[^\w\s-]', '', str(query))
    query = query[:100]
    
    if len(query) < 2:
        raise ValidationError("Search query too short (minimum 2 characters)")
    
    return query


def validate_image_size(image):
    """Validate image file size"""
    if image.size > 5 * 1024 * 1024:
        raise ValidationError("Image size must be less than 5MB")
    
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    if hasattr(image, 'content_type') and image.content_type not in allowed_types:
        raise ValidationError("Only JPEG and PNG images allowed")
    
    return image


def validate_amenities(amenities):
    """Validate hostel amenities list"""
    if not isinstance(amenities, list):
        raise ValidationError("Amenities must be a list")
    
    if len(amenities) > 20:
        raise ValidationError("Maximum 20 amenities allowed")
    
    for amenity in amenities:
        if not isinstance(amenity, str):
            raise ValidationError("Each amenity must be a string")
        if len(amenity) > 50:
            raise ValidationError("Amenity name too long (max 50 characters)")
    
    return amenities
