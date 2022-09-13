#!/bin/bash          

# Fill in details in this section
subscription_id="<SUBCRIPTION_ID>"
resource_prefix="<RESOURCE_PREFIX>"
location="eastus"
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
# if ! [ -x "$(command -v az)" ]; then
#   echo 'Error: Azure CLI is not installed. Please follow guidance on https://aka.ms/azure-cli to install az command line' >&2
#   exit 1
# fi

# az upgrade --all true --yes
# # login if required
# az account get-access-token
# if [[ $? == 0 ]]; then
#   echo "Logged in, using current subscriptions "
# else
#   echo "Logging in via az login..."
#   az login --use-device-code
# fi



# echo "Setting subscription to $subscription_id"
# az account set -s $subscription_id

storage_account_key=$(az storage account keys list --account-name $storage_account_name --out json --query "[0].value")

# this is completely optional. It will download some demo NYC data and upload it to the default storage account, to make the setup experience smoother
echo "preparing data"
for file in ./data/*
  do
    echo $file
    file_name=`basename $file`
    echo $file_name
    az storage fs file upload --account-name $storage_account_name --file-system $storage_file_system_name --path home_credit_data/$file_name --source $file --account-key $storage_account_key
  done
