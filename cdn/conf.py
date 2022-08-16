import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

AWS_ACCESS_KEY_ID = 'EAMYCCAV7GLM2MNYQ5LT'
AWS_SECRET_ACCESS_KEY = 'Ubq5txiFK2FmqBHC801SzMAQnqOI8UKp21wXTzrFjqQ'
AWS_STORAGE_BUCKET_NAME = 'agartha-media'
AWS_S3_ENDPOINT_URL = 'https://fra1.digitaloceanspaces.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
} 
AWS_LOCATION = "https://agartha-media.fra1.digitaloceanspaces.com"
AWS_DEFAULT_ACL = "public-read"

# STATICFILES_STORAGE = 'cdn.backends.StaticRootS3BotoStorage'
DEFAULT_FILE_STORAGE = "cdn.backends.MediaRootS3BotoStorage"
