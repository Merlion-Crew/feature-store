terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

resource "azurerm_application_insights" "ml_application_insights" {
  name                = local.app_insights_name
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"

  tags = var.resource_tags
}

resource "azurerm_machine_learning_workspace" "ml_workspace" {
  name                    = local.azureml_workspace_name
  location                = var.location
  resource_group_name     = var.resource_group_name
  application_insights_id = azurerm_application_insights.ml_application_insights.id
  key_vault_id            = var.key_vault_id
  storage_account_id      = var.storage_account_id

  tags = var.resource_tags

  // Additional key vault access policies will be granted automatically to the
  // SystemAssigned managed identity when provisioning the workspace.
  identity {
    type         = "SystemAssigned, UserAssigned"
    identity_ids = [var.managed_identity_id]
  }
}

data "azurerm_subscription" "subscription" {
}

data "azurerm_role_definition" "contributer" {
  name  = "Contributor"
  scope = data.azurerm_subscription.subscription.id
}

resource "azurerm_role_assignment" "ml_workspace_contributor_to_managed_identity" {
  scope              = azurerm_machine_learning_workspace.ml_workspace.id
  role_definition_id = data.azurerm_role_definition.contributer.id
  principal_id       = var.managed_identity_principal_id
}

resource "azurerm_machine_learning_inference_cluster" "ml_inference_cluster" {
  name                  = "inferencecluster"
  location              = var.location
  cluster_purpose       = var.inference_cluster_purpose
  kubernetes_cluster_id = var.inference_cluster_id

  machine_learning_workspace_id = azurerm_machine_learning_workspace.ml_workspace.id

  tags = var.resource_tags

  identity {
    type         = "SystemAssigned, UserAssigned"
    identity_ids = [var.managed_identity_id]
  }
}
