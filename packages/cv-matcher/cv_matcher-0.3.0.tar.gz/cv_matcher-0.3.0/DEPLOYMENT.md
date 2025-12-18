# Azure Deployment Guide

This guide covers deploying the CV Matcher application to Azure using GitHub Actions.

## Prerequisites

1. **Azure Account**: Sign up at [portal.azure.com](https://portal.azure.com)
2. **Azure CLI**: Install from [docs.microsoft.com/cli/azure/install-azure-cli](https://docs.microsoft.com/cli/azure/install-azure-cli)
3. **GitHub Repository**: Your cv-matcher repository
4. **OpenAI API Key**: Required for the application

## Deployment Options

### Option 1: Azure App Service (Recommended for Quick Start)

#### 1. Create Azure App Service

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-cv-matcher --location eastus

# Create App Service plan
az appservice plan create \
  --name plan-cv-matcher \
  --resource-group rg-cv-matcher \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --name cv-matcher \
  --resource-group rg-cv-matcher \
  --plan plan-cv-matcher \
  --runtime "PYTHON:3.11"

# Configure startup command
az webapp config set \
  --name cv-matcher \
  --resource-group rg-cv-matcher \
  --startup-file "startup.sh"
```

#### 2. Get Publish Profile

```bash
az webapp deployment list-publishing-profiles \
  --name cv-matcher \
  --resource-group rg-cv-matcher \
  --xml
```

Copy the entire XML output.

#### 3. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `AZURE_WEBAPP_PUBLISH_PROFILE`: Paste the XML from step 2
- `OPENAI_API_KEY`: Your OpenAI API key

#### 4. Deploy

Push to main branch or trigger manually:
```bash
git push origin main
```

Or manually trigger from GitHub Actions tab.

#### 5. Access Your App

Your app will be available at: `https://cv-matcher.azurewebsites.net`

---

### Option 2: Azure Container Apps (More Flexible)

#### 1. Create Azure Container Registry

```bash
# Create ACR
az acr create \
  --name cvmatchercr \
  --resource-group rg-cv-matcher \
  --sku Basic \
  --admin-enabled true

# Get ACR credentials
az acr credential show --name cvmatchercr
```

#### 2. Create Container App Environment

```bash
# Create environment
az containerapp env create \
  --name cv-matcher-env \
  --resource-group rg-cv-matcher \
  --location eastus

# Create container app
az containerapp create \
  --name cv-matcher \
  --resource-group rg-cv-matcher \
  --environment cv-matcher-env \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --target-port 7860 \
  --ingress external \
  --query properties.configuration.ingress.fqdn
```

#### 3. Get Azure Service Principal

```bash
az ad sp create-for-rbac \
  --name "github-cv-matcher-deploy" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/rg-cv-matcher \
  --sdk-auth
```

Copy the entire JSON output.

#### 4. Configure GitHub Secrets

Add these secrets to your repository:
- `AZURE_CREDENTIALS`: Paste the JSON from step 3
- `OPENAI_API_KEY`: Your OpenAI API key

Update the workflow file `.github/workflows/deploy-azure-container.yml`:
- Set `AZURE_CONTAINER_REGISTRY` to your ACR name (e.g., `cvmatchercr`)
- Set `AZURE_RESOURCE_GROUP` to your resource group name
- Set `AZURE_CONTAINER_APP_NAME` to your container app name

#### 5. Deploy

```bash
git push origin main
```

Or trigger manually from GitHub Actions.

#### 6. Access Your App

Get the URL:
```bash
az containerapp show \
  --name cv-matcher \
  --resource-group rg-cv-matcher \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

---

## Local Docker Testing

Before deploying, test the Docker image locally:

```bash
# Build image
docker build -t cv-matcher .

# Run container
docker run -p 7860:7860 \
  -e OPENAI_API_KEY=your-key-here \
  -e USE_LOCAL_MODEL=false \
  cv-matcher

# Access at http://localhost:7860
```

---

## Environment Variables

Configure these in Azure:

### App Service
```bash
az webapp config appsettings set \
  --name cv-matcher \
  --resource-group rg-cv-matcher \
  --settings \
    USE_LOCAL_MODEL=false \
    OPENAI_API_KEY=your-key-here
```

### Container Apps
```bash
az containerapp update \
  --name cv-matcher \
  --resource-group rg-cv-matcher \
  --set-env-vars \
    USE_LOCAL_MODEL=false \
    OPENAI_API_KEY=your-key-here
```

---

## Monitoring

### View Logs (App Service)
```bash
az webapp log tail \
  --name cv-matcher \
  --resource-group rg-cv-matcher
```

### View Logs (Container Apps)
```bash
az containerapp logs show \
  --name cv-matcher \
  --resource-group rg-cv-matcher \
  --follow
```

---

## Scaling

### App Service
```bash
# Scale up (more powerful instance)
az appservice plan update \
  --name plan-cv-matcher \
  --resource-group rg-cv-matcher \
  --sku P1V2

# Scale out (more instances)
az appservice plan update \
  --name plan-cv-matcher \
  --resource-group rg-cv-matcher \
  --number-of-workers 3
```

### Container Apps
```bash
az containerapp update \
  --name cv-matcher \
  --resource-group rg-cv-matcher \
  --min-replicas 1 \
  --max-replicas 5
```

---

## Troubleshooting

### App Service Issues
```bash
# Check deployment status
az webapp deployment list \
  --name cv-matcher \
  --resource-group rg-cv-matcher

# Restart app
az webapp restart \
  --name cv-matcher \
  --resource-group rg-cv-matcher
```

### Container App Issues
```bash
# Get revision details
az containerapp revision list \
  --name cv-matcher \
  --resource-group rg-cv-matcher

# Restart container app
az containerapp revision restart \
  --name cv-matcher \
  --resource-group rg-cv-matcher
```

### Common Issues

1. **Port binding error**: Ensure `GRADIO_SERVER_PORT` matches Azure's expected port
2. **OpenAI key not found**: Verify `OPENAI_API_KEY` secret is set correctly
3. **Timeout errors**: Increase request timeout in Azure portal
4. **Memory issues**: Upgrade to a higher SKU/tier

---

## Cost Optimization

### Free Tier Options
- **App Service**: F1 tier (free, limited)
- **Container Apps**: Pay per request (minimal cost for low traffic)

### Recommended Tiers
- **Development**: B1 ($~13/month)
- **Production**: P1V2 ($~70/month) with autoscaling

### Cost Saving Tips
1. Use auto-shutdown for dev/test environments
2. Enable autoscaling based on traffic
3. Use Azure Reserved Instances for production
4. Monitor costs in Azure Cost Management

---

## Security Best Practices

1. **Use Azure Key Vault** for storing secrets
2. **Enable HTTPS** only (default)
3. **Restrict IP access** if needed
4. **Enable authentication** (Azure AD, etc.)
5. **Regular security updates** via GitHub Actions

---

## Next Steps

1. Set up custom domain
2. Configure SSL certificate
3. Enable Application Insights for monitoring
4. Set up Azure Front Door for CDN
5. Configure backup and disaster recovery

For more information, visit [Azure Documentation](https://docs.microsoft.com/azure/).
