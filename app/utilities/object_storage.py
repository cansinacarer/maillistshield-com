"""Object storage utilities for S3-compatible storage operations.

This module provides functions for interacting with S3-compatible object storage,
including file uploads, downloads, deletions, and pre-signed URL generation.
"""

import json
from botocore.exceptions import ClientError
from datetime import datetime

from flask import current_app
from app.config import s3


def upload_file(bucket_name, directory, file, s3, s3path=None):
    """Upload a file to an S3 bucket.

    Args:
        bucket_name: The name of the target S3 bucket.
        directory: Local directory containing the file.
        file: The filename to upload.
        s3: The boto3 S3 resource object.
        s3path: Optional custom path in the bucket. Defaults to the filename.
    """
    file_path = directory + "/" + file
    remote_path = s3path
    if remote_path is None:
        remote_path = file

    try:
        s3.Bucket(bucket_name).upload_file(file_path, remote_path)
    except ClientError as ce:
        print("error", ce)


def download_file(bucket_name, directory, local_name, key_name, s3):
    """Download a file from an S3 bucket.

    Args:
        bucket_name: The name of the source S3 bucket.
        directory: Local directory to save the file.
        local_name: The local filename to save as.
        key_name: The S3 object key to download.
        s3: The boto3 S3 resource object.
    """
    file_path = directory + "/" + local_name

    try:
        s3.Bucket(bucket_name).download_file(key_name, file_path)
    except ClientError as ce:
        print("error", ce)


def delete_file(bucket_name, keys, s3):
    """Delete one or more files from an S3 bucket.

    Args:
        bucket_name: The name of the S3 bucket.
        keys: List of S3 object keys to delete.
        s3: The boto3 S3 resource object.
    """
    objects = []
    for key in keys:
        objects.append({"Key": key})
    try:
        s3.Bucket(bucket_name).delete_objects(Delete={"Objects": objects})
    except ClientError as ce:
        print("error", ce)


def list_objects(bucket, s3):
    """List all objects in an S3 bucket.

    Args:
        bucket: The name of the S3 bucket.
        s3: The boto3 S3 resource object.

    Returns:
        list: A list of object keys in the bucket.
    """
    try:
        response = s3.meta.client.list_objects(Bucket=bucket)
        objects = []
        for content in response["Contents"]:
            objects.append(content["Key"])
        print(bucket, "contains", len(objects), "files")
        return objects
    except ClientError as ce:
        print("error", ce)


def copy_file(source_bucket, destination_bucket, source_key, destination_key, s3):
    """Copy a file between S3 buckets or within a bucket.

    Args:
        source_bucket: The name of the source bucket.
        destination_bucket: The name of the destination bucket.
        source_key: The S3 key of the source object.
        destination_key: The S3 key for the destination object.
        s3: The boto3 S3 resource object.
    """
    try:
        source = {"Bucket": source_bucket, "Key": source_key}
        s3.Bucket(destination_bucket).copy(source, destination_key)
    except ClientError as ce:
        print("error", ce)


def prevent_public_access(bucket, s3):
    """Configure a bucket to block all public access.

    Args:
        bucket: The name of the S3 bucket.
        s3: The boto3 S3 resource object.
    """
    try:
        s3.meta.client.put_public_access_block(
            Bucket=bucket,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
        )
    except ClientError as ce:
        print("error", ce)


def create_bucket(name, s3, secure=False):
    """Create a new S3 bucket.

    Args:
        name: The name for the new bucket.
        s3: The boto3 S3 resource object.
        secure: If True, block all public access to the bucket.
    """
    try:
        s3.create_bucket(Bucket=name)
        if secure:
            prevent_public_access(name, s3)
    except ClientError as ce:
        print("error", ce)


def generate_download_link(bucket_name, key, s3, expiration_in_seconds=60):
    """Generate a pre-signed URL for downloading an S3 object.

    Args:
        bucket_name: The name of the S3 bucket.
        key: The S3 object key.
        s3: The boto3 S3 resource object.
        expiration_in_seconds: URL expiration time in seconds.

    Returns:
        str: A pre-signed URL for downloading the object.
    """
    try:
        response = s3.meta.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expiration_in_seconds,
        )
        return response
    except ClientError as ce:
        print("error", ce)


