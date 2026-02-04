import boto3
import uuid
import datetime
import hashlib
import time
from django.conf import settings
from botocore.exceptions import ClientError
from django.template.defaultfilters import slugify

def get_dynamodb_resource():
    return boto3.resource(
        'dynamodb',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

def get_expiry_timestamp(days=2):
    """Returns a timestamp for TTL (seconds since epoch)."""
    return int(time.time() + (days * 24 * 60 * 60))

def increment_daily_counter(counter_name):
    """Increments a daily atomic counter in the 'Counters' table or a specific item."""
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('Appointments') # Reusing Appointments table for counters or better a separate one?
    # Actually, let's use a "Counters" partition in the Appointments table if we don't want to create new tables.
    # Partition PK: 'id', let's use 'COUNTER#YYYYMMDD'
    
    today = datetime.datetime.now().strftime('%Y%m%d')
    counter_id = f"COUNTER#{today}#{counter_name}"
    
    try:
        response = table.update_item(
            Key={'id': counter_id},
            UpdateExpression="ADD #count :inc",
            ExpressionAttributeNames={'#count': 'count_value'},
            ExpressionAttributeValues={':inc': 1},
            ReturnValues="UPDATED_NEW"
        )
        return response['Attributes']['count_value']
    except Exception as e:
        print(f"Counter Error: {e}")
        return 0

def save_patient_to_dynamodb(data):
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('Patients')
    
    # Duplicate Detection Hash
    email = str(data.get('email', '')).lower()
    description = str(data.get('description', data.get('message', ''))).strip()
    content_hash = hashlib.md5(f"{email}{description}".encode()).hexdigest()
    
    # Check for duplicates in the last 10 mins? 
    # High complexity if we query first. Let's just use UUID but add the hash.
    # Alternative: Use hash as PK to block duplicates, but user might want to submit different ones.
    
    expiry = get_expiry_timestamp(2) # 2 days TTL
    
    item = {
        'id': str(uuid.uuid4()),
        'name': str(data.get('name')),
        'email': email,
        'phone': str(data.get('phone')),
        'description': description,
        'content_hash': content_hash,
        'status': 'unresolved', # For admin filtering
        'created_at': datetime.datetime.now().isoformat(),
        'expiry_timestamp': expiry
    }
    
    table.put_item(Item=item)
    increment_daily_counter('inquiries')
    return item

def save_appointment_to_dynamodb(data):
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('Appointments')
    
    date_str = str(data.get('date')) # YYYY-MM-DD
    time_slot = str(data.get('time_slot'))
    clean_date = date_str.replace('-', '')
    
    # Atomic collision prevention using a secondary attribute or a dedicated slot item
    # Since 'id' is our PK and we want 'YYYYMMDD-N', it doesn't prevent same slot at different ID.
    # We should use a 'slot_key' like 'SLOT#20260125#10:30AM'
    
    slot_id = f"SLOT#{clean_date}#{time_slot.replace(' ', '')}"
    
    # We need to ensure THIS SLOT is not taken.
    # But the table PK is 'id'. We could use 'id' as the slot_id?
    # NO, user wants 'id' as 'YYYYMMDD-1'.
    
    # Sequential ID generation logic
    counter = 1
    max_retries = 50
    expiry = get_expiry_timestamp(3) # 3 days TTL
    
    while counter <= max_retries:
        new_id = f"{clean_date}-{counter}"
        
        item = {
            'id': new_id,
            'name': str(data.get('name')),
            'email': str(data.get('email')),
            'phone': str(data.get('phone')),
            'service': str(data.get('service')),
            'date': date_str,
            'time_slot': time_slot,
            'slot_key': slot_id, # For collision check if we had a GSI or different PK
            'status': 'requested', # requested, confirmed, cancelled
            'admin_notes': '',
            'created_at': datetime.datetime.now().isoformat(),
            'expiry_timestamp': expiry
        }
        
        try:
            # Atomic check: Is this ID taken? (Sequential ID check)
            table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(id)'
            )
            # Slot collision check is harder without GSI or knowing existing IDs.
            # Best way: Add a separate item for the slot to "lock" it.
            try:
                table.put_item(
                    Item={'id': slot_id, 'appointment_id': new_id},
                    ConditionExpression='attribute_not_exists(id)'
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    # Slot already booked! Cleanup the sequential item and raise.
                    table.delete_item(Key={'id': new_id})
                    raise Exception(f"Slot {time_slot} is already booked for this date.")
                else:
                    raise e
            
            increment_daily_counter('appointments')
            return item
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                counter += 1
                continue
            else:
                raise e
                
    raise Exception("Could not generate a unique ID for this date after multiple attempts.")

def fetch_all_inquiries():
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('Patients')
    # Filter out counters if they are there, or just scan
    response = table.scan()
    items = response.get('Items', [])
    # Sort by created_at desc
    items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return items

def fetch_all_appointments(date_filter=None):
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('Appointments')
    response = table.scan()
    items = response.get('Items', [])
    # Filter out SLOT# and COUNTER# items
    appointments = [i for i in items if not i['id'].startswith('SLOT#') and not i['id'].startswith('COUNTER#')]
    
    if date_filter:
        appointments = [a for a in appointments if a.get('date') == date_filter]
    
    # Sort by id (Sequential)
    appointments.sort(key=lambda x: x.get('id', ''))
    return appointments

def update_item_status(table_name, item_id, status, notes=None):
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(table_name)
    update_expr = "SET #s = :s"
    attr_names = {"#s": "status"}
    attr_vals = {":s": status}
    
    if notes is not None:
        update_expr += ", admin_notes = :n"
        attr_vals[":n"] = notes
        
    table.update_item(
        Key={'id': item_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_vals
    )
    
    # If appointment is cancelled, free up the slot lock
    if table_name == 'Appointments' and status == 'cancelled':
        item = table.get_item(Key={'id': item_id}).get('Item')
        if item and 'slot_key' in item:
            try:
                table.delete_item(Key={'id': item['slot_key']})
            except:
                pass

def fetch_taken_slots(date_str):
    """Returns a list of time slots already booked for a specific date."""
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('Appointments')
    clean_date = date_str.replace('-', '')
    
    # We search for SLOT#YYYYMMDD#... items
    from boto3.dynamodb.conditions import Key
    response = table.scan(
        FilterExpression=Key('id').begins_with(f"SLOT#{clean_date}")
    )
    items = response.get('Items', [])
    # Extract time from SLOT#YYYYMMDD#TIME
    taken = []
    prefix = f"SLOT#{clean_date}#"
    for i in items:
        # i['id'] = SLOT#20260125#10:30AM
        time_part = i['id'].replace(prefix, '')
        # Re-add space for matching comparison? 10:30AM -> 10:30 AM
        # Our template uses space. Dynamo saved without space in slot_id.
        taken.append(time_part)
    return taken

def delete_dynamo_item(table_name, item_id):
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(table_name)
    
    # If it's an appointment, we should also free up the slot
    if table_name == 'Appointments' and not item_id.startswith('SLOT#'):
        item = table.get_item(Key={'id': item_id}).get('Item')
        if item and 'slot_key' in item:
            table.delete_item(Key={'id': item['slot_key']})
            
    table.delete_item(Key={'id': item_id})

def process_inquiry(data):
    """Unified logic to save to DynamoDB and send email for inquiries."""
    # Duplicate Detection
    email = str(data.get('email', '')).lower()
    description = str(data.get('description', data.get('message', ''))).strip()
    content_hash = hashlib.md5(f"{email}{description}".encode()).hexdigest()
    
    # Check if this hash was submitted recently (within 10 mins)
    # Simple check: Fetch all and see if hash matches in last X mins
    # This is a bit expensive for Scan, but for low volume it's fine.
    # A true solution would use a GSI on content_hash.
    
    inquiries = fetch_all_inquiries()
    recent_dup = False
    now = datetime.datetime.now()
    for i in inquiries:
        if i.get('content_hash') == content_hash:
             created_at = datetime.datetime.fromisoformat(i.get('created_at'))
             if (now - created_at).total_seconds() < 600:
                  recent_dup = True
                  break
    
    if recent_dup:
        print("Duplicate inquiry detected. Skipping email/save.")
        return None

    item = save_patient_to_dynamodb(data)
    
    # Send Email...
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = 'New Patient Inquiry'
        message = f"Hi {data.get('name')},\n\nWe received your inquiry. We will contact you at {data.get('phone')} shortly."
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [data.get('email')],
            fail_silently=False
        )
        
        # Email to Admin
        admin_message = f"New Inquiry:\nID: {item['id']}\nName: {data.get('name')}\nEmail: {data.get('email')}\nPhone: {data.get('phone')}\nMessage: {data.get('description', data.get('message', ''))}"
        send_mail(
            'New Inquiry Received',
            admin_message,
            settings.DEFAULT_FROM_EMAIL,
            ['g12113251a@gmail.com'],
            fail_silently=False
        )
    except Exception as e:
        print(f"CRITICAL EMAIL ERROR: {e}")


def fetch_gallery_photos():
    """Fetches all items from the Gallery_photos table."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Gallery_photos')
        response = table.scan()
        items = response.get('Items', [])
        # Sort by created_at desc if available
        items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return items
    except Exception as e:
        print(f"DynamoDB Gallery Fetch Error: {e}")
        return []


def save_gallery_photo(image_url, title="", description=""):
    """Saves a new photo record to the Gallery_photos table."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Gallery_photos')
        item = {
            'id': str(uuid.uuid4()),
            'image_url': image_url,
            'title': title,
            'description': description,
            'created_at': datetime.datetime.now().isoformat(),
        }
        table.put_item(Item=item)
        return item
    except Exception as e:
        print(f"DynamoDB Gallery Save Error: {e}")
        return None


def fetch_blogs(include_drafts=False):
    """Fetches all blogs from the Blogs table."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Blogs')
        response = table.scan()
        items = response.get('Items', [])
        
        if not include_drafts:
            items = [i for i in items if not i.get('draft', True)]
            
        # Sort by datetime desc
        items.sort(key=lambda x: x.get('datetime', ''), reverse=True)
        return items
    except Exception as e:
        print(f"DynamoDB Blog Fetch Error: {e}")
        return []


def fetch_blog_by_slug(slug):
    """Fetches a specific blog by its slug."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Blogs')
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Key('slug').eq(slug)
        )
        items = response.get('Items', [])
        return items[0] if items else None
    except Exception as e:
        print(f"DynamoDB Blog Slug Fetch Error: {e}")
        return None

