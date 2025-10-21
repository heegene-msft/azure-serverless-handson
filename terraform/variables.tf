# ============================================================
# Common Variables
# ============================================================

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "serverless-handson"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "koreacentral"
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# ============================================================
# Event Hub Variables
# ============================================================

variable "eventhub_sku" {
  description = "SKU for Event Hub Namespace (Basic, Standard, Premium)"
  type        = string
  default     = "Standard"
}

variable "eventhub_capacity" {
  description = "Throughput units for Event Hub"
  type        = number
  default     = 1
}

# ============================================================
# Cosmos DB Variables
# ============================================================

variable "cosmos_enable_free_tier" {
  description = "Enable Cosmos DB free tier (only one per subscription)"
  type        = bool
  default     = false
}

# ============================================================
# API Management Variables
# ============================================================

variable "apim_sku" {
  description = "SKU for API Management (Consumption, Developer, Basic, Standard, Premium)"
  type        = string
  default     = "Consumption"
}

variable "apim_publisher_name" {
  description = "Publisher name for APIM"
  type        = string
  default     = "Serverless Handson"
}

variable "apim_publisher_email" {
  description = "Publisher email for APIM"
  type        = string
  default     = "admin@example.com"
}
