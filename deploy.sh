#!/bin/bash
# Deployment script for CampusDeal Backend
# Run this after deploying to production

set -e  # Exit on error

echo "🚀 Starting deployment tasks..."

# Run database migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Create default categories if they don't exist
echo "📂 Setting up default categories..."
python manage.py shell << EOF
from marketplace.models import ItemCategory
categories = ['Electronics', 'Books', 'Clothing', 'Furniture', 'Phones', 'Laptops', 'Accessories', 'Other']
for cat in categories:
    ItemCategory.objects.get_or_create(name=cat)
print(f"✅ Created/verified {len(categories)} categories")
EOF

# Collect static files (if not done in Dockerfile)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Deployment tasks completed successfully!"
