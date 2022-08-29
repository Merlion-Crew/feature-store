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

variable "resource_tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
