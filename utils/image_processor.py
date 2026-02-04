"""
Image processing utility for gallery uploads.
Handles image resizing, optimization, and validation.
"""
import os
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings


class ImageProcessor:
    """Process and optimize uploaded images."""
    
    # Resolution limits
    PHOTO_MAX_WIDTH = 1920
    PHOTO_MAX_HEIGHT = 1080
    THUMBNAIL_MAX_WIDTH = 1280
    THUMBNAIL_MAX_HEIGHT = 720
    
    # Quality settings
    JPEG_QUALITY = 85
    
    # Allowed formats
    ALLOWED_FORMATS = ['JPEG', 'JPG', 'PNG', 'WEBP']
    
    @staticmethod
    def process_image(uploaded_file, image_type='photo'):
        """
        Process an uploaded image file.
        
        Args:
            uploaded_file: Django UploadedFile object
            image_type: 'photo' or 'thumbnail'
            
        Returns:
            Processed image file object
        """
        # Open the image
        img = Image.open(uploaded_file)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Determine max dimensions
        if image_type == 'thumbnail':
            max_width = ImageProcessor.THUMBNAIL_MAX_WIDTH
            max_height = ImageProcessor.THUMBNAIL_MAX_HEIGHT
        else:
            max_width = ImageProcessor.PHOTO_MAX_WIDTH
            max_height = ImageProcessor.PHOTO_MAX_HEIGHT
        
        # Resize if necessary
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=ImageProcessor.JPEG_QUALITY, optimize=True)
        output.seek(0)
        
        # Generate unique filename
        ext = 'jpg'
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        
        # Create new InMemoryUploadedFile
        processed_file = InMemoryUploadedFile(
            output,
            'ImageField',
            unique_name,
            'image/jpeg',
            output.getbuffer().nbytes,
            None
        )
        
        return processed_file, unique_name
    
    @staticmethod
    def validate_image(uploaded_file):
        """
        Validate uploaded image file.
        
        Returns:
            (is_valid, error_message)
        """
        try:
            img = Image.open(uploaded_file)
            
            # Check format
            if img.format not in ImageProcessor.ALLOWED_FORMATS:
                return False, f"Invalid format. Allowed: {', '.join(ImageProcessor.ALLOWED_FORMATS)}"
            
            # Check file size (max 10MB)
            uploaded_file.seek(0, 2)  # Seek to end
            size = uploaded_file.tell()
            uploaded_file.seek(0)  # Reset
            
            if size > 10 * 1024 * 1024:  # 10MB
                return False, "File size too large. Maximum 10MB allowed."
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    @staticmethod
    def save_uploaded_image(uploaded_file, subfolder='photos', image_type='photo'):
        """
        Save an uploaded image to the media directory.
        
        Args:
            uploaded_file: Django UploadedFile object
            subfolder: Subfolder within media/gallery/
            image_type: 'photo' or 'thumbnail'
            
        Returns:
            Relative URL path to the saved image
        """
        # Validate
        is_valid, error = ImageProcessor.validate_image(uploaded_file)
        if not is_valid:
            raise ValueError(error)
        
        # Process image
        processed_file, filename = ImageProcessor.process_image(uploaded_file, image_type)
        
        # Create directory if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'gallery', subfolder)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(processed_file.read())
        
        # Return relative URL
        return f"{settings.MEDIA_URL}gallery/{subfolder}/{filename}"
