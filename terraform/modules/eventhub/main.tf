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

  name                = each.key
  namespace_name      = azurerm_eventhub_namespace.this.name
  resource_group_name = var.resource_group_name
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
