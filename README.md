# GPT Realtime Starter Kit

A starter kit for building realtime speech-to-speech applications using the GPT Realtime API (`gpt-realtime-1.5`) on Azure AI Foundry.

## Project Structure

```
├── assets/                        # Static assets
├── frontend/                      # Frontend application
├── hooks/
│   ├── postprovision.ps1          # Post-provision hook (Windows)
│   └── postprovision.sh           # Post-provision hook (Linux/Mac)
├── infra/
│   ├── main.bicep                 # Bicep orchestrator (subscription-scoped)
│   ├── main.parameters.json       # Parameter bindings for azd
│   └── core/
│       ├── ai-resource.bicep      # Azure OpenAI (Cognitive Services) account
│       ├── ai-model-deployment.bicep  # gpt-realtime-1.5 model deployment
│       └── role-assignment.bicep  # RBAC: Cognitive Services OpenAI User
├── src/
│   ├── main.py                    # Application entry point
│   └── chat.prompty               # Prompty configuration
├── azure.yaml                     # Azure Developer CLI project config
├── LICENSE
├── README.md
└── requirements.txt
```

## What Gets Deployed

Running `azd up` provisions the following in your Azure subscription:

| Resource | Description |
|---|---|
| **Resource Group** | `rg-{env-name}` |
| **Azure OpenAI** | Cognitive Services account (`S0` SKU) |
| **Model Deployment** | `gpt-realtime-1.5` (`2026-02-23`, GlobalStandard) |
| **RBAC Role Assignment** | `Cognitive Services OpenAI User` for your identity (keyless auth) |

## Getting Started

### Prerequisites

- [Azure Developer CLI (azd)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd) installed
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- An Azure subscription
- Python 3.10+

### Deploy to Azure

1. **Log in** to Azure:

   ```bash
   azd auth login
   ```

2. **Provision and deploy** all resources:

   ```bash
   azd up
   ```

   You will be prompted to:
   - Enter an **environment name** (e.g. `gptrealtimedev`)
   - Select your **Azure subscription**
   - Select a **region** (recommended: `Sweden Central` or `East US 2` for best model availability)

3. After provisioning completes, a `.env` file is generated at the project root with:

   ```
   AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com/"
   AZURE_OPENAI_DEPLOYMENT="gpt-realtime-1-5"
   ```

### Connect to the Realtime API

The deployed model is accessible via WebSocket at:

```
wss://<your-resource>.openai.azure.com/openai/v1/realtime?model=gpt-realtime-1-5
```

Authentication uses **Microsoft Entra ID** (keyless). Use `AzureDeveloperCliCredential` or `DefaultAzureCredential` from the `azure-identity` SDK to obtain a Bearer token.

See [GPT_REALTIME_TRANSCRIPTION_TUTORIAL.md](GPT_REALTIME_TRANSCRIPTION_TUTORIAL.md) for a full walkthrough of connecting, configuring sessions, streaming audio, and handling events.

### Tear Down

To remove all deployed Azure resources:

```bash
azd down
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
