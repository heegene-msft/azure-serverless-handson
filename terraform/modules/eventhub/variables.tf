variable "namespace_name" {
  description = "Name of the Event Hub Namespace"
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

variable "sku" {
  description = "SKU for Event Hub Namespace (Basic, Standard, Premium)"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.sku)
    error_message = "SKU must be Basic, Standard, or Premium."
  }
}

variable "capacity" {
  description = "Throughput units (1-20 for Standard, 1-10 for Premium)"
  type        = number
  default     = 1

  validation {
    condition     = var.capacity >= 1 && var.capacity <= 20
    error_message = "Capacity must be between 1 and 20."
  }
}

variable "eventhubs" {
  description = "Map of Event Hubs to create"
  type = map(object({
    partition_count   = number
    message_retention = number
  }))
  default = {}
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
  default     = {}
}

variable "grant_data_sender_to_current_user" {
  description = "Grant Azure Event Hubs Data Sender role to current user"
  type        = bool
  default     = true
}
