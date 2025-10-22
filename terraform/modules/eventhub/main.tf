# ============================================================
# Event Hub Module
# ============================================================

resource "azurerm_eventhub_namespace" "this" {
  name                = var.namespace_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.sku
  capacity            = var.capacity

  # Security best practices
  minimum_tls_version = "1.2"
  
  tags = var.tags
}

# Create Event Hubs within the namespace
resource "azurerm_eventhub" "hubs" {
  for_each = var.eventhubs

  name           = each.key
  namespace_id   = azurerm_eventhub_namespace.this.id
  partition_count     = each.value.partition_count
  message_retention   = each.value.message_retention
}

# Create authorization rules for the namespace (for easier access)
resource "azurerm_eventhub_namespace_authorization_rule" "listen_send" {
  name                = "ListenSendRule"
  namespace_name      = azurerm_eventhub_namespace.this.name
  resource_group_name = var.resource_group_name

  listen = true
  send   = true
  manage = false
}

# Get current client (user/service principal deploying Terraform)
data "azurerm_client_config" "current" {}

# Grant Azure Event Hubs Data Sender role to current user for local development
resource "azurerm_role_assignment" "current_user_data_sender" {
  count = var.grant_data_sender_to_current_user ? 1 : 0

  scope                = azurerm_eventhub_namespace.this.id
  role_definition_name = "Azure Event Hubs Data Sender"
  principal_id         = data.azurerm_client_config.current.object_id
}

# Grant Azure Event Hubs Data Receiver role to current user for local development
resource "azurerm_role_assignment" "current_user_data_receiver" {
  count = var.grant_data_sender_to_current_user ? 1 : 0

  scope                = azurerm_eventhub_namespace.this.id
  role_definition_name = "Azure Event Hubs Data Receiver"
  principal_id         = data.azurerm_client_config.current.object_id
}
