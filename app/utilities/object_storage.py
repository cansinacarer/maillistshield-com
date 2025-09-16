import json
from botocore.exceptions import ClientError
from datetime import datetime

from flask import current_app
from app.config import s3


def upload_file(bucket_name, directory, file, s3, s3path=None):
    file_path = directory + "/" + file
    remote_path = s3path
    if remote_path is None:
        remote_path = file

    try:
        s3.Bucket(bucket_name).upload_file(file_path, remote_path)
    except ClientError as ce:
        print("error", ce)


def download_file(bucket_name, directory, local_name, key_name, s3):
    file_path = directory + "/" + local_name

    try:
        s3.Bucket(bucket_name).download_file(key_name, file_path)
    except ClientError as ce:
        print("error", ce)


def delete_file(bucket_name, keys, s3):
    objects = []
    for key in keys:
        objects.append({"Key": key})
    try:
        s3.Bucket(bucket_name).delete_objects(Delete={"Objects": objects})
    except ClientError as ce:
        print("error", ce)


def list_objects(bucket, s3):
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
    try:
        source = {"Bucket": source_bucket, "Key": source_key}
        s3.Bucket(destination_bucket).copy(source, destination_key)
    except ClientError as ce:
        print("error", ce)


def prevent_public_access(bucket, s3):
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
    try:
        s3.create_bucket(Bucket=name)
        if secure:
            prevent_public_access(name, s3)
    except ClientError as ce:
        print("error", ce)


def generate_download_link(bucket_name, key, s3, expiration_in_seconds=60):
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
    total_size = 0

    for obj in s3.Bucket(bucket_name).objects.filter(Prefix=folder_path):
        total_size = total_size + obj.size

    return round(total_size)


def generate_remote_file(bucket_name, folder_path, file_name, s3, content):
    return s3.meta.client.put_object(
        Body=content, Bucket=bucket_name, Key=folder_path + "/" + file_name
    )


def timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def generate_upload_link_profile_picture(user, file_type):
    return generate_upload_link(
        current_app.config["S3_BUCKET_NAME"],
        f"profile-pictures/{user.id}.png",
        file_type,
        s3,
        30,
    )


def generate_upload_link_validation_file(user, file_type, file):
    return generate_upload_link(
        current_app.config["S3_BUCKET_NAME"],
        f"validation/uploaded/{timestamp()}-{file}",
        file_type,
        s3,
        600,  # Longer expiration to allow for slower uploads of large csv files
    )


def generate_user_folder(user):
    generate_remote_file(
        current_app.config["S3_BUCKET_NAME"],
        f"user-files/user-{user.id}",
        ".tmp",
        s3,
        "tmp",
    )


def user_folder_size(user):
    return folder_size(
        current_app.config["S3_BUCKET_NAME"], f"user-files/user-{user.id}", s3
    )
