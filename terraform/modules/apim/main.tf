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

# Create a basic operation (example)
resource "azurerm_api_management_api_operation" "example_get" {
  operation_id        = "get-example"
  api_name            = azurerm_api_management_api.function_api.name
  api_management_name = azurerm_api_management.this.name
  resource_group_name = var.resource_group_name
  display_name        = "GET Example"
  method              = "GET"
  url_template        = "/*"
  description         = "Example GET operation to Function App"
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
