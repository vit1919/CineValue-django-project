from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django_ratelimit.decorators import ratelimit

from ..forms import SignUpForm


@ratelimit(key='ip', rate='5/m', block=True)
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registered!')
            return redirect('/')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})
