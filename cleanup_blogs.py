import boto3
import os
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()

def cleanup_blogs():
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    table = dynamodb.Table('Blogs')
    items = table.scan().get('Items', [])
    
    placeholders = {
        'Cardiology': 'https://plus.unsplash.com/premium_photo-1673322194344-96ae4b2c1294?q=80&w=2070&auto=format&fit=crop',
        'Lifestyle': 'https://plus.unsplash.com/premium_photo-1663852297267-827c73e7529e?q=80&w=2070&auto=format&fit=crop',
        'Technology': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070&auto=format&fit=crop',
        'General': 'https://plus.unsplash.com/premium_photo-1673322194344-96ae4b2c1294?q=80&w=2070&auto=format&fit=crop'
    }

    print(f"Auditing {len(items)} items...")
    count = 0
    for item in items:
        updated = False
        
        # Ensure thumbnail exists and is a valid-looking URL
        thumbnail = item.get('thumbnail', '')
        if not thumbnail or not thumbnail.startswith('http'):
            item['thumbnail'] = placeholders.get(item.get('category', 'General'), placeholders['General'])
            updated = True
        
        # Ensure slug exists
        if 'slug' not in item:
            from django.template.defaultfilters import slugify
            item['slug'] = slugify(item.get('title', 'untitled-blog'))
            updated = True
            
        # Ensure draft exists
        if 'draft' not in item:
            item['draft'] = False
            updated = True
            
        if updated:
            print(f"Updating blog: {item.get('title')} (ID: {item.get('id')})")
            table.put_item(Item=item)
            count += 1
            
    print(f"Cleanup finished. {count} items updated.")

if __name__ == "__main__":
    cleanup_blogs()
