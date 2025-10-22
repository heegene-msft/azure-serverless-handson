# ============================================================
# Azure Serverless Handson - Infrastructure as Code
# ============================================================
# This orchestrates all modules for the serverless architecture
# Event Hub -> APIM -> Functions -> Cosmos DB -> App Insights
# Compatible with both Terraform and OpenTofu

terraform {
  required_version = ">= 1.0"  # OpenTofu 1.6+ also compatible

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.0, < 5.0"  # 4.x 최신 버전 사용
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  subscription_id = var.subscription_id != "" ? var.subscription_id : null
  
  # Use Azure AD authentication for Storage Data Plane operations
  # This allows managing storage containers without shared key access
  storage_use_azuread = true
  
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

  containers = ["deployments"]  # Function code deployment only
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
    device_events = {
      partition_count   = 2
      message_retention = 1
    }
    telemetry_events = {
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
        devices = {
          partition_key_path = "/deviceId"
          throughput         = null # Use database throughput
        }
        events = {
          partition_key_path = "/deviceId"
          throughput         = null
        }
        leases = {
          partition_key_path = "/id"
          throughput         = null # For Cosmos DB Change Feed leases
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

  storage_account_name        = module.storage.name
  storage_account_id          = module.storage.id
  deployment_container_id     = module.storage.deployment_container_id
  storage_role_assignment_id  = module.storage.current_user_role_assignment_id
  eventhub_namespace_id       = module.eventhub.namespace_id
  cosmosdb_account_id               = module.cosmosdb.account_id
  cosmosdb_account_name             = module.cosmosdb.account_name
  app_insights_key                  = module.insights.instrumentation_key
  app_insights_connection_string    = module.insights.connection_string

  # Function code path
  function_code_path     = "${path.root}/../src/functions"

  # Function-specific settings
  runtime_version        = "~4"
  runtime_stack          = "python"
  runtime_version_detail = "3.11"

  app_settings = {
    # Event Hub Settings - Azure AD Authentication (Managed Identity)
    "EventHubConnection__fullyQualifiedNamespace" = "${module.eventhub.namespace_name}.servicebus.windows.net"
    "EventHubConnection__credential"              = "managedidentity"
    EVENTHUB_NAME                                 = "telemetry_events"

    # Cosmos DB Settings - Azure AD Authentication (Managed Identity)
    "CosmosDBConnection__accountEndpoint" = module.cosmosdb.endpoint
    "CosmosDBConnection__credential"      = "managedidentity"
    COSMOS_DB_DATABASE_NAME               = "serverless_db"
    COSMOS_DB_CONTAINER_NAME              = "events"

    # Storage Settings (이미 Managed Identity 사용 중)
    # AzureWebJobsStorage는 function_app 모듈에서 자동 설정됨
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
