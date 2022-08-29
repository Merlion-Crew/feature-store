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

variable "managed_identity_principal_id" {
  description = "Object ID of the managed identity that will be used for resource user assigned identity and assigned necessary access policies"
  type        = string
}

variable "managed_identity_tenant_id" {
  description = "Tenant ID of the managed identity that will be used for resource user assigned identity and assigned necessary access policies"
  type        = string
}

variable "sku" {
  description = "SKU of the key vault instance to create, possible values are standard and premium"
  type        = string
  default     = "standard"
}

variable "resource_tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
