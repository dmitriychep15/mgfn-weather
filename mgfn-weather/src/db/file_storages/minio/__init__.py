"""Minio file storage client and function for it's initialization."""

import json
import logging

from miniopy_async import Minio


logger = logging.getLogger(__name__)


async def init_minio(
    address: str,
    access_key: str,
    secret_key: str,
    bucket: str,
) -> Minio:
    """
    Initializes Minio client:
    - Make connection to Minio;
    - Create required bucket if such one doesn't exist;
    - Set bucket policy.
    """
    logger.info("Start initializing file storage %s...", address)
    client = Minio(
        endpoint=address,
        secure=False,
        access_key=access_key,
        secret_key=secret_key,
    )
    bucket_found = await client.bucket_exists(bucket)
    if not bucket_found:
        await client.make_bucket(bucket)
        logger.info("Bucket '%s' was successfully created", bucket)
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": [
                    "s3:GetBucketLocation",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                ],
                "Resource": f"arn:aws:s3:::{bucket}",
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListMultipartUploadParts",
                    "s3:AbortMultipartUpload",
                ],
                "Resource": f"arn:aws:s3:::{bucket}/*",
            },
        ],
    }
    await client.set_bucket_policy(bucket, json.dumps(policy))
    logger.info("Set policy for bucket '%s'", bucket)
    logger.info("SUCCESS - file storage is successfully initialized")
    return client


minio_client: Minio | None = None
