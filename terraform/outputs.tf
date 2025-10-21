# ============================================================
# Terraform Outputs
# ============================================================
# These outputs will be used by Python test scripts

output "resource_group_name" {
  description = "Name of the resource group"
  value       = module.resource_group.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = module.resource_group.location
}

# ============================================================
# Storage Account Outputs
# ============================================================

output "storage_account_name" {
  description = "Name of the storage account"
  value       = module.storage.name
}

output "storage_connection_string" {
  description = "Connection string for storage account"
  value       = module.storage.primary_connection_string
  sensitive   = true
}

output "storage_blob_endpoint" {
  description = "Blob endpoint for storage account"
  value       = module.storage.primary_blob_endpoint
}

# ============================================================
# Event Hub Outputs
# ============================================================

output "eventhub_namespace" {
  description = "Event Hub namespace name"
  value       = module.eventhub.namespace_name
}

output "eventhub_connection_string" {
  description = "Event Hub connection string"
  value       = module.eventhub.primary_connection_string
  sensitive   = true
}

output "eventhub_names" {
  description = "Names of created event hubs"
  value       = module.eventhub.eventhub_names
}

# ============================================================
# Cosmos DB Outputs
# ============================================================

output "cosmosdb_account_name" {
  description = "Cosmos DB account name"
  value       = module.cosmosdb.account_name
}

output "cosmosdb_endpoint" {
  description = "Cosmos DB endpoint"
  value       = module.cosmosdb.endpoint
}

output "cosmosdb_connection_string" {
  description = "Cosmos DB connection string"
  value       = module.cosmosdb.primary_connection_string
  sensitive   = true
}

output "cosmosdb_primary_key" {
  description = "Cosmos DB primary key"
  value       = module.cosmosdb.primary_key
  sensitive   = true
}

# ============================================================
# Function App Outputs
# ============================================================

output "function_app_name" {
  description = "Name of the Function App"
  value       = module.function_app.name
}

output "function_app_hostname" {
  description = "Default hostname of the Function App"
  value       = module.function_app.default_hostname
}

output "function_app_url" {
  description = "Full URL of the Function App"
  value       = "https://${module.function_app.default_hostname}"
}

# ============================================================
# Application Insights Outputs
# ============================================================

output "app_insights_name" {
  description = "Name of Application Insights"
  value       = module.insights.name
}

output "app_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = module.insights.instrumentation_key
  sensitive   = true
}

output "app_insights_connection_string" {
  description = "Application Insights connection string"
  value       = module.insights.connection_string
  sensitive   = true
}

# ============================================================
# API Management Outputs
# ============================================================

output "apim_name" {
  description = "Name of API Management"
  value       = module.apim.name
}

output "apim_gateway_url" {
  description = "Gateway URL for API Management"
  value       = module.apim.gateway_url
}

output "apim_portal_url" {
  description = "Developer portal URL for API Management"
  value       = module.apim.developer_portal_url
}
