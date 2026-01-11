import boto3
import os
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class S3Service:
    """Service for handling AWS S3 operations"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_S3_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    
    def upload_movie(self, file_obj, key, content_type='video/mp4', metadata=None):
        """Upload movie file to S3"""
        try:
            extra_args = {
                'ContentType': content_type,
                'ServerSideEncryption': 'AES256'
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Successfully uploaded movie to S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise
    
    def generate_presigned_url(self, key, expiration=3600):
        """Generate presigned URL for streaming"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise
    
    def delete_movie(self, key):
        """Delete movie file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Successfully deleted movie from S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting from S3: {str(e)}")
            raise
    
    def get_object_size(self, key):
        """Get size of object in S3"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return response['ContentLength']
        except ClientError as e:
            logger.error(f"Error getting object size: {str(e)}")
            raise
