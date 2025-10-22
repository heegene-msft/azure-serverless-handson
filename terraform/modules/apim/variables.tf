variable "name" {
  description = "Name of the API Management instance"
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

variable "publisher_name" {
  description = "Publisher name for APIM"
  type        = string
}

variable "publisher_email" {
  description = "Publisher email for APIM"
  type        = string
}

variable "sku_name" {
  description = "SKU name in format {tier}_{capacity} (e.g., Consumption_0, Developer_1, Basic_1, Standard_1, Premium_1)"
  type        = string
  default     = "Consumption_0"

  validation {
    condition     = can(regex("^(Consumption_0|Developer_[1-9]|Basic_[1-4]|Standard_[1-4]|Premium_[1-9][0-9]*)$", var.sku_name))
    error_message = "SKU must be in format {tier}_{capacity}. Examples: Consumption_0, Developer_1, Basic_1, Standard_1, Premium_1"
  }
}

variable "function_app_url" {
  description = "URL of the Function App"
  type        = string
}

variable "function_app_key" {
  description = "Function App host key"
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
  default     = {}
}
