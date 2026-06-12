#!/usr/bin/env python3
"""Простой скрипт для синхронизации локальной папки media/ в S3.

Использование:
  set AWS_ACCESS_KEY_ID=...
  set AWS_SECRET_ACCESS_KEY=...
  set AWS_STORAGE_BUCKET_NAME=your-bucket
  python scripts\sync_media_to_s3.py --bucket your-bucket

Если переменная окружения не задана, можно передать `--bucket`.
"""
import argparse
import os
import mimetypes
import boto3
from botocore.exceptions import ClientError


def upload_file(s3_client, bucket, local_path, key):
    content_type, _ = mimetypes.guess_type(local_path)
    extra_args = {'ContentType': content_type} if content_type else {}
    try:
        s3_client.upload_file(local_path, bucket, key, ExtraArgs=extra_args)
        print(f'Uploaded: {local_path} -> s3://{bucket}/{key}')
    except ClientError as e:
        print(f'Error uploading {local_path}: {e}')


def sync_media(bucket, prefix=''):
    media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
    if not os.path.isdir(media_root):
        print('media/ directory not found:', media_root)
        return

    s3 = boto3.client('s3')

    for root, dirs, files in os.walk(media_root):
        for fname in files:
            local_path = os.path.join(root, fname)
            rel_path = os.path.relpath(local_path, media_root).replace('\\', '/')
            key = f"{prefix.rstrip('/')}/{rel_path}".lstrip('/') if prefix else rel_path
            upload_file(s3, bucket, local_path, key)


def main():
    parser = argparse.ArgumentParser(description='Sync local media/ to S3')
    parser.add_argument('--bucket', help='S3 bucket name (overrides AWS_STORAGE_BUCKET_NAME env)')
    parser.add_argument('--prefix', default='', help='Optional key prefix in bucket')
    args = parser.parse_args()

    bucket = args.bucket or os.environ.get('AWS_STORAGE_BUCKET_NAME')
    if not bucket:
        print('Bucket name required via --bucket or AWS_STORAGE_BUCKET_NAME env var')
        return

    print('Starting sync to bucket:', bucket)
    sync_media(bucket, args.prefix)


if __name__ == '__main__':
    main()
