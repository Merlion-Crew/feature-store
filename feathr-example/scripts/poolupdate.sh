subscription_id="<SUBSCRIPTION_ID>"
resource_prefix="<RESOURCE_PREFIX>"
synapse_sql_admin_name="<SQL_ADMIN_NAME>"
synapse_sql_admin_password="<PASSWORD>"
synapse_sparkpool_name="<SPARKPOOL_NAME>"

resoruce_group_name="$resource_prefix"rg

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

az synapse spark pool delete --name $synapse_sparkpool_name --workspace-name $synapse_workspace_name --resource-group $resoruce_group_name


az synapse spark pool create --name $synapse_sparkpool_name --workspace-name $synapse_workspace_name  --resource-group $resoruce_group_name --spark-version 3.1 --node-count 3 --node-size Medium --enable-auto-pause true --delay 30