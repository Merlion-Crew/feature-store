terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {}
  # subscription_id = var.subscription_id
  # tenant_id       = var.tenant_id
  # client_id       = var.client_id
  # client_secret   = var.client_secret
}

module "resource_group" {
  source = "./modules/resource_group"

  project_name = var.project_name
  location     = var.location

  resource_tags = var.resource_tags
}

module "managed_identity" {
  source = "./modules/managed_identity"

  project_name        = var.project_name
  location            = var.location
  resource_group_name = module.resource_group.resource_group_name

  resource_tags = var.resource_tags
}

module "key_vault" {
  source = "./modules/key_vault"

  project_name                  = var.project_name
  location                      = var.location
  resource_group_name           = module.resource_group.resource_group_name
  managed_identity_principal_id = module.managed_identity.managed_identity_principal_id
  managed_identity_tenant_id    = module.managed_identity.managed_identity_tenant_id
  sku                           = var.key_vault_sku

  resource_tags = var.resource_tags
}

module "storage_account" {
  source = "./modules/storage"

  project_name                  = var.project_name
  location                      = var.location
  resource_group_name           = module.resource_group.resource_group_name
  managed_identity_principal_id = module.managed_identity.managed_identity_principal_id
  tier                          = var.storage_account_tier
  replication_type              = var.storage_account_replication_type

  resource_tags = var.resource_tags
}

module "redis_online_store" {
  source = "./modules/redis"

  project_name                  = var.project_name
  location                      = var.location
  resource_group_name           = module.resource_group.resource_group_name
  managed_identity_principal_id = module.managed_identity.managed_identity_principal_id
  family                        = var.redis_family
  capacity                      = var.redis_capacity
  sku                           = var.redis_sku

  resource_tags = var.resource_tags
}

module "container_registry" {
  source = "./modules/container_registry"

  project_name                  = var.project_name
  location                      = var.location
  resource_group_name           = module.resource_group.resource_group_name
  managed_identity_principal_id = module.managed_identity.managed_identity_principal_id
  sku                           = var.container_registry_sku

  resource_tags = var.resource_tags
}

module "gitlab_runner_nic" {
  source = "./modules/network_interface"

  project_name        = var.project_name
  location            = var.location
  resource_group_name = module.resource_group.resource_group_name
  purpose             = "gitlab-runner"

  resource_tags = var.resource_tags
}

module "gitlab_runner_vm" {
  source = "./modules/virtual_machine"

  project_name                  = var.project_name
  location                      = var.location
  resource_group_name           = module.resource_group.resource_group_name
  managed_identity_id           = module.managed_identity.managed_identity_id
  managed_identity_principal_id = module.managed_identity.managed_identity_principal_id
  nic_id                        = module.gitlab_runner_nic.nic_id
  vm_size                       = var.gitlab_runner_vm_size
  admin_username                = var.gitlab_runner_admin_username
  admin_password                = var.gitlab_runner_admin_password
  disk_caching                  = var.gitlab_runner_disk_caching
  disk_storage_account_type     = var.gitlab_runner_disk_storage_account_type

  resource_tags = var.resource_tags
}

module "aks_training_cluster" {
  source = "./modules/kubernetes"

  project_name                  = var.project_name
  location                      = var.location
  resource_group_name           = module.resource_group.resource_group_name
  managed_identity_id           = module.managed_identity.managed_identity_id
  managed_identity_principal_id = module.managed_identity.managed_identity_principal_id
  purpose                       = "training"
  default_node_pool_node_count  = var.aks_training_cluster_default_node_pool_node_count
  default_node_pool_vm_size     = var.aks_training_cluster_default_node_pool_vm_size

  resource_tags = var.resource_tags
}

module "aks_inference_cluster" {
  source = "./modules/kubernetes"

  project_name                  = var.project_name
  location                      = var.location
  resource_group_name           = module.resource_group.resource_group_name
  managed_identity_id           = module.managed_identity.managed_identity_id
  managed_identity_principal_id = module.managed_identity.managed_identity_principal_id
  purpose                       = "inference"
  default_node_pool_node_count  = var.aks_inference_cluster_default_node_pool_node_count
  default_node_pool_vm_size     = var.aks_inference_cluster_default_node_pool_vm_size

  resource_tags = var.resource_tags
}

module "aks_airflow_cluster" {
  source = "./modules/kubernetes"

  project_name                  = var.project_name
  location                      = var.location
  resource_group_name           = module.resource_group.resource_group_name
  managed_identity_id           = module.managed_identity.managed_identity_id
  managed_identity_principal_id = module.managed_identity.managed_identity_principal_id
  purpose                       = "airflow"
  default_node_pool_node_count  = var.aks_airflow_cluster_default_node_pool_node_count
  default_node_pool_vm_size     = var.aks_airflow_cluster_default_node_pool_vm_size

  resource_tags = var.resource_tags
}

module "azure_ml" {
  source = "./modules/azure_ml"

  project_name                  = var.project_name
  location                      = var.location
  resource_group_name           = module.resource_group.resource_group_name
  key_vault_id                  = module.key_vault.key_vault_id
  storage_account_id            = module.storage_account.storage_account_id
  managed_identity_id           = module.managed_identity.managed_identity_id
  managed_identity_principal_id = module.managed_identity.managed_identity_principal_id
  inference_cluster_id          = module.aks_inference_cluster.cluster_id
  inference_cluster_purpose     = var.azureml_inference_cluster_purpose

  resource_tags = var.resource_tags
}
