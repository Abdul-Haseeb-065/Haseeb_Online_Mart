from typing import List
import boto3 # type: ignore
from botocore.exceptions import NoCredentialsError# type: ignore
from fastapi import HTTPException, UploadFile
from app.settings import BUCKET_NAME, AWS_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY# type: ignore


def upload_files_in_s3(files: List[UploadFile], product_id: int):
    s3_client = boto3.client("s3",
                             aws_access_key_id=AWS_ACCESS_KEY,
                             aws_secret_access_key=AWS_SECRET_KEY
                             )
    image_urls: List[str] = []
    for file in files:
        try:
            object_name = f"products/{product_id}/{file.filename}"
            print(f"Object Name : {object_name}")
            s3_client.upload_fileobj(
                file.file,
                BUCKET_NAME,
                object_name
            )
            image_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
            image_urls.append(image_url)
        except NoCredentialsError as x:
            raise HTTPException(status_code=500, detail=str(x))
    return image_urls
