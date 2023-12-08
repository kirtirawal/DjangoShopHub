from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, LoginForm
from django.contrib.auth.decorators import login_required


def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')

    context = {'form': form}
    return render(request, 'accounts/login.html', context)


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
