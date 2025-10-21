# ===================================================================
# Function App Module (Consumption Plan)
# ===================================================================

resource "azurerm_service_plan" "this" {
  name                = "${var.name}-plan"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  sku_name            = "Y1" # Consumption plan

  tags = var.tags
}

resource "azurerm_linux_function_app" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = azurerm_service_plan.this.id

  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_account_access_key

  site_config {
    application_stack {
      python_version = var.runtime_version_detail
    }
    
    application_insights_key               = var.app_insights_key
    application_insights_connection_string = var.app_insights_connection_string
  }

  app_settings = merge(
    {
      "FUNCTIONS_WORKER_RUNTIME"     = var.runtime_stack
      "FUNCTIONS_EXTENSION_VERSION"  = var.runtime_version
      "WEBSITE_RUN_FROM_PACKAGE"     = "1"
    },
    var.app_settings
  )

  tags = var.tags
}

# Data source to retrieve function keys (requires function app to be deployed)
data "azurerm_function_app_host_keys" "this" {
  name                = azurerm_linux_function_app.this.name
  resource_group_name = var.resource_group_name

  depends_on = [azurerm_linux_function_app.this]
}
