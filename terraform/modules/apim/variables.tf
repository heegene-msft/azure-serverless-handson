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
  description = "SKU name (Consumption, Developer, Basic, Standard, Premium)"
  type        = string
  default     = "Consumption"
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
