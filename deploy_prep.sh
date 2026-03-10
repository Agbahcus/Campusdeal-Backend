#!/bin/bash
# Quick deployment preparation script

echo "🚀 Preparing CampusDeal for deployment..."

# 1. Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 2. Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# 3. Check for issues
echo "🔍 Running system checks..."
python manage.py check --deploy

# 4. Show migrations status
echo "📊 Checking migrations..."
python manage.py showmigrations

echo ""
echo "✅ Preparation complete!"
echo ""
echo "Next steps:"
echo "1. Commit and push to GitHub"
echo "2. Deploy on Railway"
echo "3. Run migrations on Railway"
echo "4. Create superuser on Railway"
