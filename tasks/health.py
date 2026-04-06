from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis


def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Checks database, cache, and returns system status.
    """
    status = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown',
    }
    http_status = 200

    try:
        connection.ensure_connection()
        status['database'] = 'connected'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
        http_status = 503

    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            status['cache'] = 'connected'
        else:
            status['cache'] = 'error: cache test failed'
            status['status'] = 'degraded'
    except Exception as e:
        status['cache'] = f'error: {str(e)}'
        status['status'] = 'degraded'

    return JsonResponse(status, status=http_status)

