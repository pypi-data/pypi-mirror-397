"""
AWS CloudTrail S3 Bucket Creation

This module handles S3 bucket creation specifically for AWS CloudTrail service.
CloudTrail owns its bucket policy, lifecycle rules, and configuration.

"""

import json
from .. import s3


def create_cloudtrail_bucket_policy_json(bucket_name: str, account_id: str, trail_name: str, region: str) -> str:
    """
    Create AWS CloudTrail bucket policy JSON.
    
    This defines the least-privilege policy for AWS CloudTrail service.
    Includes both AWS:SourceAccount and AWS:SourceArn conditions for FTR compliance.
    
    Args:
        bucket_name: Name of the CloudTrail S3 bucket
        account_id: AWS account ID
        trail_name: Name of the CloudTrail trail
        region: AWS region where the trail is created
    
    Returns:
        JSON string with bucket policy
    """
    # Construct CloudTrail ARN: arn:aws:cloudtrail:<region>:<account_id>:trail/<trail_name>
    trail_arn = f"arn:aws:cloudtrail:{region}:{account_id}:trail/{trail_name}"
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AWSCloudTrailAclCheck",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:GetBucketAcl",
                "Resource": f"arn:aws:s3:::{bucket_name}",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": account_id,
                        "aws:SourceArn": trail_arn
                    }
                }
            },
            {
                "Sid": "AWSCloudTrailWrite",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "StringEquals": {
                        "s3:x-amz-acl": "bucket-owner-full-control",
                        "aws:SourceAccount": account_id,
                        "aws:SourceArn": trail_arn
                    }
                }
            }
        ]
    }
    
    return json.dumps(policy)


def create_cloudtrail_s3_bucket(
    scope,
    bucket_name: str,
    account_id: str,
    project_name: str,
    environment: str,
    region: str,
    trail_name: str = None,
    logging_bucket: str = None,
    kms_key_id: str = None,
    resource_id: str = "cloudtrail_bucket"
):
    """
    Create FTR-compliant S3 bucket for AWS CloudTrail.
    
    This creates a bucket with:
    - CloudTrail-specific bucket policy (with AWS:SourceArn condition)
    - 10-year retention lifecycle
    - Public access blocking
    - Versioning and encryption
    - Optional access logging
    
    Args:
        scope: The CDKTF construct scope
        bucket_name: Name of the bucket
        account_id: AWS account ID
        project_name: Project name (used to derive trail_name if not provided)
        environment: Environment (dev, staging, prod)
        region: AWS region where the trail is created
        trail_name: Optional name of the CloudTrail trail (defaults to "{project_name}-trail")
        logging_bucket: Optional logs bucket name
        kms_key_id: Optional KMS key ID
        resource_id: Terraform resource ID
    
    Returns:
        dict: Created S3 resources
    
    Example:
        >>> from . import s3_bucket
        >>> # Minimal usage - trail_name derived from project_name
        >>> trail_bucket = s3_bucket.create_cloudtrail_s3_bucket(
        ...     scope=stack,
        ...     bucket_name="myapp-cloudtrail-us-east-1",
        ...     account_id="123456789012",
        ...     project_name="myapp",
        ...     environment="prod",
        ...     region="us-east-1"
        ... )
        >>> # Custom trail name
        >>> trail_bucket = s3_bucket.create_cloudtrail_s3_bucket(
        ...     scope=stack,
        ...     bucket_name="myapp-cloudtrail-us-east-1",
        ...     account_id="123456789012",
        ...     project_name="myapp",
        ...     environment="prod",
        ...     region="us-east-1",
        ...     trail_name="myapp-custom-trail"
        ... )
    """
    # Create CloudTrail-specific bucket policy with AWS:SourceArn condition
    # Default trail_name to {project_name}-trail if not provided
    policy_json = create_cloudtrail_bucket_policy_json(
        bucket_name, account_id, trail_name or f"{project_name}-trail", region
    )
    
    # Create CloudTrail-specific lifecycle rule (10-year retention)
    lifecycle_rule = s3.create_lifecycle_rule(
        rule_id="cloudtrail-logs-lifecycle",
        retention_days=3650,  # 10 years for audit trail
        ia_transition_days=90,
        glacier_transition_days=365,
        noncurrent_retention_days=90
    )
    
    # Build tags
    tags = {
        "Service": "CloudTrail",
        "Project": project_name,
        "Environment": environment
    }
    
    # Create the bucket using generic S3 method
    return s3.create_bucket(
        scope=scope,
        bucket_name=bucket_name,
        block_public_access=True,
        enable_versioning=True,
        enable_encryption=True,
        kms_key_id=kms_key_id,
        bucket_policy_json=policy_json,
        lifecycle_rules=[lifecycle_rule],
        logging_target_bucket=logging_bucket,
        logging_prefix="cloudtrail-access-logs/" if logging_bucket else None,
        tags=tags,
        resource_id=resource_id
    )
