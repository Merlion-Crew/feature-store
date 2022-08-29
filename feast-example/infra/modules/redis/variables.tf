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

variable "family" {
  description = "The SKU family/pricing reids group to use for online store, Valid values are C (for Basic/Standard SKU family) and P (for Premium)"
  type        = string
  default     = "C"
}

variable "capacity" {
  description = "The size of the redis cache for online store, possible values for a SKU family of C (Basic/Standard) are 0, 1, 2, 3, 4, 5, 6, and for P (Premium) family are 1, 2, 3, 4"
  type        = number
  default     = 1
}

variable "sku" {
  description = "The SKU of redis online store to use, possible values are Basic, Standard and Premium."
  type        = string
  default     = "Basic"
}

variable "resource_tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
