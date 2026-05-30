"""
ONE-TIME SETUP ENDPOINT FOR RENDER
DELETE THIS FILE AFTER INITIAL SETUP!
"""
from django.conf import settings
from django.utils.crypto import get_random_string
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
    if not settings.DEBUG:
        return Response(
            {"error": "Setup endpoint is disabled"},
            status=404
        )
    
    results = {
        "superuser": None,
        "categories": [],
        "warnings": []
    }
    
    # Create superuser
    if not User.objects.filter(username='admin').exists():
        admin_password = getattr(settings, 'INITIAL_SETUP_PASSWORD', '')
        if not admin_password:
            admin_password = get_random_string(20)

        User.objects.create_superuser(
            username='admin',
            email='admin@campusdeal.com',
            password=admin_password
        )
        results["superuser"] = {
            "username": "admin",
            "password": admin_password,
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
