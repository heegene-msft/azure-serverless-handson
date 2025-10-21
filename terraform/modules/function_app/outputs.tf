output "name" {
  description = "Name of the Function App"
  value       = azurerm_linux_function_app.this.name
}

output "id" {
  description = "ID of the Function App"
  value       = azurerm_linux_function_app.this.id
}

output "default_hostname" {
  description = "Default hostname of the Function App"
  value       = azurerm_linux_function_app.this.default_hostname
}

output "default_function_key" {
  description = "Default function key"
  value       = try(data.azurerm_function_app_host_keys.this.default_function_key, "")
  sensitive   = true
}

output "outbound_ip_addresses" {
  description = "Outbound IP addresses"
  value       = azurerm_linux_function_app.this.outbound_ip_addresses
}
