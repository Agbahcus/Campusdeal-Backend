@echo off
echo 🚀 Preparing CampusDeal for deployment...
echo.

echo 📦 Installing dependencies...
pip install -r requirements.txt
echo.

echo 📁 Collecting static files...
python manage.py collectstatic --noinput
echo.

echo 🔍 Running system checks...
python manage.py check --deploy
echo.

echo 📊 Checking migrations...
python manage.py showmigrations
echo.

echo ✅ Preparation complete!
echo.
echo Next steps:
echo 1. Commit and push to GitHub
echo 2. Deploy on Railway
echo 3. Run migrations on Railway
echo 4. Create superuser on Railway
echo.
pause
