
from django.conf import settings

from django.shortcuts import redirect
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from django.views.generic import TemplateView

from django.contrib import admin
from django.urls import path

from django.urls import path, include, re_path

from .views import (rate_limiter_view, view_404, 
                        handler_403, home_view, service_detail_view, awards_view, about_view, services_view,
                        gallery_photos_view, gallery_videos_view) #subscribe_view
from inquiry.admin_views import (admin_dashboard_view, admin_enquiry_list_view, 
                                admin_appointment_list_view, export_excel_view,
                                admin_blog_list_view, admin_blog_edit_view,
                                admin_gallery_photos_view, admin_gallery_videos_view)

from .sitemaps import StaticSitemap
from blog.sitemaps import BlogSitemap

handler404 = view_404

handler403 = handler_403

admin.site.site_header = 'Admin panel'           
admin.site.index_title = 'Site Admin'              
admin.site.site_title = 'Admin site'
admin.site.site_url = "" 


sitemap_dict = {'sitemaps': {'static': StaticSitemap, 'blog': BlogSitemap}}


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('user/', include('user.urls')),
    path('blog/', include('blog.urls')),
    path('contact-us/', include('inquiry.urls')),
    
    # Admin Dashboard (Direct Mapping)
    path('admin-dashboard/', include([
        path('', admin_dashboard_view, name='admin_dashboard'),
        path('enquiries/', admin_enquiry_list_view, name='admin_enquiries'),
        path('appointments/', admin_appointment_list_view, name='admin_appointments'),
        path('blogs/', admin_blog_list_view, name='admin_blogs'),
        path('blogs/edit/<str:blog_id>/', admin_blog_edit_view, name='admin_blog_edit'),
        path('gallery/photos/', admin_gallery_photos_view, name='admin_gallery_photos'),
        path('gallery/videos/', admin_gallery_videos_view, name='admin_gallery_videos'),
        path('export/<str:type>/', export_excel_view, name='admin_export'),
    ])),
    

    path('sitemap.xml', sitemap, sitemap_dict, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
    path('ratelimit-error/', rate_limiter_view, name='ratelimit-error'),

    # add new path here

    path('', home_view, name='home'),
    path('services/', services_view, name='services'),
    path('about/', about_view, name='about'),
    path('services/<str:service_slug>/', service_detail_view, name='service-detail'),
    path('awards/', awards_view, name='awards'),
    path('gallery/photos/', gallery_photos_view, name='gallery-photos'),
    path('gallery/videos/', gallery_videos_view, name='gallery-videos'),

    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
   urlpatterns +=  []

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
   
urlpatterns += [ re_path(r'^.*/$', view_404, name='page_not_found'),]