def generate_upload_link(
    bucket_name, file_name, file_type, s3, expiration_in_seconds=60
):
    """Generate a pre-signed POST URL for uploading to S3.

    Args:
        bucket_name: The name of the S3 bucket.
        file_name: The target filename/key in the bucket.
        file_type: The Content-Type of the file being uploaded.
        s3: The boto3 S3 resource object.
        expiration_in_seconds: URL expiration time in seconds.

    Returns:
        str: JSON string containing upload data and preview URL.
    """
    try:
        upload = s3.meta.client.generate_presigned_post(
            Bucket=bucket_name,
            Key=file_name,
            Fields={"Content-Type": file_type},
            Conditions=[{"Content-Type": file_type}],
            ExpiresIn=expiration_in_seconds,
        )
        response = json.dumps(
            {
                "data": upload,
                # this is only for displaying the uploaded image in the upload preview:
                "url": generate_download_link(
                    bucket_name, file_name, s3, expiration_in_seconds
                ),
            }
        )
        return response
    except ClientError as ce:
        print("error", ce)


def folder_size(bucket_name, folder_path, s3):
    """Calculate the total size of all objects in a folder.

    Args:
        bucket_name: The name of the S3 bucket.
        folder_path: The folder prefix to calculate size for.
        s3: The boto3 S3 resource object.

    Returns:
        int: Total size in bytes of all objects in the folder.
    """
    total_size = 0

    for obj in s3.Bucket(bucket_name).objects.filter(Prefix=folder_path):
        total_size = total_size + obj.size

    return round(total_size)


def generate_remote_file(bucket_name, folder_path, file_name, s3, content):
    """Create a file directly in S3 with the specified content.

    Args:
        bucket_name: The name of the S3 bucket.
        folder_path: The folder path in the bucket.
        file_name: The name of the file to create.
        s3: The boto3 S3 resource object.
        content: The content to write to the file.

    Returns:
        dict: The S3 put_object response.
    """
    return s3.meta.client.put_object(
        Body=content, Bucket=bucket_name, Key=folder_path + "/" + file_name
    )


def timestamp():
    """Generate a timestamp string for file naming.

    Returns:
        str: Current timestamp in YYYYMMDDHHmmss format.
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")


def generate_upload_link_profile_picture(user, file_type):
    """Generate a pre-signed upload URL for a user's profile picture.

    Args:
        user: The user object.
        file_type: The MIME type of the image being uploaded.

    Returns:
        str: JSON string containing upload data and preview URL.
    """
    return generate_upload_link(
        current_app.config["S3_BUCKET_NAME"],
        f"profile-pictures/{user.id}.png",
        file_type,
        s3,
        30,
    )


def generate_upload_link_validation_file(user, file_type, file):
    """Generate a pre-signed upload URL for a batch validation file.

    Args:
        user: The user object.
        file_type: The MIME type of the file being uploaded.
        file: The original filename.

    Returns:
        str: JSON string containing upload data and preview URL.
    """
    return generate_upload_link(
        current_app.config["S3_BUCKET_NAME"],
        f"validation/uploaded/{timestamp()}-{file}",
        file_type,
        s3,
        600,  # Longer expiration to allow for slower uploads of large csv files
    )


def generate_user_folder(user):
    """Create a user's personal folder in object storage.

    Creates a placeholder file to establish the folder structure.

    Args:
        user: The user object.
    """
    generate_remote_file(
        current_app.config["S3_BUCKET_NAME"],
        f"user-files/user-{user.id}",
        ".tmp",
        s3,
        "tmp",
    )


def user_folder_size(user):
    """Calculate the total size of a user's folder.

    Args:
        user: The user object.

    Returns:
        int: Total size in bytes of the user's folder.
    """
    return folder_size(
        current_app.config["S3_BUCKET_NAME"], f"user-files/user-{user.id}", s3
    )
