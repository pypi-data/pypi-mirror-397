"""
FTR Compliance Configuration Module
===================================

Provides default FTR compliance configuration for AWS infrastructure stacks.

This module is part of the AWSArchitectureBase package and provides sensible
defaults for FTR compliance services. Consuming applications can:

1. Use these defaults by importing this module
2. Override specific values by customizing the returned dictionary
3. Create their own ftr_compliance_config.py module to completely override defaults

:author: Buzzerboy Inc
:version: 1.0.0
"""


def get_default_ftr_compliance_config(project_name):
    """
    Get default FTR Compliance configuration.
    
    This can be overridden by consuming applications by passing
    their own ftr_compliance_config to the stack.
    
    :param project_name: Project name for naming (e.g., "product-app-tier")
    :type project_name: str
    :return: FTR compliance configuration dictionary
    :rtype: dict
    
    Example:
        >>> from AWSArchitectureBaseStack import ftr_compliance_config
        >>> config = ftr_compliance_config.get_default_ftr_compliance_config("my-app-prod")
        >>> # Customize as needed
        >>> config['inspector']['enable_ec2'] = True
        >>> # Pass to stack
        >>> stack = AWSArchitectureBase(
        ...     scope, "my-stack",
        ...     ftr_compliance_config=config,
        ...     ...
        ... )
    """
    return {
        'security_hub': {
            'enable_standards': True,
            'auto_enable_controls': True,
            'standards': [
                'cis-aws-foundations-benchmark/v/3.0.0'
            ]
        },
        'config': {
            's3_bucket_name': f'{project_name}-config',
            'recorder_name': f'{project_name}-recorder',
            'channel_name': f'{project_name}-channel',
            'enable_recorder': True,
            'enable_rules': True,
            'rules': ['S3_BUCKET_VERSIONING_ENABLED'],
            's3_key_prefix': 'config',
            'sns_topic_arn': None
        },
        'backup': {
            'enable_backup': True,
            'vault_name': f'{project_name}-backup-vault',
            'retention_days': 35
        },
        'inspector': {
            'enable_scanning': True,
            'enable_ec2': False,
            'enable_ecr': True
        },
        'systems_manager': {
            'enable_patching': True,
            'operating_system': 'AMAZON_LINUX_2'
        },
        'cloudtrail': {
            'enable_logging': True,
            'trail_name': f'{project_name}-trail',
            'enable_log_file_validation': True
        },
        'notifications': {
            'topic_name': f'{project_name}-compliance-alerts',
            'email_addresses': []
        }
    }

