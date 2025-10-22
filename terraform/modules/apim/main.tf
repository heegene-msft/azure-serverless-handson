# ============================================================
# API Management Module
# ============================================================

resource "azurerm_api_management" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  publisher_name      = var.publisher_name
  publisher_email     = var.publisher_email

  sku_name = var.sku_name

  tags = var.tags
}

# Create API for Function App
resource "azurerm_api_management_api" "function_api" {
  name                = "function-api"
  resource_group_name = var.resource_group_name
  api_management_name = azurerm_api_management.this.name
  revision            = "1"
  display_name        = "Function App API"
  path                = "api"
  protocols           = ["https"]

  service_url = "https://${var.function_app_url}"
}

# HTTP Trigger - Process Event (POST)
resource "azurerm_api_management_api_operation" "process_event" {
  operation_id        = "process-event"
  api_name            = azurerm_api_management_api.function_api.name
  api_management_name = azurerm_api_management.this.name
  resource_group_name = var.resource_group_name
  display_name        = "Process Event"
  method              = "POST"
  url_template        = "/process-event"
  description         = "Process event and store in Cosmos DB"

  request {
    representation {
      content_type = "application/json"
    }
  }

  response {
    status_code = 200
    representation {
      content_type = "application/json"
    }
  }
}

# HTTP Trigger - Health Check (GET)
resource "azurerm_api_management_api_operation" "health_check" {
  operation_id        = "health-check"
  api_name            = azurerm_api_management_api.function_api.name
  api_management_name = azurerm_api_management.this.name
  resource_group_name = var.resource_group_name
  display_name        = "Health Check"
  method              = "GET"
  url_template        = "/health"
  description         = "Function App health check endpoint"

  response {
    status_code = 200
    representation {
      content_type = "application/json"
    }
  }
}

# Add policy to include function key
resource "azurerm_api_management_api_policy" "function_policy" {
  api_name            = azurerm_api_management_api.function_api.name
  api_management_name = azurerm_api_management.this.name
  resource_group_name = var.resource_group_name

  xml_content = <<XML
<policies>
  <inbound>
    <base />
    <set-header name="x-functions-key" exists-action="override">
      <value>${var.function_app_key}</value>
    </set-header>
    <rate-limit calls="100" renewal-period="60" />
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>
XML
}
