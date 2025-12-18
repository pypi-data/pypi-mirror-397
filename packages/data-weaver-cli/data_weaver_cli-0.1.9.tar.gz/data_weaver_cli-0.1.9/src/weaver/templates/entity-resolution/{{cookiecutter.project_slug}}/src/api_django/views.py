from django.http import JsonResponse


def health_check(request):
    """Basic health check endpoint."""
    if request.method == 'GET':
        return JsonResponse({
            'status': 'healthy',
            'message': 'Django API is running'
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)