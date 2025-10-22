# ============================================================
# Cosmos DB Module
# ============================================================

resource "azurerm_cosmosdb_account" "this" {
  name                = var.account_name
  location            = var.location
  resource_group_name = var.resource_group_name
  offer_type          = var.offer_type
  kind                = "GlobalDocumentDB"

  free_tier_enabled          = var.enable_free_tier
  automatic_failover_enabled = false

  consistency_policy {
    consistency_level       = var.consistency_level
    max_interval_in_seconds = 300
    max_staleness_prefix    = 100000
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }

  tags = var.tags
}

# Create SQL Databases
resource "azurerm_cosmosdb_sql_database" "databases" {
  for_each = var.databases

  name                = each.key
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.this.name
  throughput          = each.value.throughput
}

# Create SQL Containers
resource "azurerm_cosmosdb_sql_container" "containers" {
  for_each = merge([
    for db_key, db in var.databases : {
      for container_key, container in db.containers :
      "${db_key}/${container_key}" => merge(container, {
        database_name = db_key
      })
    }
  ]...)

  name                = split("/", each.key)[1]
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.this.name
  database_name       = azurerm_cosmosdb_sql_database.databases[each.value.database_name].name
  partition_key_paths = [each.value.partition_key_path]
  throughput          = each.value.throughput

  indexing_policy {
    indexing_mode = "consistent"

    included_path {
      path = "/*"
    }

    excluded_path {
      path = "/_etag/?"
    }
  }
}
