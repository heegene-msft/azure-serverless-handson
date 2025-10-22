output "name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.this.name
}

output "id" {
  description = "ID of the storage account"
  value       = azurerm_storage_account.this.id
}

output "primary_access_key" {
  description = "Primary access key"
  value       = azurerm_storage_account.this.primary_access_key
  sensitive   = true
}

output "primary_connection_string" {
  description = "Primary connection string"
  value       = azurerm_storage_account.this.primary_connection_string
  sensitive   = true
}

output "primary_blob_endpoint" {
  description = "Primary blob endpoint"
  value       = azurerm_storage_account.this.primary_blob_endpoint
}

output "container_names" {
  description = "Names of created containers"
  value       = [for c in azurerm_storage_container.containers : c.name]
}

output "deployment_container_id" {
  description = "ID of the deployments container"
  value       = azurerm_storage_container.containers["deployments"].id
}

output "current_user_role_assignment_id" {
  description = "ID of the role assignment for current user"
  value       = azurerm_role_assignment.current_user_blob_contributor.id
}
