
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import JsonResponse

from celery.result import AsyncResult
from .tasks import generate_images_parallel
from .models import GeneratedImage

logger = logging.getLogger(__name__)

@login_required
def home(request):
    if request.method == 'POST':
        prompts = request.POST.getlist('prompt')
        if prompts:
            try:
                task = generate_images_parallel.delay(prompts, request.user.id)
                image_urls = task.get()  # Wait for all images to be generated
                logger.info(f"Generated {len(image_urls)} images for user {request.user.id}")
                messages.success(request, f"Successfully generated {len(image_urls)} images.")
            except Exception as e:
                logger.error(f"Failed to generate images for user {request.user.id}: {str(e)}")
                # messages.error(request, 'Failed to generate images. Please try again.')
            return redirect('home')
    
    images = GeneratedImage.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'image_generator/home.html', {'images': images})

@login_required
def check_image_status(request):
    latest_images = GeneratedImage.objects.filter(user=request.user).order_by('-created_at')[:3]
    new_images = [
        {
            'url': img.image_url,
            'prompt': img.prompt,
            'created_at': img.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for img in latest_images
    ]
    return JsonResponse({'images': new_images})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    # Add Bootstrap classes to form fields
    for field in form.visible_fields():
        field.field.widget.attrs['class'] = 'form-control'
    
    return render(request, 'image_generator/signup.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'image_generator/login.html', {'form': form})


def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')