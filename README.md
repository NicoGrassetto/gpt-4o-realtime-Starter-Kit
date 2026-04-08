# GPT Realtime Starter Kit

A starter kit for building realtime speech-to-speech applications using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) and the GPT Realtime API (`gpt-realtime-1.5`) on Azure AI Foundry.

## Architecture

```
Browser ──WebSocket──► FastAPI server ──SDK WebSocket──► Azure Realtime API
                       (RealtimeRunner / RealtimeSession)
                       ├─ SDK handles session configuration
                       ├─ SDK auto-executes @function_tool calls
                       └─ SDK emits high-level events → browser
```

The server uses the **OpenAI Agents SDK** (`RealtimeAgent` + `RealtimeRunner` + `RealtimeSession`) to manage the connection to Azure. Tools defined with `@function_tool` are executed automatically by the SDK — no manual event interception needed.

## Project Structure

```
├── assets/                        # Static assets
├── config/
│   ├── __init__.py                # YAML config loader (modes + defaults)
│   ├── session_defaults.yaml      # Shared session baseline
│   └── modes/                     # Mode presets (voice_assistant, transcription, etc.)
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
├── prompts/
│   ├── __init__.py                # Prompt loader (.prompty files)
│   ├── default.prompty            # General-purpose voice assistant
│   ├── customer_support.prompty   # Domain-specific support agent
│   └── transcriber.prompty        # Transcription + translation
├── src/
│   ├── main.py                    # FastAPI server with SDK session manager
│   └── agent.py                   # RealtimeAgent factory
├── tools/
│   ├── __init__.py                # Tool exports (ALL_TOOLS list)
│   ├── weather.py                 # @function_tool: get_weather
│   └── search.py                  # @function_tool: search_knowledge_base
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

## Supported GA Realtime Models

This starter kit targets the **GA (Generally Available)** Realtime API only. Preview/beta models (`gpt-4o-realtime-preview`, `gpt-4o-mini-realtime-preview`) are **not** supported.

| Model ID | Version | Description |
|---|---|---|
| `gpt-realtime-1.5` | `2026-02-23` | Latest and best quality — **default for this kit** |
| `gpt-realtime` | `2025-08-28` | Base GA realtime model |
| `gpt-realtime-mini` | `2025-12-15` | Cost-efficient, updated mini |
| `gpt-realtime-mini` | `2025-10-06` | Cost-efficient GA model |

To use a different model, set the `AZURE_OPENAI_DEPLOYMENT` environment variable to the deployment name of any GA model above.

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

The server uses the OpenAI Agents SDK to connect to Azure. On each WebSocket connection to `/ws/{session_id}`, the server:

1. Creates a `RealtimeAgent` with instructions from a `.prompty` file and `@function_tool` definitions
2. Creates a `RealtimeRunner` and starts a `RealtimeSession` targeting your Azure deployment
3. Authenticates using **Microsoft Entra ID** (keyless) via `DefaultAzureCredential`
4. Relays audio and high-level SDK events between browser and Azure

### Run locally

```bash
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Tear Down

To remove all deployed Azure resources:

```bash
azd down
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
