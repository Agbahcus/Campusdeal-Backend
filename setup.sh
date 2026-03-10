#!/bin/bash

echo "🚀 CampusDeal Backend Setup"
echo "============================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "✅ .env created. Please edit it with your credentials."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running migrations..."
python manage.py migrate

# Create superuser prompt
echo ""
echo "👤 Create superuser account?"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python manage.py createsuperuser
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create media directories
echo "📂 Creating media directories..."
mkdir -p media/profile_pics
mkdir -p media/item_images
mkdir -p media/hostel_images
mkdir -p media/refund_evidence

# Run system check
echo "🔍 Running system check..."
python manage.py check

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit .env with your API keys (Paystack, Termii)"
echo "2. Run: python manage.py runserver"
echo "3. Access admin: http://127.0.0.1:8000/admin/"
echo "4. Test API: http://127.0.0.1:8000/api/"
echo ""
echo "📚 Read DEPLOYMENT_GUIDE.md for production deployment"
