"""
Management command to create test data for development

Usage: python manage.py create_test_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from marketplace.models import ItemCategory, ItemListing
from decimal import Decimal


class Command(BaseCommand):
    help = 'Creates test data for development'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')
        
        # Create categories
        categories_data = [
            {'name': 'Textbooks', 'icon': 'book'},
            {'name': 'Electronics', 'icon': 'laptop'},
            {'name': 'Furniture', 'icon': 'chair'},
            {'name': 'Clothing', 'icon': 'shirt'},
            {'name': 'Kitchen Items', 'icon': 'utensils'},
        ]
        
        categories = []
        for cat_data in categories_data:
            cat, created = ItemCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data['icon']}
            )
            categories.append(cat)
            if created:
                self.stdout.write(f'Created category: {cat.name}')
        
        # Create test users
        test_users_data = [
            {
                'username': '+2348011111111',
                'email': 'seller1@test.com',
                'password': 'test123',
                'first_name': 'John',
                'last_name': 'Seller',
                'phone': '+2348011111111',
                'location': 'ilorin'
            },
            {
                'username': '+2348022222222',
                'email': 'seller2@test.com',
                'password': 'test123',
                'first_name': 'Jane',
                'last_name': 'Merchant',
                'phone': '+2348022222222',
                'location': 'malete'
            },
        ]
        
        users = []
        for user_data in test_users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                
                # Create profile
                Profile.objects.create(
                    user=user,
                    phone_number=user_data['phone'],
                    primary_location=user_data['location'],
                    phone_verified=True,
                    university='University of Ilorin'
                )
                self.stdout.write(f'Created user: {user.get_full_name()}')
            users.append(user)
        
        # Create sample listings
        listings_data = [
            {
                'title': 'Engineering Mathematics Textbook',
                'description': 'Advanced Engineering Mathematics by Kreyszig, 10th Edition',
                'category': categories[0],
                'condition': 'fairly_used',
                'price': Decimal('3500.00'),
                'location': 'ilorin',
                'seller': users[0]
            },
            {
                'title': 'HP Laptop - Core i5',
                'description': 'HP ProBook 450, 8GB RAM, 500GB HDD, Good condition',
                'category': categories[1],
                'condition': 'used',
                'price': Decimal('85000.00'),
                'location': 'ilorin',
                'seller': users[0]
            },
            {
                'title': 'Study Table and Chair',
                'description': 'Wooden study desk with matching chair',
                'category': categories[2],
                'condition': 'fairly_used',
                'price': Decimal('12000.00'),
                'location': 'malete',
                'seller': users[1]
            },
            {
                'title': 'Physics Textbook - Fundamentals',
                'description': 'Halliday & Resnick Physics textbook',
                'category': categories[0],
                'condition': 'new',
                'price': Decimal('4500.00'),
                'location': 'ilorin',
                'seller': users[1]
            },
        ]
        
        for listing_data in listings_data:
            listing, created = ItemListing.objects.get_or_create(
                title=listing_data['title'],
                seller=listing_data['seller'],
                defaults=listing_data
            )
            if created:
                self.stdout.write(f'Created listing: {listing.title}')
        
        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))
        self.stdout.write('\nTest Users:')
        self.stdout.write('Username: +2348011111111, Password: test123')
        self.stdout.write('Username: +2348022222222, Password: test123')