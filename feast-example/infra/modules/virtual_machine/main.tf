terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

resource "azurerm_linux_virtual_machine" "vm" {
  name                            = local.vm_name
  resource_group_name             = var.resource_group_name
  location                        = var.location
  size                            = var.vm_size
  admin_username                  = var.admin_username
  admin_password                  = var.admin_password
  disable_password_authentication = false

  network_interface_ids = [var.nic_id]

  os_disk {
    caching              = var.disk_caching
    storage_account_type = var.disk_storage_account_type
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

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

resource "azurerm_role_assignment" "contributor_to_managed_identity" {
  scope              = azurerm_linux_virtual_machine.vm.id
  role_definition_id = data.azurerm_role_definition.contributer.id
  principal_id       = var.managed_identity_principal_id
}
