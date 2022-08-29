locals {
  vnet_name              = "${var.project_name}-${var.purpose}-vnet"
  subnet_name            = "${var.project_name}-${var.purpose}-subnet"
  network_interface_name = "${var.project_name}-${var.purpose}-nic"
}
