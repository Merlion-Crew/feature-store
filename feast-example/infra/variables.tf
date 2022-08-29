# variable "subscription_id" {
# }

# variable "tenant_id" {
# }

# variable "client_id" {
# }

# variable "client_secret" {
# }

/* Required variables */

variable "project_name" {
  description = "Project name that will be used as the prefix of all resources"
  type        = string
}

variable "location" {
  description = "Azure resource location"
  type        = string
}

/* Optional variables */

variable "resource_tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}

variable "key_vault_sku" {
  description = "SKU of the key vault instance to create, possible values are standard and premium"
  type        = string
  default     = "standard"
}

variable "storage_account_tier" {
  description = "Account tier to create for the storage account, possible values are Standard and Premium"
  type        = string
  default     = "Standard"
}

variable "storage_account_replication_type" {
  description = "Replication type to use for the storage account, possible values are LRS, GRS, RAGRS, ZRS, GZRS and RAGZRS"
  type        = string
  default     = "LRS"
}

variable "redis_family" {
  description = "The SKU family/pricing reids group to use for online store, Valid values are C (for Basic/Standard SKU family) and P (for Premium)"
  type        = string
  default     = "C"
}

variable "redis_capacity" {
  description = "The size of the redis cache for online store, possible values for a SKU family of C (Basic/Standard) are 0, 1, 2, 3, 4, 5, 6, and for P (Premium) family are 1, 2, 3, 4"
  type        = number
  default     = 1
}

variable "redis_sku" {
  description = "The SKU of redis online store to use, possible values are Basic, Standard and Premium."
  type        = string
  default     = "Basic"
}

variable "container_registry_sku" {
  description = "SKU of the container registry instance to create, possible values are Basic, Standard and Premium"
  type        = string
  default     = "Standard"
}

variable "gitlab_runner_vm_size" {
  description = "VM size of the virtual machine used for gitlab runner"
  type        = string
  default     = "Standard_B2s"
}

variable "gitlab_runner_admin_username" {
  description = "VM username of the local administrator account"
  type        = string
  default     = "adminuser"
}

variable "gitlab_runner_admin_password" {
  description = "VM password of the local administrator account"
  type        = string
  default     = "Pa55w0rd"
}

variable "gitlab_runner_disk_caching" {
  description = "VM disk caching, possible values include None, ReadOnly and ReadWrite"
  type        = string
  default     = "ReadWrite"
}

variable "gitlab_runner_disk_storage_account_type" {
  description = "VM managed disk storage account type to use, possible values are Attach, FromImage and Empty"
  type        = string
  default     = "StandardSSD_LRS"
}


variable "aks_training_cluster_default_node_pool_node_count" {
  description = "Node count in training cluster"
  type        = number
  default     = 3
}

variable "aks_training_cluster_default_node_pool_vm_size" {
  description = "VM size in training cluster"
  type        = string
  default     = "Standard_B2s"
}

variable "aks_inference_cluster_default_node_pool_node_count" {
  description = "Node count in inference cluster"
  type        = number
  default     = 3
}

variable "aks_inference_cluster_default_node_pool_vm_size" {
  description = "VM size in inference cluster"
  type        = string
  default     = "Standard_B2s"
}

variable "aks_airflow_cluster_default_node_pool_node_count" {
  description = "Node count in airflow cluster"
  type        = number
  default     = 3
}

variable "aks_airflow_cluster_default_node_pool_vm_size" {
  description = "VM size in airflow cluster"
  type        = string
  default     = "Standard_B2s"
}


variable "azureml_inference_cluster_purpose" {
  description = "The purpose of the attached inference cluster in AzureML workspace, possible values are DevTest, DenseProd and FastProd"
  type        = string
  default     = "DevTest"
}
