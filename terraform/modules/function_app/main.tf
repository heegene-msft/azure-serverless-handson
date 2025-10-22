# ===================================================================
# Function App Module (Consumption Plan)
# ===================================================================

data "azurerm_client_config" "current" {}

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

  storage_account_name = var.storage_account_name
  # Use Managed Identity instead of access key
  storage_uses_managed_identity = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    application_stack {
      python_version = var.runtime_version_detail
    }
    
    application_insights_key               = var.app_insights_key
    application_insights_connection_string = var.app_insights_connection_string
  }

  app_settings = merge(
    {
      "FUNCTIONS_WORKER_RUNTIME"       = var.runtime_stack
      "FUNCTIONS_EXTENSION_VERSION"    = var.runtime_version
      "AzureWebJobsStorage__accountName" = var.storage_account_name
      "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
      "ENABLE_ORYX_BUILD"              = "true"
    },
    var.app_settings
  )

  tags = var.tags
}

# Assign Storage Blob Data Owner role to Function App Managed Identity
resource "azurerm_role_assignment" "storage_blob" {
  scope                = var.storage_account_id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = azurerm_linux_function_app.this.identity[0].principal_id
}

# Assign Storage Account Contributor for File Share access
resource "azurerm_role_assignment" "storage_account" {
  scope                = var.storage_account_id
  role_definition_name = "Storage Account Contributor"
  principal_id         = azurerm_linux_function_app.this.identity[0].principal_id
}

# Assign Event Hub Data Receiver role to Function App Managed Identity
resource "azurerm_role_assignment" "eventhub_receiver" {
  scope                = var.eventhub_namespace_id
  role_definition_name = "Azure Event Hubs Data Receiver"
  principal_id         = azurerm_linux_function_app.this.identity[0].principal_id
}

# Assign Event Hub Data Sender role to Function App Managed Identity (for output bindings)
resource "azurerm_role_assignment" "eventhub_sender" {
  scope                = var.eventhub_namespace_id
  role_definition_name = "Azure Event Hubs Data Sender"
  principal_id         = azurerm_linux_function_app.this.identity[0].principal_id
}

# Assign Cosmos DB Built-in Data Contributor role to Function App Managed Identity
# Cosmos DB uses its own RBAC system, not Azure RBAC
resource "azurerm_cosmosdb_sql_role_assignment" "function_app_data_contributor" {
  resource_group_name = var.resource_group_name
  account_name        = var.cosmosdb_account_name
  # Built-in Data Contributor role definition ID
  role_definition_id  = "${var.cosmosdb_account_id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
  principal_id        = azurerm_linux_function_app.this.identity[0].principal_id
  scope               = var.cosmosdb_account_id
}

# ===================================================================
# Function Code Deployment
# ===================================================================

# Create ZIP archive of function code
data "archive_file" "function_code" {
  type        = "zip"
  source_dir  = "${path.root}/../src/functions"
  output_path = "${path.root}/.terraform/function_app.zip"
  excludes = [
    "__pycache__",
    "*.pyc",
    ".venv",
    "venv",
    ".python_packages",
    "local.settings.json",
    ".funcignore"
  ]
}

# Upload deployment package to Blob Storage using Azure CLI
resource "null_resource" "upload_and_deploy" {
  triggers = {
    code_hash              = data.archive_file.function_code.output_md5
    container_ready        = var.deployment_container_id
    role_assignment_ready  = var.storage_role_assignment_id
  }

  provisioner "local-exec" {
    command = <<EOT
      echo "Waiting for role assignment to propagate..."
      sleep 15
      
      echo "Uploading deployment package to Blob Storage..."
      
      # Upload ZIP to Blob Storage
      az storage blob upload \
        --account-name ${var.storage_account_name} \
        --container-name deployments \
        --name "function-${data.archive_file.function_code.output_md5}.zip" \
        --file "${data.archive_file.function_code.output_path}" \
        --auth-mode login \
        --overwrite true
      
      # Get Blob URL
      BLOB_URL=$(az storage blob url \
        --account-name ${var.storage_account_name} \
        --container-name deployments \
        --name "function-${data.archive_file.function_code.output_md5}.zip" \
        --auth-mode login \
        -o tsv)
      
      echo "Setting WEBSITE_RUN_FROM_PACKAGE to: $BLOB_URL"
      
      # Get existing app settings
      EXISTING_SETTINGS=$(az functionapp config appsettings list \
        --name ${azurerm_linux_function_app.this.name} \
        --resource-group ${var.resource_group_name} \
        --query "[?name!='WEBSITE_RUN_FROM_PACKAGE'].{name:name, value:value}" \
        -o json | jq -r 'map("\(.name)=\(.value)") | join(" ")')
      
      # Update Function App setting to use Blob URL (preserving existing settings)
      az functionapp config appsettings set \
        --name ${azurerm_linux_function_app.this.name} \
        --resource-group ${var.resource_group_name} \
        --settings WEBSITE_RUN_FROM_PACKAGE="$BLOB_URL" $EXISTING_SETTINGS
      
      echo "Syncing triggers..."
      az rest --method POST \
        --uri "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${var.resource_group_name}/providers/Microsoft.Web/sites/${azurerm_linux_function_app.this.name}/syncfunctiontriggers?api-version=2022-03-01" \
        || echo "Trigger sync may have failed, but continuing..."
      
      echo "Restarting function app..."
      az functionapp restart \
        --name ${azurerm_linux_function_app.this.name} \
        --resource-group ${var.resource_group_name}
      
      echo "Waiting for Function App to start..."
      sleep 30
      
      echo "Deployment completed!"
    EOT
  }

  depends_on = [
    azurerm_linux_function_app.this,
    azurerm_role_assignment.storage_blob,
    azurerm_role_assignment.storage_account,
    azurerm_role_assignment.eventhub_receiver,
    azurerm_role_assignment.eventhub_sender,
    azurerm_cosmosdb_sql_role_assignment.function_app_data_contributor
  ]
}

# Data source to retrieve function keys (requires function app to be deployed)
data "azurerm_function_app_host_keys" "this" {
  name                = azurerm_linux_function_app.this.name
  resource_group_name = var.resource_group_name

  depends_on = [
    azurerm_linux_function_app.this,
    null_resource.upload_and_deploy
  ]
}
