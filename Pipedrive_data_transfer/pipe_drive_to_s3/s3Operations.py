from boto3.session import Session
import boto3
import os


class S3Operations():
    def __init__(self, aws_access_id, aws_access_secret_key, bucket_name):
        self.aws_access_id = aws_access_id
        self.aws_access_secret_key = aws_access_secret_key
        self.bucket_name = bucket_name

        self.bucket = self.connect_S3_bucket()
    

    def connect_S3_bucket(self):
        session = Session(
            aws_access_key_id=self.aws_access_id,
            aws_secret_access_key=self.aws_access_secret_key
        )

        s3 = session.resource('s3')
        connected_bucket = s3.Bucket(self.bucket_name)

        return connected_bucket

    
    def upload_file(self, local_path, s3_path):
        self.bucket.upload_file(local_path, s3_path)
    