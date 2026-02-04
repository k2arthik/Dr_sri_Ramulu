from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# from .models import Blog  # Removed Django model usage

# from .forms import BlogImageForm  # File not found on disk, commenting out to prevent crash


from utils.decorators import login_required_rest_api
from utils.dynamodb import fetch_blogs, fetch_blog_by_slug

@require_http_methods(['GET'])
def get_blog(request, slug):
    blog = fetch_blog_by_slug(slug)
    if not blog:
        return render(request, '404.html', status=404)

    return render(request, 'html/blog/blog-view.html', {
                                        'blog': blog,
                                    })


@require_http_methods(['GET'])
def list_blogs(request):

    page_number = request.GET.get("page", 1)
    blogs_list = fetch_blogs(include_drafts=False)

    paginator = Paginator(blogs_list, per_page=15)
    page = paginator.get_page(page_number)

    # Calculate elided page range
    page_range = paginator.get_elided_page_range(page_number, on_each_side=2, on_ends=1)
    
    return render(request, 'html/blog/blog-list.html', {
                                                'blogs': page,
                                                'page_range': page_range,
                                            })


BLOG_PERMISSIONS = ['blog.add_blog', 'blog.change_blog']


@login_required_rest_api
@require_http_methods(['POST'])
def upload_image(request):
    """
    Image upload temporarily disabled as BlogImageForm is missing.
    """
    return JsonResponse({'error': 'Image upload is currently unavailable'}, status=501)
