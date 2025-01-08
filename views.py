from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import subprocess
import shutil
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import *
from .forms import *
from datetime import datetime


def homepage_view(request):
    return render(request, 'amatakpro/homepage.html')

@login_required
def admin_settings_view(request):
    settings = AdminSettings.objects.first()
    if request.method == 'POST':
        form = AdminSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin settings updated successfully!")
            return redirect('admin_settings')
    else:
        form = AdminSettingsForm(instance=settings)
    return render(request, 'amatakpro/admin_settings.html', {'form': form})

#@login_required
#def create_django_app(request):
    #if request.method == 'POST':
        #form = AppNameForm(request.POST)
       # if form.is_valid():
           # app_name = form.cleaned_data['app_name']
            #os.system(f'django-admin startapp {app_name}')
            #return HttpResponse(f'App {app_name} created successfully!')
    #else:
        #form = AppNameForm()
    #return render(request, 'amatakpro/create_app.html', {'form': form})

#def create_django_app(app_name):
    #"""Create a new Django app using the startapp command."""
    #subprocess.run(['python', 'manage.py', 'startapp', app_name])
    
#def create_django_app(app_name):
    #"""Create a new Django app using the startapp command."""
    ##app_directory = os.path.join('', app_name)  # Update this to the appropriate directory
    #subprocess.run(['python', 'manage.py', 'startapp', app_name],) # cwd=app_directory
    



@login_required
def user_profile_view(request):
    user = request.user
    return render(request, 'amatakpro/user_profile.html', {'user': user})

@login_required
def update_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'amatakpro/update_profile.html', {'form': form})

@login_required
def user_bills_view(request):
    bills = []  # Placeholder for user bills
    return render(request, 'amatakpro/user_bills.html', {'bills': bills})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed successfully!")
            return redirect('user_profile')
        else:
            messages.error(request, "Error changing password. Please try again.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'amatakpro/change_password.html', {'form': form})

def user_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('homepage')

def user_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have logged in successfully!")
            return redirect('user_profile')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = AuthenticationForm()
    return render(request, 'amatakpro/login.html', {'form': form})


def password_reset_view(request):
    return render(request, 'amatakpro/password_reset.html')


def create_account_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Error creating account. Please check the form.")
    else:
        form = UserCreationForm()
    return render(request, 'amatakpro/create_account.html', {'form': form})

def download_app_view(request, app_name):
    app_path = os.path.join('', app_name)  # Update path as needed
    if os.path.exists(app_path):
        response = HttpResponse(open(app_path, 'rb').read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename={app_name}.zip'  # Ensure file is zipped or in a downloadable format
        return response
    else:
        messages.error(request, "App not found.")
        return redirect('app_list')
    


###update

@login_required
def create_django_app(request):
    if request.method == 'POST':
        form = AppNameForm(request.POST)
        if form.is_valid():
            app_name = form.cleaned_data['app_name']
            os.system(f'django-admin startapp {app_name}')
            CreatedApp.objects.create(name=app_name)
            return redirect('app_list')
    else:
        form = AppNameForm()
    return render(request, 'amatakpro/create_app.html', {'form': form})

def get_directory_contents(path):
    directory_contents = []
    if os.path.exists(path):
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            entry_stats = os.stat(entry_path)
            entry_details = {
                'name': entry,
                'is_directory': os.path.isdir(entry_path),
                'size': entry_stats.st_size,
                'created_time': datetime.fromtimestamp(entry_stats.st_ctime),
            }
            directory_contents.append(entry_details)
    return directory_contents



@login_required
def app_list_view(request):
    apps = CreatedApp.objects.all()
    app_details = []
    root_dir = settings.BASE_DIR

    for app in apps:
        app_name = app.name
        app_path = os.path.join(root_dir, app_name)
        if os.path.exists(app_path):
            app_entries = get_directory_contents(app_path)
            app_details.append({'app_name': app_name, 'entries': app_entries})

    return render(request, 'amatakpro/app_list.html', {'app_details': app_details})

@login_required
def update_app_view(request, id):
    app = get_object_or_404(CreatedApp, id=id)
    if request.method == 'POST':
        form = UpdateAppForm(request.POST, instance=app)
        if form.is_valid():
            new_name = form.cleaned_data['name']
            old_name = app.name
            
            # Rename the directory if the name has changed
            if old_name != new_name:
                old_path = os.path.join(settings.BASE_DIR, old_name)
                new_path = os.path.join(settings.BASE_DIR, new_name)
                os.rename(old_path, new_path)
                app.name = new_name
            
            app.save()
            return redirect('app_list')
    else:
        form = UpdateAppForm(instance=app)
    return render(request, 'amatakpro/update_app.html', {'form': form, 'app': app})

@login_required
def delete_app_view(request, id):
    app = get_object_or_404(CreatedApp, id=id)
    if request.method == 'POST':
        app_name = app.name
        app_folder_path = os.path.join(settings.BASE_DIR, app_name)

        # Delete the app directory
        if os.path.exists(app_folder_path):
            shutil.rmtree(app_folder_path)
        app.delete()
        return redirect('app_list')
    return render(request, 'amatakpro/delete_app.html', {'app': app})

@login_required
def activate_app_view(request):
    apps = CreatedApp.objects.all()
    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        app = get_object_or_404(CreatedApp, id=app_id)
        
        # Logic to activate the app
        app_name = app.name
        print(f"Activating app: {app_name}")
        return redirect('app_list')
    return render(request, 'amatakpro/app_activate_template.html', {'apps': apps})

@login_required
def add_to_settings(request):
    if request.method == 'POST':
        app_name = request.POST.get('app_name')
        settings_file_path = os.path.join(settings.BASE_DIR, 'settings.py')

        # Modify the settings.py file
        with open(settings_file_path, 'r') as file:
            lines = file.readlines()

        installed_apps_line_index = next(i for i, line in enumerate(lines) if line.startswith("INSTALLED_APPS = ["))
        
        # Add app name to INSTALLED_APPS if not already present
        if app_name not in lines[installed_apps_line_index]:
            lines.insert(installed_apps_line_index + 1, f"    '{app_name}',\n")
            print(f"Updated INSTALLED_APPS with: {app_name}")
        
        # Write back the modified settings.py
        with open(settings_file_path, 'w') as file:
            file.writelines(lines)

        return redirect('app_list')

    return render(request, 'amatakpro/add_to_settings.html')


@login_required
def edit_file_view(request, app_name, file_name):
    app_path = os.path.join(settings.BASE_DIR, app_name, file_name)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        with open(app_path, 'w') as file:
            file.write(content)
        return redirect('app_list')

    with open(app_path, 'r') as file:
        content = file.read()

    return render(request, 'amatakpro/edit_file.html', {'app_name': app_name, 'file_name': file_name, 'content': content})
