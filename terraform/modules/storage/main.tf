# ============================================================
# Storage Account Module
# ============================================================

resource "azurerm_storage_account" "this" {
  name                     = var.name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  
  # Security best practices
  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false  # Disabled by Azure Policy
  
  tags = var.tags
}

# Get current user for Data Plane access
data "azurerm_client_config" "current" {}

# Assign Storage Blob Data Contributor to current user for Data Plane operations
resource "azurerm_role_assignment" "current_user_blob_contributor" {
  scope                = azurerm_storage_account.this.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

# Create blob containers using Azure AD authentication
# Requires: provider azurerm { storage_use_azuread = true }
resource "azurerm_storage_container" "containers" {
  for_each = toset(var.containers)

  name                  = each.value
  storage_account_id    = azurerm_storage_account.this.id
  container_access_type = "private"
  
  depends_on = [azurerm_role_assignment.current_user_blob_contributor]
}
