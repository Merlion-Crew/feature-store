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

variable "managed_identity_id" {
  description = "ID of the managed identity that will be used for resource user assigned identity and assigned necessary access policies"
  type        = string
}

variable "managed_identity_principal_id" {
  description = "Object ID of the managed identity that will be used for resource user assigned identity and assigned necessary access policies"
  type        = string
}

variable "purpose" {
  description = "The purpose of the AKS cluster created, this will be used in the name and the dns prefix of the cluster"
  type        = string
}

variable "default_node_pool_node_count" {
  description = "Default node pool node count in aks cluster"
  type        = number
  default     = 3
}

variable "default_node_pool_vm_size" {
  description = "Default node pool VM size in aks cluster"
  type        = string
  default     = "Standard_B2s"
}

variable "resource_tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
