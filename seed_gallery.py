import sys
import os

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()

from utils.dynamodb import save_gallery_photo, get_dynamodb_resource
from botocore.exceptions import ClientError

def create_table_if_not_exists():
    dynamodb = get_dynamodb_resource()
    try:
        table = dynamodb.create_table(
            TableName='Gallery_photos',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Creating Gallery_photos table...")
        table.wait_until_exists()
        print("Table created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Table Gallery_photos already exists.")
        else:
            print(f"Error creating table: {e}")

def seed_gallery():
    photos = [
        {
            'image_url': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070&auto=format&fit=crop',
            'title': 'Advanced Cardiac Care',
            'description': 'Modern facilities for comprehensive heart treatment.'
        },
        {
            'image_url': 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?q=80&w=2080&auto=format&fit=crop',
            'title': 'Surgical Excellence',
            'description': 'Precision in every procedure.'
        },
        {
            'image_url': 'https://images.unsplash.com/photo-1581056771107-24ca5f033842?q=80&w=2070&auto=format&fit=crop',
            'title': 'Patient Consultation',
            'description': 'Personalized attention to every heart.'
        },
        {
            'image_url': 'https://images.unsplash.com/photo-1631815589968-fdb09a223b1e?q=80&w=2070&auto=format&fit=crop',
            'title': 'Heart Monitoring',
            'description': 'State-of-the-art diagnostic equipment.'
        },
        {
            'image_url': 'https://images.unsplash.com/photo-1530026405186-ed1f139313f8?q=80&w=2070&auto=format&fit=crop',
            'title': 'Cardiac Rehabilitation',
            'description': 'Supporting your journey to a healthy heart.'
        },
        {
            'image_url': 'https://images.unsplash.com/photo-1551076805-e1869033e561?q=80&w=2070&auto=format&fit=crop',
            'title': 'Expert Team',
            'description': 'Dedicated specialists working for you.'
        }
    ]
    
    for p in photos:
        res = save_gallery_photo(p['image_url'], p['title'], p['description'])
        if res:
            print(f"Saved: {p['title']}")

if __name__ == "__main__":
    create_table_if_not_exists()
    seed_gallery()
