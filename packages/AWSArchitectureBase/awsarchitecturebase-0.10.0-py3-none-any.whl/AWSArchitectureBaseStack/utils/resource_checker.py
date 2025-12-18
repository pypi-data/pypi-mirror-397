"""
AWS Resource Existence Checker
===============================

Utility functions to check if AWS resources already exist before creation.
This prevents deployment failures when resources already exist in the account.
"""

import boto3
from botocore.exceptions import ClientError


def check_guardduty_detector_exists(region: str, profile: str = None) -> tuple[bool, str]:
    """
    Check if GuardDuty detector already exists.
    
    Args:
        region: AWS region
        profile: AWS profile name
        
    Returns:
        Tuple of (exists: bool, detector_id: str or None)
    """
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        client = session.client('guardduty', region_name=region)
        response = client.list_detectors()
        
        if response.get('DetectorIds'):
            return True, response['DetectorIds'][0]
        return False, None
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print(f"⚠️  Warning: Cannot check GuardDuty status - permission denied")
            return False, None
        raise


def check_security_hub_exists(region: str, profile: str = None) -> bool:
    """
    Check if Security Hub is already enabled.
    
    Args:
        region: AWS region
        profile: AWS profile name
        
    Returns:
        bool: True if Security Hub is enabled
    """
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        client = session.client('securityhub', region_name=region)
        client.describe_hub()
        return True
    except ClientError as e:
        if e.response['Error']['Code'] in ['InvalidAccessException', 'ResourceNotFoundException']:
            return False
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print(f"⚠️  Warning: Cannot check Security Hub status - permission denied")
            return False
        raise


def check_access_analyzer_exists(region: str, profile: str = None) -> tuple[bool, list]:
    """
    Check if IAM Access Analyzers already exist.
    
    Args:
        region: AWS region
        profile: AWS profile name
        
    Returns:
        Tuple of (exists: bool, analyzer_names: list)
    """
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        client = session.client('accessanalyzer', region_name=region)
        response = client.list_analyzers()
        
        analyzers = response.get('analyzers', [])
        if analyzers:
            names = [a['name'] for a in analyzers]
            return True, names
        return False, []
    except ClientError as e:
        if e.response['Error']['Code'] in ['ServiceQuotaExceededException', 'AccessDeniedException']:
            print(f"⚠️  Warning: Cannot check Access Analyzer status - {e.response['Error']['Code']}")
            return True, []  # Assume exists if quota exceeded
        raise


def check_iam_role_exists(role_name: str, profile: str = None) -> bool:
    """
    Check if IAM role already exists.
    
    Args:
        role_name: IAM role name
        profile: AWS profile name
        
    Returns:
        bool: True if role exists
    """
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        client = session.client('iam')
        client.get_role(RoleName=role_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            return False
        if e.response['Error']['Code'] == 'AccessDenied':
            print(f"⚠️  Warning: Cannot check IAM role '{role_name}' - permission denied")
            return False
        raise


def check_cloudwatch_log_group_exists(log_group_name: str, region: str, profile: str = None) -> bool:
    """
    Check if CloudWatch Log Group already exists.
    
    Args:
        log_group_name: Log group name
        region: AWS region
        profile: AWS profile name
        
    Returns:
        bool: True if log group exists
    """
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        client = session.client('logs', region_name=region)
        response = client.describe_log_groups(logGroupNamePrefix=log_group_name, limit=1)
        
        for group in response.get('logGroups', []):
            if group['logGroupName'] == log_group_name:
                return True
        return False
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print(f"⚠️  Warning: Cannot check CloudWatch log group '{log_group_name}' - permission denied")
            return False
        raise


def check_config_recorder_exists(region: str, profile: str = None) -> tuple[bool, str]:
    """
    Check if AWS Config recorder already exists.
    
    Args:
        region: AWS region
        profile: AWS profile name
        
    Returns:
        Tuple of (exists: bool, recorder_name: str or None)
    """
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        client = session.client('config', region_name=region)
        response = client.describe_configuration_recorders()
        
        recorders = response.get('ConfigurationRecorders', [])
        if recorders:
            return True, recorders[0]['name']
        return False, None
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print(f"⚠️  Warning: Cannot check AWS Config status - permission denied")
            return False, None
        raise


def check_service_linked_role_exists(service_name: str, profile: str = None) -> bool:
    """
    Check if service-linked role exists.
    
    Args:
        service_name: AWS service name (e.g., 'config.amazonaws.com')
        profile: AWS profile name
        
    Returns:
        bool: True if role exists
    """
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        client = session.client('iam')
        
        # Service-linked roles follow naming convention
        role_name = f"AWSServiceRoleFor{service_name.split('.')[0].replace('-', '').title()}"
        if service_name == 'config.amazonaws.com':
            role_name = 'AWSServiceRoleForConfig'
        
        try:
            client.get_role(RoleName=role_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                return False
            raise
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print(f"⚠️  Warning: Cannot check service-linked role for '{service_name}' - permission denied")
            return False
        raise