def fetch_blog_by_id(blog_id):
    """Fetches a specific blog by its ID."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Blogs')
        response = table.get_item(Key={'id': blog_id})
        return response.get('Item')
    except Exception as e:
        print(f"DynamoDB Blog ID Fetch Error: {e}")
        return None


def save_blog(data):
    """Saves or updates a blog in the Blogs table."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Blogs')
        
        # Ensure we have an ID
        blog_id = data.get('id') or data.get('blog_id') or str(uuid.uuid4())
        
        item = {
            'id': blog_id,
            'title': data.get('title', ''),
            'slug': data.get('slug') or slugify(data.get('title', '')),
            'body': data.get('body', ''),
            'thumbnail': data.get('thumbnail', ''),
            'draft': data.get('draft', True),
            'datetime': data.get('datetime') or datetime.datetime.now().isoformat(),
            'meta_description': data.get('meta_description', ''),
            'category': data.get('category', 'General'),
            'updated_at': datetime.datetime.now().isoformat(),
        }
        
        table.put_item(Item=item)
        return item
    except Exception as e:
        print(f"DynamoDB Blog Save Error: {e}")
        return None

def delete_blog(blog_id):
    """Deletes a blog from the Blogs table."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Blogs')
        table.delete_item(Key={'id': blog_id})
        return True
    except Exception as e:
        print(f"DynamoDB Blog Delete Error: {e}")
        return False

def delete_gallery_photo(photo_id):
    """Deletes a photo from the Gallery_photos table."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Gallery_photos')
        table.delete_item(Key={'id': photo_id})
        return True
    except Exception as e:
        print(f"DynamoDB Gallery Photo Delete Error: {e}")
        return False

