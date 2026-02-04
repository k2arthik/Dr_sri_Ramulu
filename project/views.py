from django.conf import settings 
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from django.shortcuts import render, HttpResponse
from django.views.decorators.http import require_http_methods

from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django_ratelimit.exceptions import Ratelimited
# from blog.models import Blog  # Removed Django model usage

from utils.dynamodb import fetch_gallery_photos, fetch_blogs, fetch_gallery_videos


def rate_limiter_view(request, *args, **kwargs):
    return render(request, 'ratelimit.html', status=429)


def view_404(request, *args, **kwargs):
    return render(request, '404.html', status=404)


def handler_403(request, exception=None):
    if isinstance(exception, Ratelimited):
        return HttpResponse('Sorry too many requests, please wait', status=429)
    return HttpResponseForbidden('Forbidden')


def home_view(request):
    recent_blogs = fetch_blogs(include_drafts=False) # Get all published blogs to handle sorting/limiting in template or here
    photos = fetch_gallery_photos()[:6] # Limit to 6 for the 2x3 grid
    videos = fetch_gallery_videos()[:4] # Limit to 4 for the 2x2 grid (2x2)
    faqs = [
    {
        "question": "Why choose Lux Hospitals?",
        "answer": "Lux Hospitals offers world-class healthcare with advanced technology."
    },
    {
        "question": "What services does Lux Hospitals Hyderabad provide?",
        "answer": "We provide cardiology, neurology, orthopedics, diagnostics, and emergency care."
    },
    {
        "question": "Which hospitals offer personalized and luxurious treatments?",
        "answer": "Lux Hospitals combines personalized treatment with premium patient experience."
    }
]

    context = {
        'recent_blogs': recent_blogs,
        'photos': photos,
        'videos': videos,
        'faqs': faqs
    }
    return render(request, 'home.html', context, status=200)


def service_detail_view(request, service_slug):
    services = {
        'cardiac-imaging': {
            'title': 'Cardiac Imaging',
            'description': 'Advanced cardiac imaging services using state-of-the-art technology for accurate diagnosis and treatment planning.',
            'icon': 'bi-heart-fill'
        },
        'chronic-total-occlusions': {
            'title': 'Chronic Total Occlusions',
            'description': 'Specialized treatment for chronic total occlusions with cutting-edge interventional techniques.',
            'icon': 'bi-heart-pulse'
        },
        'tavr-laa-closure': {
            'title': 'TAVR/LAA Closure',
            'description': 'Transcatheter Aortic Valve Replacement and Left Atrial Appendage Closure procedures.',
            'icon': 'bi-heart-half'
        },
        'interventions-chd': {
            'title': 'Interventions for CHD',
            'description': 'Comprehensive interventions for Congenital Heart Disease in children and adults.',
            'icon': 'bi-heart'
        },
        'coronary-interventions': {
            'title': 'Coronary Interventions',
            'description': 'Advanced coronary intervention procedures for complex cardiovascular conditions.',
            'icon': 'bi-hospital'
        },
        'peripheral-vascular-interventions': {
            'title': 'Peripheral Vascular Interventions',
            'description': 'Minimally invasive procedures to treat blood vessel problems outside the heart.',
            'icon': 'bi-heart-pulse-fill'
        },
        'pacemakers-devices': {
            'title': 'Pacemakers & Devices',
            'description': 'Implantation and management of Pacemakers, ICDs, and CRT devices for heart rhythm disorders.',
            'icon': 'bi-cpu'
        },
    }
    
    service = services.get(service_slug)
    if not service:
        return render(request, '404.html', status=404)
    
    faqs = [
    {
        "question": "Why choose Lux Hospitals?",
        "answer": "Lux Hospitals offers world-class healthcare with advanced technology."
    },
    {
        "question": "What services does Lux Hospitals Hyderabad provide?",
        "answer": "We provide cardiology, neurology, orthopedics, diagnostics, and emergency care."
    },
    {
        "question": "Which hospitals offer personalized and luxurious treatments?",
        "answer": "Lux Hospitals combines personalized treatment with premium patient experience."
    }
]

    
    return render(request, 'service-detail.html', {'service': service,'faqs':faqs, 'service_slug': service_slug}, status=200)


def services_view(request):
    services = [
        {
            'title': 'Cardiac Imaging',
            'description': 'Advanced cardiac imaging services using state-of-the-art technology for accurate diagnosis and treatment planning.',
            'slug': 'cardiac-imaging',
            'icon': 'bi-heart-fill'
        },
        {
            'title': 'Chronic Total Occlusions',
            'description': 'Specialized treatment for chronic total occlusions with cutting-edge interventional techniques.',
            'slug': 'chronic-total-occlusions',
            'icon': 'bi-heart-pulse'
        },
        {
            'title': 'TAVR/LAA Closure',
            'description': 'Transcatheter Aortic Valve Replacement and Left Atrial Appendage Closure procedures.',
            'slug': 'tavr-laa-closure',
            'icon': 'bi-heart-half'
        },
        {
            'title': 'Interventions for CHD',
            'description': 'Comprehensive interventions for Congenital Heart Disease in children and adults.',
            'slug': 'interventions-chd',
            'icon': 'bi-heart'
        },
        {
            'title': 'Coronary Interventions',
            'description': 'Advanced coronary intervention procedures for complex cardiovascular conditions.',
            'slug': 'coronary-interventions',
            'icon': 'bi-hospital'
        },
        {
            'title': 'Peripheral Vascular Interventions',
            'description': 'Minimally invasive procedures to treat blood vessel problems outside the heart.',
            'slug': 'peripheral-vascular-interventions',
            'icon': 'bi-heart-pulse-fill'
        },
        {
            'title': 'Pacemakers & Devices',
            'description': 'Implantation and management of Pacemakers, ICDs, and CRT devices for heart rhythm disorders.',
            'slug': 'pacemakers-devices',
            'icon': 'bi-cpu'
        },
    ]

    faqs = [
    {
        "question": "Why choose Lux Hospitals?",
        "answer": "Lux Hospitals offers world-class healthcare with advanced technology."
    },
    {
        "question": "What services does Lux Hospitals Hyderabad provide?",
        "answer": "We provide cardiology, neurology, orthopedics, diagnostics, and emergency care."
    },
    {
        "question": "Which hospitals offer personalized and luxurious treatments?",
        "answer": "Lux Hospitals combines personalized treatment with premium patient experience. Lorem We provide cardiology, neurology, orthopedics, diagnostics, and emergency care."
    }
    ]
    conts= {
        'services': services,
        'faqs':faqs
    }
    return render(request, 'services.html',conts, status=200)


def awards_view(request):
    return render(request, 'awards.html', status=200)


def about_view(request):
    return render(request, 'about.html', status=200)


def gallery_photos_view(request):
    photos = fetch_gallery_photos()
    return render(request, 'html/gallery_photos.html', {'photos': photos}, status=200)


def gallery_videos_view(request):
    videos = fetch_gallery_videos()
    return render(request, 'html/gallery_videos.html', {'videos': videos}, status=200)