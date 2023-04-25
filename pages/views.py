from django.shortcuts import render


# Create your views here.
def home(request):
    data = {
    }
    return render(request, 'pages/home.html', data)
