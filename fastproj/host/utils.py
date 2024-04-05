import boto3

def delete_file_from_s3(bucket_name, file_s3_url):
    try:
        # Extract file key from the S3 URL
        file_key = '/'.join(file_s3_url.split('/')[3:])
        
        # Initialize S3 client
        s3 = boto3.client('s3')
        
        # Delete the file from S3
        s3.delete_object(Bucket=bucket_name, Key=file_key)
        
        return True
    except Exception as e:
        print(f"Error deleting file from S3: {e}")
        return False