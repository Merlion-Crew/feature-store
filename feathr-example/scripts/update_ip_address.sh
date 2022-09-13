#!/bin/bash          

# Fill in details in this section
subscription_id="<SUBCRIPTION_ID>"
resource_prefix="<RESOURCE_PREFIX>"
synapse_sql_admin_name="cliuser1"
synapse_sql_admin_password="<PASSWORD>"
synapse_sparkpool_name="spark31"

# You don't have to modify the names below
service_principal_name="$resource_prefix"sp
resoruce_group_name="$resource_prefix"rg
storage_account_name="$resource_prefix"sto
storage_file_system_name="$resource_prefix"fs
synapse_workspace_name="$resource_prefix"spark
redis_cluster_name="$resource_prefix"redis
purview_account_name="$resource_prefix"purview

# detect whether az cli is installed or not
if ! [ -x "$(command -v az)" ]; then
  echo 'Error: Azure CLI is not installed. Please follow guidance on https://aka.ms/azure-cli to install az command line' >&2
  exit 1
fi

az upgrade --all true --yes
# login if required
az account get-access-token
if [[ $? == 0 ]]; then
  echo "Logged in, using current subscriptions "
else
  echo "Logging in via az login..."
  az login --use-device-code
fi



echo "Setting subscription to $subscription_id, Creating $service_principal_name service principal"
az account set -s $subscription_id

# depending on your preference, you can set a narrow range of IPs (like below) or a broad range of IPs to allow client access to Synapse clusters
external_ip=$(curl -s http://whatismyip.akamai.com/)
echo "External IP is: ${external_ip}. Adding it to firewall rules" 
az synapse workspace firewall-rule create --name allowCurrentIP --workspace-name $synapse_workspace_name --resource-group $resoruce_group_name --start-ip-address "$external_ip" --end-ip-address "$external_ip"

