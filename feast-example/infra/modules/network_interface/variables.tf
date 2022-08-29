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

variable "purpose" {
  description = "The purpose of the network interface to be created, this will be used to name the nic"
  type        = string
}

variable "internal_subnet_vnet_address_space" {
  description = "The vnet address space of the subnet that is used by the internal ip configuration of the nic"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "internal_subnet_address_prefixes" {
  description = "The address prefixes of the subnet that is used by the internal ip configuration of the nic"
  type        = list(string)
  default     = ["10.0.0.0/24"]
}

variable "resource_tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
