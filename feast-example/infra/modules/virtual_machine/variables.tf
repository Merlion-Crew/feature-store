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

variable "nic_id" {
  description = "The network interface id that the VM will be attached to"
  type        = string
}

variable "vm_size" {
  description = "VM size of the virtual machine"
  type        = string
  default     = "Standard_B2s"
}

variable "admin_username" {
  description = "VM username of the local administrator account"
  type        = string
  default     = "adminuser"
}

variable "admin_password" {
  description = "VM password of the local administrator account"
  type        = string
  default     = "Pa55w0rd"
}

variable "disk_caching" {
  description = "VM disk caching, possible values include None, ReadOnly and ReadWrite"
  type        = string
  default     = "ReadWrite"
}

variable "disk_storage_account_type" {
  description = "VM managed disk storage account type to use, possible values are Attach, FromImage and Empty"
  type        = string
  default     = "StandardSSD_LRS"
}

variable "resource_tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
