output "name" {
  description = "Name of API Management"
  value       = azurerm_api_management.this.name
}

output "id" {
  description = "ID of API Management"
  value       = azurerm_api_management.this.id
}

output "gateway_url" {
  description = "Gateway URL"
  value       = azurerm_api_management.this.gateway_url
}

output "developer_portal_url" {
  description = "Developer portal URL"
  value       = azurerm_api_management.this.developer_portal_url
}
