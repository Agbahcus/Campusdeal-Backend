"""
ONE-TIME SETUP ENDPOINT FOR RENDER
DELETE THIS FILE AFTER INITIAL SETUP!
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from marketplace.models import ItemCategory


@api_view(['POST'])
def initial_setup(request):
    """
    One-time setup endpoint for Render deployment
    Creates superuser and categories
    
    ⚠️ DELETE THIS ENDPOINT AFTER USE! ⚠️
    """
    
    results = {
        "superuser": None,
        "categories": [],
        "warnings": []
    }
    
    # Create superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@campusdeal.com',
            password='CampusDeal2024!'  # CHANGE THIS IN ADMIN PANEL!
        )
        results["superuser"] = {
            "username": "admin",
            "password": "CampusDeal2024!",
            "message": "⚠️ CHANGE PASSWORD IMMEDIATELY IN ADMIN PANEL!"
        }
    else:
        results["superuser"] = "Already exists"
    
    # Create categories
    categories = [
        'Electronics', 'Books', 'Clothing', 'Furniture',
        'Phones', 'Laptops', 'Accessories', 'Other'
    ]
    
    for cat_name in categories:
        category, created = ItemCategory.objects.get_or_create(name=cat_name)
        if created:
            results["categories"].append(f"Created: {cat_name}")
        else:
            results["categories"].append(f"Exists: {cat_name}")
    
    # Add warnings
    results["warnings"] = [
        "⚠️ DELETE THIS ENDPOINT IMMEDIATELY AFTER USE!",
        "⚠️ CHANGE ADMIN PASSWORD IN ADMIN PANEL!",
        "⚠️ Remove marketplace/setup_views.py",
        "⚠️ Remove setup URL from marketplace/urls.py"
    ]
    
    return Response(results)
