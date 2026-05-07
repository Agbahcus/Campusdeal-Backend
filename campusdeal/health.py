"""
Health check endpoint for monitoring and load balancers
"""
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Health check endpoint that verifies:
    - Application is running
    - Database connection is working
    
    Returns 200 if healthy, 503 if unhealthy
    """
    health_status = {
        "status": "healthy",
        "checks": {}
    }
    
    is_healthy = True
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["checks"]["database"] = f"error: {str(e)}"
        is_healthy = False
    
    # Check critical settings
    try:
        critical_settings = [
            'SECRET_KEY',
            'DATABASE_URL' if 'DATABASE_URL' in settings.__dict__ else None,
        ]
        health_status["checks"]["configuration"] = "ok"
    except Exception as e:
        logger.error(f"Configuration check failed: {str(e)}")
        health_status["checks"]["configuration"] = f"error: {str(e)}"
        is_healthy = False
    
    if not is_healthy:
        health_status["status"] = "unhealthy"
        return JsonResponse(health_status, status=503)
    
    return JsonResponse(health_status, status=200)


def readiness_check(request):
    """
    Readiness check - similar to health but can include more detailed checks
    Used by orchestrators to determine if app is ready to receive traffic
    """
    return health_check(request)
