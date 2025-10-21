variable "name" {
  description = "Name of the Function App"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "storage_account_name" {
  description = "Name of the storage account for function app"
  type        = string
}

variable "storage_account_access_key" {
  description = "Access key for the storage account"
  type        = string
  sensitive   = true
}

variable "app_insights_key" {
  description = "Application Insights instrumentation key"
  type        = string
  sensitive   = true
}

variable "app_insights_connection_string" {
  description = "Application Insights connection string"
  type        = string
  sensitive   = true
}

variable "runtime_version" {
  description = "Functions runtime version"
  type        = string
  default     = "~4"
}

variable "runtime_stack" {
  description = "Runtime stack (python, node, dotnet, java)"
  type        = string
  default     = "python"
}

variable "runtime_version_detail" {
  description = "Detailed runtime version (e.g., 3.11 for Python)"
  type        = string
  default     = "3.11"
}

variable "app_settings" {
  description = "Additional app settings"
  type        = map(string)
  default     = {}
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
  default     = {}
}
