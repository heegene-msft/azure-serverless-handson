variable "account_name" {
  description = "Name of the Cosmos DB account"
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

variable "offer_type" {
  description = "Offer type for Cosmos DB"
  type        = string
  default     = "Standard"
}

variable "consistency_level" {
  description = "Consistency level (Eventual, Session, BoundedStaleness, Strong, ConsistentPrefix)"
  type        = string
  default     = "Session"

  validation {
    condition     = contains(["Eventual", "Session", "BoundedStaleness", "Strong", "ConsistentPrefix"], var.consistency_level)
    error_message = "Must be a valid consistency level."
  }
}

variable "enable_free_tier" {
  description = "Enable Cosmos DB free tier (only one per subscription)"
  type        = bool
  default     = false
}

variable "databases" {
  description = "Map of databases and their containers"
  type = map(object({
    throughput = number
    containers = map(object({
      partition_key_path = string
      throughput         = number
    }))
  }))
  default = {}
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
  default     = {}
}
