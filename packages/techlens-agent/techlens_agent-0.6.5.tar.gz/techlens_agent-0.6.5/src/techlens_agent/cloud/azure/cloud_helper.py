import subprocess
import json

from azure.identity import AzureAuthorityHosts
from azure.core import AzureClouds


cloud_to_settings = {
    "AzureCloud": (
        AzureAuthorityHosts.AZURE_PUBLIC_CLOUD,
        "management.azure.com",
        AzureClouds.AZURE_PUBLIC_CLOUD,
        ["https://management.azure.com/.default"],
    ),
    "AzureUSGovernment": (
        AzureAuthorityHosts.AZURE_GOVERNMENT,
        "management.usgovcloudapi.net",
        AzureClouds.AZURE_US_GOVERNMENT,
        ["https://management.core.usgovcloudapi.net/.default"],
    ),
}


def detect_cloud(subscription_id: str, dry: False) -> str:
    if dry:
        return "AzureCloud"

    try:
        result = subprocess.run(
            f"az account show --subscription {subscription_id} --output json",
            capture_output=True,
            text=True,
            check=True,
        )
        account_info = json.loads(result.stdout)
        return account_info.get("cloudName", "AzureCloud")

    except Exception as e:
        return "AzureCloud"


def get_cloud_settings(cloud_name):
    return cloud_to_settings.get(cloud_name, cloud_to_settings["AzureCloud"])
