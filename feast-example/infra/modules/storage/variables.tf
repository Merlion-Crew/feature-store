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

variable "tier" {
  description = "Account tier to create for the storage account, possible values are Standard and Premium"
  type        = string
  default     = "Standard"
}

variable "replication_type" {
  description = "Replication type to use for the storage account, possible values are LRS, GRS, RAGRS, ZRS, GZRS and RAGZRS"
  type        = string
  default     = "LRS"
}

variable "resource_tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
