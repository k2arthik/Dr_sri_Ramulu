"""
Migration script to convert existing video_url records to video_id format.
Run this once to migrate existing data in DynamoDB.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from utils.dynamodb import fetch_gallery_videos, get_dynamodb_resource
from utils.youtube_utils import extract_youtube_id


def migrate_video_records():
    """
    Migrate all video records from video_url to video_id format.
    """
    print("Starting video migration...")
    
    # Fetch all existing videos
    videos = fetch_gallery_videos()
    
    if not videos:
        print("No videos found to migrate.")
        return
    
    print(f"Found {len(videos)} videos to migrate.")
    
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('Gallery_videos')
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for video in videos:
        video_id_field = video.get('id')
        video_url = video.get('video_url', '')
        
        # Skip if already has video_id field
        if 'video_id' in video and video.get('video_id'):
            print(f"  ✓ Skipping {video_id_field} - already has video_id")
            skipped_count += 1
            continue
        
        # Extract YouTube ID from URL
        youtube_id = extract_youtube_id(video_url)
        
        if not youtube_id:
            print(f"  ✗ Error: Could not extract ID from {video_url}")
            error_count += 1
            continue
        
        try:
            # Update the record with video_id field
            table.update_item(
                Key={'id': video_id_field},
                UpdateExpression='SET video_id = :vid',
                ExpressionAttributeValues={
                    ':vid': youtube_id
                }
            )
            print(f"  ✓ Migrated {video_id_field}: {video_url} → {youtube_id}")
            migrated_count += 1
            
        except Exception as e:
            print(f"  ✗ Error updating {video_id_field}: {e}")
            error_count += 1
    
    print("\n" + "="*50)
    print("Migration Summary:")
    print(f"  Total videos: {len(videos)}")
    print(f"  Migrated: {migrated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")
    print("="*50)


if __name__ == '__main__':
    confirm = input("This will modify video records in DynamoDB. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        migrate_video_records()
    else:
        print("Migration cancelled.")
