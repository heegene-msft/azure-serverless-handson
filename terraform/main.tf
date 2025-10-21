# ============================================================
# Azure Serverless Handson - Main Terraform Configuration
# ============================================================
# This orchestrates all modules for the serverless architecture
# Event Hub -> APIM -> Functions -> Cosmos DB -> App Insights

terraform {
  required_version = ">=1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# ============================================================
# Local Variables
# ============================================================
locals {
  resource_prefix = "${var.project_name}-${var.environment}"
  common_tags = merge(
    var.tags,
    {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  )
}

# ============================================================
# Resource Group Module
# ============================================================
module "resource_group" {
  source = "./modules/resource_group"

  name     = "${local.resource_prefix}-rg"
  location = var.location
  tags     = local.common_tags
}

# ============================================================
# Application Insights Module
# ============================================================
module "insights" {
  source = "./modules/insights"

  name                = "${local.resource_prefix}-insights"
  location            = var.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags
}

# ============================================================
# Storage Account Module
# ============================================================
module "storage" {
  source = "./modules/storage"

  name                = replace("${local.resource_prefix}sa", "-", "")
  location            = var.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags

  containers = ["products", "results", "samples"]
}

# ============================================================
# Event Hub Module
# ============================================================
module "eventhub" {
  source = "./modules/eventhub"

  namespace_name      = "${local.resource_prefix}-evhns"
  location            = var.location
  resource_group_name = module.resource_group.name
  sku                 = var.eventhub_sku
  capacity            = var.eventhub_capacity
  tags                = local.common_tags

  eventhubs = {
    product_events = {
      partition_count   = 2
      message_retention = 1
    }
    order_events = {
      partition_count   = 2
      message_retention = 1
    }
  }
}

# ============================================================
# Cosmos DB Module
# ============================================================
module "cosmosdb" {
  source = "./modules/cosmosdb"

  account_name        = "${local.resource_prefix}-cosmos"
  location            = var.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags

  offer_type          = "Standard"
  consistency_level   = "Session"
  enable_free_tier    = var.cosmos_enable_free_tier

  databases = {
    serverless_db = {
      throughput = 400
      containers = {
        products = {
          partition_key_path = "/pk"
          throughput         = null # Use database throughput
        }
        events = {
          partition_key_path = "/eventType"
          throughput         = null
        }
      }
    }
  }
}

# ============================================================
# Function App Module
# ============================================================
module "function_app" {
  source = "./modules/function_app"

  name                = "${local.resource_prefix}-func"
  location            = var.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags

  storage_account_name       = module.storage.name
  storage_account_access_key = module.storage.primary_access_key
  app_insights_key           = module.insights.instrumentation_key
  app_insights_connection_string = module.insights.connection_string

  # Function-specific settings
  runtime_version = "~4"
  runtime_stack   = "python"
  runtime_version_detail = "3.11"

  app_settings = {
    # Event Hub Settings
    EVENTHUB_CONNECTION_STRING = module.eventhub.primary_connection_string
    EVENTHUB_NAME             = "product_events"

    # Cosmos DB Settings
    COSMOS_DB_CONNECTION_STRING = module.cosmosdb.primary_connection_string
    COSMOS_DB_DATABASE_NAME     = "serverless_db"
    COSMOS_DB_CONTAINER_NAME    = "products"

    # Storage Settings
    STORAGE_CONNECTION_STRING = module.storage.primary_connection_string
  }
}

# ============================================================
# API Management Module
# ============================================================
module "apim" {
  source = "./modules/apim"

  name                = "${local.resource_prefix}-apim"
  location            = var.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags

  sku_name            = var.apim_sku
  publisher_name      = var.apim_publisher_name
  publisher_email     = var.apim_publisher_email

  function_app_url    = module.function_app.default_hostname
  function_app_key    = module.function_app.default_function_key
}
