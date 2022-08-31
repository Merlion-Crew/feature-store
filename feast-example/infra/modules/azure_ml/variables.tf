variable "project_name" {
  description = "Project name that will be used as the prefix of all resources"
  type        = string
}

variable "location" {
  description = "Azure resource location"
  type        = string
}

variable "resource_group_name" {
  description = "Azure resource group name where all resources will be created"
  type        = string
}

variable "key_vault_id" {
  description = "ID of the key vault resource"
  type        = string
}

variable "storage_account_id" {
  description = "ID of the storage account"
  type        = string
}

variable "managed_identity_id" {
  description = "ID of the managed identity that will be used for resource user assigned identity and assigned necessary access policies"
  type        = string
}

variable "managed_identity_principal_id" {
  description = "Object ID of the managed identity that will be used for resource user assigned identity and assigned necessary access policies"
  type        = string
}

variable "inference_cluster_id" {
  description = "ID of the Kubeernetes cluster that will be used for inference usage"
  type        = string
}

variable "inference_cluster_purpose" {
  description = "The purpose of the Inference Cluster. Options are DevTest, DenseProd and FastProd."
  type        = string
  default     = "DevTest"
}

variable "resource_tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
