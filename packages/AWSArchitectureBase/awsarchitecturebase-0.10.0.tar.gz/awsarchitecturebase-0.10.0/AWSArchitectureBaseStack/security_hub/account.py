"""
Security Hub Account Configuration
==================================

Functions for enabling and configuring AWS Security Hub at the account level.
"""

from cdktf_cdktf_provider_aws.securityhub_account import SecurityhubAccount
from ..utils import resource_checker


def enable_security_hub_account(
    scope,
    resource_id: str = "security_hub_account",
    enable_default_standards: bool = True,
    control_finding_generator: str = "SECURITY_CONTROL",
    auto_enable_controls: bool = True,
    skip_if_exists: bool = True,
    region: str = None,
    profile: str = None
):
    """
    Enable AWS Security Hub for the account.

    Creates the Security Hub account configuration with recommended settings
    for FTR compliance monitoring.

    **Important:** Security Hub can only be enabled once per AWS account.

    If Security Hub is already enabled (via Console, CLI, or another IaC tool), 
    deployment behavior depends on skip_if_exists:
    - True (default): Skips creation with warning, deployment continues
    - False: Deployment fails with resource conflict error

    :param scope: The CDKTF construct scope (stack instance)
    :param resource_id: Unique identifier for this resource
    :type resource_id: str
    :param enable_default_standards: Enable AWS Foundational Security Best Practices
    :type enable_default_standards: bool
    :param control_finding_generator: Finding generation method
    :type control_finding_generator: str
    :param auto_enable_controls: Automatically enable new controls
    :type auto_enable_controls: bool
    :param skip_if_exists: Skip creation if Security Hub already enabled (prevents deployment failure)
    :type skip_if_exists: bool
    :param region: AWS region (required for existence check)
    :type region: str
    :param profile: AWS profile name
    :type profile: str
    :returns: Security Hub account resource or None if skipped
    :rtype: SecurityhubAccount or None

    Example:
        >>> from AWSArchitectureBase.AWSArchitectureBaseStack import security_hub
        >>> 
        >>> # Default behavior - skip if already exists
        >>> hub = security_hub.enable_security_hub_account(
        ...     scope=self,
        ...     enable_default_standards=True,
        ...     auto_enable_controls=True
        ... )
        >>> 
        >>> # Force creation (will fail if already exists)
        >>> hub = security_hub.enable_security_hub_account(
        ...     scope=self,
        ...     skip_if_exists=False
        ... )

    .. note::
       **Security Hub Charges:** AWS Security Hub incurs charges per finding and compliance check.
       See AWS pricing for details.
       
       **control_finding_generator options:** "SECURITY_CONTROL" or "STANDARD_CONTROL"
       
       **If Security Hub Already Exists:**
       
       With skip_if_exists=True (default):
       - Prints warning message
       - Returns None
       - Deployment continues normally
       - Standards can still be enabled separately
       
       With skip_if_exists=False:
       - Terraform will attempt to create the resource
       - Will fail with: "BadRequestException: account is already subscribed"
       - Use this if you want to import existing Security Hub into Terraform state
       
       **To Import Existing Security Hub:**
       
       ```bash
       cdktf import aws_securityhub_account.security_hub_account <account-id>
       ```

    .. warning::
       Do NOT disable Security Hub manually if it's managed by this code.
       Standards and findings will be lost.
    """
    # Check if Security Hub already exists
    if skip_if_exists and region:
        exists = resource_checker.check_security_hub_exists(region, profile)
        if exists:
            print("⚠️  WARNING: Security Hub is already enabled in this AWS account.")
            print("    Skipping creation to avoid deployment failure.")
            print("    Existing Security Hub will continue to operate.")
            print("    Standards can still be enabled separately.")
            print(f"    To manage it with Terraform, import it using:")
            print(f"    terraform import aws_securityhub_account.{resource_id} <account-id>\n")
            return None
    
    if skip_if_exists and not region:
        # Legacy warning when region is not provided
        print("⚠️  WARNING: Security Hub account creation requested.")
        print("    If Security Hub is already enabled in this AWS account, Terraform will attempt to adopt it.")
        print("    Set skip_if_exists=False in your configuration if you want strict creation enforcement.")
        print("    See Security Hub documentation for import instructions if deployment fails.\n")
    
    security_hub = SecurityhubAccount(
        scope,
        resource_id,
        enable_default_standards=enable_default_standards,
        control_finding_generator=control_finding_generator,
        auto_enable_controls=auto_enable_controls
    )

    return security_hub
