import boto3
import os
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()

def check_dynamodb():
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    table = dynamodb.Table('Blogs')
    response = table.scan()
    items = response.get('Items', [])
    
    print(f"Found {len(items)} items in table 'Blogs'.")
    for i, item in enumerate(items):
        print(f"\nItem {i+1}:")
        for key, value in item.items():
            if key == 'body':
                print(f"  {key}: [Body content omitted, length: {len(value)}]")
            else:
                print(f"  {key}: {value}")

if __name__ == "__main__":
    check_dynamodb()
