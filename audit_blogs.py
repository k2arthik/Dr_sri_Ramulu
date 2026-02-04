import boto3
import os
import json
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()

def audit_blogs():
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    table = dynamodb.Table('Blogs')
    response = table.scan()
    items = response.get('Items', [])
    
    print(f"Total Blogs: {len(items)}")
    for i, item in enumerate(items):
        print(f"--- Blog {i+1} ---")
        print(f"ID: {item.get('id')}")
        print(f"Title: {item.get('title')}")
        print(f"Thumbnail URL: {item.get('thumbnail')}")
        print(f"Keys present: {list(item.keys())}")

if __name__ == "__main__":
    audit_blogs()
