import json
import shutil
import sys
from datetime import datetime
from mypy_boto3_s3 import S3Client


def create_bucket(s3: S3Client, bucket: str) -> str:
    timestamp = str(int(datetime.timestamp(datetime.now())))
    try:
        print('Creating an S3 bucket...')
        response = s3.create_bucket(Bucket=bucket + timestamp)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        bucket_name = response['Location'][1:]
        print(f'S3 bucket created successfully.\n{bucket_name}')
        return bucket_name


def put_bucket_policy(s3: S3Client, s3_config: dict, bucket: str, aws_user_account: str, role_arn) -> None:
    bucket_policy = s3_config['BucketPolicy']
    bucket_policy['Statement'][0]['Principal'] = {"AWS": [aws_user_account]}
    bucket_policy['Statement'][0]['Resource'] = f'arn:aws:s3:::{bucket}/*'
    bucket_policy['Statement'][1]['Principal'] = {"AWS": [role_arn]}
    bucket_policy['Statement'][1]['Resource'] = f'arn:aws:s3:::{bucket}/*'
    try:
        print('Applying a policy to an S3 Bucket...')
        s3.put_bucket_policy(
            Bucket=bucket,
            Policy=json.dumps(bucket_policy)
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'Policy successfully applied to bucket {bucket}')


def upload_server_app_to_s3_bucket(s3: S3Client, bucket: str) -> None:
    try:
        print('Uploading a server app to an S3 Bucket...')
        shutil.make_archive('server', 'zip', './server')
        s3.upload_file('./server.zip', bucket, 'server.zip')
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'Server app successfully uploaded to bucket {bucket}')


def delete_server_app_from_s3_bucket(s3: S3Client, bucket: str) -> None:
    try:
        print('Deleting a server app from an S3 Bucket...')
        s3.delete_object(Bucket=bucket, Key='server.zip')
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'Server app successfully deleted from bucket {bucket}')


def delete_bucket(s3: S3Client, bucket: str) -> None:
    try:
        print('Deleting an S3 bucket...')
        s3.delete_bucket(Bucket=bucket)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'S3 bucket deleted successfully.\n{bucket}')
