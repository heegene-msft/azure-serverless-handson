# ============================================================
# Terraform Backend Configuration (Optional)
# ============================================================
# Uncomment and configure this to use Azure Storage for remote state
# This is recommended for team collaboration and CI/CD pipelines

# terraform {
#   backend "azurerm" {
#     resource_group_name  = "terraform-state-rg"
#     storage_account_name = "tfstatestorage"
#     container_name       = "tfstate"
#     key                  = "serverless-handson.tfstate"
#   }
# }

# To enable remote state:
# 1. Create a resource group: az group create --name terraform-state-rg --location koreacentral
# 2. Create a storage account: az storage account create --name tfstatestorage --resource-group terraform-state-rg --location koreacentral --sku Standard_LRS
# 3. Create a container: az storage container create --name tfstate --account-name tfstatestorage
# 4. Uncomment the backend block above
# 5. Run: terraform init -migrate-state
