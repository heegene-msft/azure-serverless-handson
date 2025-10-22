# ================================================================
# Azure Serverless Handson - Infrastructure as Code
# ================================================================
# This configuration creates a complete serverless architecture
# for event-driven data processing on Azure.
# 
# Compatible with both Terraform and OpenTofu

## 📋 Architecture

```
Event → Event Hub → APIM → Functions → Cosmos DB
                                    ↓
                            App Insights
```

## 🎯 Resources Created

1. **Resource Group** - Container for all resources
2. **Storage Account** - Blob storage for functions and data
3. **Event Hub** - Event streaming platform
4. **Cosmos DB** - NoSQL database with change feed
5. **Function App** - Serverless compute (Python 3.11)
6. **API Management** - API gateway with policies
7. **Application Insights** - Monitoring and diagnostics

## 🚀 Getting Started

### Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0 **OR** [OpenTofu](https://opentofu.org/docs/intro/install/) >= 1.6
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- Azure subscription

### Installation Steps

#### Option 1: Using Terraform

1. **Login to Azure**
   ```bash
   az login
   az account set --subscription "<your-subscription-id>"
   ```

2. **Initialize**
   ```bash
   cd terraform
   terraform init  # or: tofu init
   ```

3. **Review and Modify Variables**
   Edit `terraform.tfvars` to customize your deployment:
   ```hcl
   project_name = "serverless-handson"       # 프로젝트명
   location     = "koreacentral"             # 혹은 원하시는 리전
   apim_publisher_email = "your-email@example.com"
   ```

4. **Plan the Deployment**
   ```bash
   terraform plan -out=tfplan  # or: tofu plan -out=tfplan
   ```

5. **Apply the Configuration**
   ```bash
   terraform apply tfplan      # or: tofu apply tfplan
   ```

## 📁 Project Structure

```
terraform/
├── main.tf                  # Main orchestration
├── variables.tf             # Variable definitions
├── outputs.tf               # Output definitions
├── backend.tf               # Remote state configuration (optional)
├── terraform.tfvars         # Variable values
├── modules/
│   ├── resource_group/      # Resource group module
│   ├── storage/             # Storage account module
│   ├── eventhub/            # Event Hub module
│   ├── cosmosdb/            # Cosmos DB module
│   ├── function_app/        # Function App module
│   ├── apim/                # API Management module
│   └── insights/            # Application Insights module
└── env/
    └── dev.tfvars           # Environment-specific variables
```

## 🔧 Configuration

### Key Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `project_name` | Project name prefix | `serverless-handson` |
| `environment` | Environment name | `dev` |
| `location` | Azure region | `koreacentral` |
| `eventhub_sku` | Event Hub SKU | `Standard` |
| `cosmos_enable_free_tier` | Enable Cosmos free tier | `false` |
| `apim_sku` | APIM SKU | `Consumption` |

### Outputs

After deployment, the tool will output important information:

```bash
terraform output  # or: tofu output
```

Key outputs:
- `resource_group_name` - Name of the created resource group
- `eventhub_connection_string` - Event Hub connection string (sensitive)
- `cosmosdb_connection_string` - Cosmos DB connection string (sensitive)
- `function_app_url` - Function App URL
- `apim_gateway_url` - API Management gateway URL

To view sensitive outputs:
```bash
terraform output -json > outputs.json  # or: tofu output -json > outputs.json
```

## 🔐 Security Best Practices

1. **Enable Remote State** (Recommended for teams)
   - Uncomment backend configuration in `backend.tf`
   - Create Azure Storage for state file
   - Run `terraform init -migrate-state` or `tofu init -migrate-state`

2. **Protect Sensitive Data**
   - Never commit `.tfstate` or `.tfstate.backup` files
   - Use Azure Key Vault for secrets
   - Enable RBAC on all resources

3. **Network Security**
   - Configure VNet integration for Function Apps
   - Enable private endpoints for Cosmos DB
   - Use Azure Firewall or NSGs

## 🧹 Cleanup

To destroy all resources:

```bash
terraform destroy  # or: tofu destroy
```

⚠️ **Warning**: This will permanently delete all resources.


## 📚 Next Steps

1. Deploy Azure Functions code (see `/src/functions`)
2. Configure Event producers (see `/src/producer`)
3. Run integration tests (see `/tests`)
4. Set up monitoring dashboards in Application Insights

## 🐛 Troubleshooting

### Common Issues

**Issue**: `terraform init` or `tofu init` fails
- **Solution**: Check Azure CLI authentication with `az account show`

**Issue**: Function App won't start
- **Solution**: Check Application Insights connection in portal

**Issue**: APIM deployment takes too long
- **Solution**: Consumption tier APIM deploys in ~5 min, other tiers 30-45 min

## 🔄 Migrating from Terraform to OpenTofu

If you have existing Terraform state and want to migrate to OpenTofu:

1. **Install OpenTofu** (see Prerequisites above)

2. **Backup your state**
   ```bash
   cp terraform.tfstate terraform.tfstate.backup
   ```

3. **Initialize OpenTofu**
   ```bash
   tofu init
   ```

4. **Verify the migration**
   ```bash
   tofu plan
   ```

OpenTofu is a drop-in replacement for Terraform. Your existing `.tf` files and state will work without modification.

## 📖 References

- [Azure Terraform Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [OpenTofu Documentation](https://opentofu.org/docs/)
- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Event Hubs Documentation](https://docs.microsoft.com/en-us/azure/event-hubs/)
- [Cosmos DB Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/)

## 📝 License

MIT License
