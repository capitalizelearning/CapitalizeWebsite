from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render


def index(request):
    """ Index page view.
    GET:
        Render the index page.
    POST:
        Handle wait-list sign up."""
    if request.method == 'GET':
        return render(request, 'index.html')
    elif request.method == 'POST':
        email = request.POST['email']
        # TODO: Handle sign up
        return redirect('index')
    return HttpResponseNotAllowed(['GET', 'POST'])
