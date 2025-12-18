from enum import Enum

class ArchitectureFlags(Enum):
    """
    Architecture configuration flags for optional components.

    **Skip Flags (disable features):**
    
    :param SKIP_DATABASE: Skip database creation
    :param SKIP_DOMAIN: Skip domain and DNS configuration
    :param SKIP_DEFAULT_POST_APPLY_SCRIPTS: Skip default post-apply scripts
    :param SKIP_SSL_CERT: Skip SSL certificate creation
    
    **Skip Flags (opt-out FTR compliance services):**
        All FTR compliance services are enabled by default (strongest compliance position).
        Use these flags to skip specific services if needed.
        :param SKIP_SECURITY_HUB: Skip AWS Security Hub with FTR compliance standards
        :param SKIP_CONFIG: Skip AWS Config for compliance monitoring
        :param SKIP_BACKUP: Skip AWS Backup for centralized backup management
        :param SKIP_INSPECTOR: Skip AWS Inspector for vulnerability assessments
        :param SKIP_SYSTEMS_MANAGER: Skip AWS Systems Manager for patch management
        :param SKIP_CLOUDTRAIL: Skip AWS CloudTrail for enhanced logging
        :param SKIP_GUARDDUTY: Skip AWS GuardDuty for threat detection
        :param SKIP_ACCESS_ANALYZER: Skip AWS IAM Access Analyzer (CIS v3.0.0 Control 1.20)
        :param SKIP_NOTIFICATIONS: Skip AWS SNS/SES for compliance notifications
        :param SKIP_ALL_FTR_COMPLIANCE: Skip all FTR compliance services at once
        """

    # Skip flags
    SKIP_DATABASE = "skip_database"
    SKIP_DOMAIN = "skip_domain"
    SKIP_DEFAULT_POST_APPLY_SCRIPTS = "skip_default_post_apply_scripts"
    SKIP_SSL_CERT = "skip_ssl_cert"
    
    # FTR Compliance enable flags
    SKIP_SECURITY_HUB = "skip_security_hub"
    SKIP_CONFIG = "skip_config"
    SKIP_BACKUP = "skip_backup"
    SKIP_INSPECTOR = "skip_inspector"
    SKIP_SYSTEMS_MANAGER = "skip_systems_manager"
    SKIP_CLOUDTRAIL = "skip_cloudtrail"
    SKIP_GUARDDUTY = "skip_guardduty"
    SKIP_ACCESS_ANALYZER = "skip_access_analyzer"
    SKIP_NOTIFICATIONS = "skip_notifications"
    SKIP_ALL_FTR_COMPLIANCE = "skip_all_ftr_compliance"