from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate


def login_(request):
    ctx={}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        auth_user = authenticate(username=username, password=password)
        if auth_user:
            login(request, auth_user)
            return redirect('/')
        else:
            ctx['err'] = 'Неправильный логин или пароль'
    return render(request, 'auth/login.html', ctx)


def logout_(request):
    logout(request)
    return redirect('/')