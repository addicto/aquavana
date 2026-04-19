from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from pages.models import NotifySignup


def home(request):
    return render(request, 'pages/home.html', {})


@csrf_exempt
@require_POST
def notify_signup(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        if not email:
            return JsonResponse({'error': 'Email is required.'}, status=400)
        _, created = NotifySignup.objects.get_or_create(email=email)
        if created:
            return JsonResponse({'message': 'Signed up successfully.'})
        return JsonResponse({'message': 'Already registered.'})
    except Exception:
        return JsonResponse({'error': 'Invalid request.'}, status=400)