def fetch_gallery_videos():
    """Fetches all items from the Gallery_videos table."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Gallery_videos')
        response = table.scan()
        items = response.get('Items', [])
        items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return items
    except Exception as e:
        print(f"DynamoDB Gallery Video Fetch Error: {e}")
        return []

def save_gallery_video(video_id, title="", description="", thumbnail_url=""):
    """Saves a new video record to the Gallery_videos table using video_id.
    
    Args:
        video_id (str): YouTube video ID (11 characters)
        title (str): Optional video title
        description (str): Optional video description
        thumbnail_url (str): Optional custom thumbnail URL (auto-generated if empty)
    """
    try:
        from utils.youtube_utils import validate_youtube_id, get_youtube_thumbnail_url
        
        # Validate video ID
        if not validate_youtube_id(video_id):
            print(f"Invalid YouTube video ID: {video_id}")
            return None
        
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Gallery_videos')
        
        # Auto-generate thumbnail if not provided
        if not thumbnail_url:
            thumbnail_url = get_youtube_thumbnail_url(video_id, quality='maxresdefault')
        
        item = {
            'id': str(uuid.uuid4()),
            'video_id': video_id,
            'title': title,
            'description': description,
            'thumbnail_url': thumbnail_url,
            'created_at': datetime.datetime.now().isoformat(),
        }
        table.put_item(Item=item)
        return item
    except Exception as e:
        print(f"DynamoDB Gallery Video Save Error: {e}")
        return None

def delete_gallery_video(video_id):
    """Deletes a video from the Gallery_videos table."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table('Gallery_videos')
        table.delete_item(Key={'id': video_id})
        return True
    except Exception as e:
        print(f"DynamoDB Gallery Video Delete Error: {e}")
        return False
