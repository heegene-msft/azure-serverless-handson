output "namespace_name" {
  description = "Name of the Event Hub Namespace"
  value       = azurerm_eventhub_namespace.this.name
}

output "namespace_id" {
  description = "ID of the Event Hub Namespace"
  value       = azurerm_eventhub_namespace.this.id
}

output "primary_connection_string" {
  description = "Primary connection string for the namespace"
  value       = azurerm_eventhub_namespace_authorization_rule.listen_send.primary_connection_string
  sensitive   = true
}

output "secondary_connection_string" {
  description = "Secondary connection string for the namespace"
  value       = azurerm_eventhub_namespace_authorization_rule.listen_send.secondary_connection_string
  sensitive   = true
}

output "primary_key" {
  description = "Primary key"
  value       = azurerm_eventhub_namespace_authorization_rule.listen_send.primary_key
  sensitive   = true
}

output "eventhub_names" {
  description = "Names of created Event Hubs"
  value       = [for hub in azurerm_eventhub.hubs : hub.name]
}

output "eventhub_ids" {
  description = "Map of Event Hub IDs"
  value       = { for key, hub in azurerm_eventhub.hubs : key => hub.id }
}
