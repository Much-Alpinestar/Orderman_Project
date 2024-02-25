from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import UserForm


def home(request):
    return render(request, 'authentication/index.html',{'users':User.objects.all()})

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Debugging-Ausgabe für Formulardaten
            print("Formulardaten:", form.cleaned_data)

            username = form.cleaned_data['username']
            fname = form.cleaned_data['fname']
            lname = form.cleaned_data['lname']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            is_superuser = form.cleaned_data['is_superuser']

            # Überprüfen, ob der Benutzername bereits verwendet wird
            if User.objects.filter(username=username).exists():
                messages.error(request, "Benutzername existiert bereits.")
                return redirect('create_user')

            # Überprüfen, ob die E-Mail-Adresse bereits verwendet wird
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email existiert bereits.")
                return redirect('create_user')

            # Benutzerkonto erstellen
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            if is_superuser:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                messages.success(request, 'Superuser wurde erfolgreich erstellt.')
            else:
                user.save()
                messages.success(request, 'Benutzer wurde erfolgreich erstellt.')
        
            return redirect('home')
        else:
            # Debugging-Ausgabe für Formularfehler
            print("Formularfehler:", form.errors)
    else:
        form = UserForm()
    return render(request, 'authentication/create_user.html', {'form': form})


def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('order_index')
        else:
            messages.error(request, 'Benutzername oder Passwort sind falsch.')
            return redirect('login')

    return render(request, 'authentication/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'Sie wurden erfolgreich abgemeldet.')
    return redirect('login')
