# generates sitemaps for SEO

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from utils.dynamodb import fetch_blogs

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        # Fetching published blogs from DynamoDB
        return fetch_blogs(include_drafts=False)

    def lastmod(self, item):
        import datetime
        dt_str = item.get('datetime')
        if dt_str:
            try:
                # Assuming datetime is stored in ISO format
                return datetime.datetime.fromisoformat(dt_str)
            except (ValueError, TypeError):
                return None
        return None
    
    def location(self, item):
        # Uses the slug from the DynamoDB item
        return reverse('get-blog', kwargs={'slug': item.get('slug')})

