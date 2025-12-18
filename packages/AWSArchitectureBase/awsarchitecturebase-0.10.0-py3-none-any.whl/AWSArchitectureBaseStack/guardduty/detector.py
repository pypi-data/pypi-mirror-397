"""
AWS GuardDuty Detector
======================

Functions for enabling and configuring GuardDuty threat detection.
"""

from cdktf_cdktf_provider_aws.guardduty_detector import GuarddutyDetector
from ..utils import resource_checker


def create_guardduty_detector(
    scope,
    enable: bool = True,
    finding_publishing_frequency: str = "FIFTEEN_MINUTES",
    resource_id: str = "guardduty_detector",
    region: str = None,
    profile: str = None
):
    """
    Enable GuardDuty detector for threat detection.

    GuardDuty continuously monitors AWS accounts and workloads for malicious 
    activity and unauthorized behavior.

    :param scope: The CDKTF construct scope (stack instance)
    :param enable: Whether to enable the detector (default: True)
    :type enable: bool
    :param finding_publishing_frequency: How often to publish findings
    :type finding_publishing_frequency: str
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param region: AWS region (required for existence check)
    :type region: str
    :param profile: AWS profile name
    :type profile: str
    :returns: GuardDuty detector resource or None if already exists
    :rtype: GuarddutyDetector

    **Finding Publishing Frequencies:**
    
    - `FIFTEEN_MINUTES`: Publish findings every 15 minutes (default)
    - `ONE_HOUR`: Publish findings every hour
    - `SIX_HOURS`: Publish findings every 6 hours

    **What GuardDuty Monitors:**
    
    - VPC Flow Logs: Network traffic analysis
    - DNS Logs: DNS query patterns
    - CloudTrail Events: API activity monitoring
    - S3 Data Events: S3 access patterns
    - EKS Audit Logs: Kubernetes activity
    - RDS Login Activity: Database access patterns
    - EBS Volumes: Malware detection
    - Lambda Network Activity: Function behavior
    - Runtime Monitoring: EC2/ECS/EKS runtime threats

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import guardduty
        >>> 
        >>> # Enable GuardDuty with default settings
        >>> detector = guardduty.create_guardduty_detector(
        ...     scope=self,
        ...     enable=True
        ... )

    .. note::
       **Cost**: GuardDuty pricing is based on:
       - Volume of CloudTrail events analyzed
       - Volume of VPC Flow Logs and DNS logs analyzed
       - Volume of S3 events analyzed
       - Number of EBS snapshots scanned for malware
       
       Typical cost: $5-50/month for small accounts
       
    .. warning::
       Disabling GuardDuty does not delete existing findings.
       Set enable=False to temporarily suspend monitoring.
    """
    if not enable:
        return None

    # Check if GuardDuty detector already exists
    if region:
        exists, detector_id = resource_checker.check_guardduty_detector_exists(region, profile)
        if exists:
            print(f"⚠️  WARNING: GuardDuty detector already exists (ID: {detector_id})")
            print(f"    Skipping creation to avoid deployment failure.")
            print(f"    The existing detector will continue to operate.")
            print(f"    To manage it with Terraform, import it using:")
            print(f"    terraform import aws_guardduty_detector.{resource_id} {detector_id}\n")
            return None

    detector = GuarddutyDetector(
        scope,
        resource_id,
        enable=enable,
        finding_publishing_frequency=finding_publishing_frequency
    )

    return detector
