# JARVIS 2.0: Private, Autonomous Multi-Agent AI Ecosystem

An architectural blueprint and local proof-of-concept (PoC) for a secure, multi-agent AI framework optimized for consumer-class hardware. This infrastructure coordinates decoupled local microservices to automate qualitative market research, multilingual strategic data synthesis, and agentic workflows without cloud dependencies.

> **Project Status:** This repository serves as a documented, successfully verified code archive. While the local testing environment has been decommissioned, the multi-model architecture remains fully preserved here for enterprise portfolio and open-source reference.

## Technical Highlights & Capabilities
The system was engineered to run entirely offline on localized hardware (Intel i5, 8GB System RAM, NVIDIA RTX 3060 6GB GPU), utilizing highly optimized local LLM endpoints:

* **Production Model Cluster:** Orchestrates a tier of specialized local models—including **DeepSeek-7B** for structural technical reasoning, alongside **Qwen-7B and Mistral AI** for multilingual enterprise strategic document parsing and analysis.
* **Master Brain (Bot A):** Implemented via FastAPI on port 6001 to govern central system prompts, contextual intent routing, and incoming user queries.
* **Continuous Analytics Engine (Bot B):** An automated background scheduler utilizing `yfinance` to ingest, process, and build mathematical technical indicators (RSI, MACD, Bollinger Bands) every 15 minutes.
* **Neural Memory Matrix:** Powered by an offline instance of `ChromaDB` for structured Retrieval-Augmented Generation (RAG) and paired with a local `Redis Server` functioning as a low-latency inter-bot message broker.
* **Agentic Automation Layer:** Integrated via the `OpenClaw Agentic Gateway` to execute secure, programmatic system automation, terminal tasks, and browser-level operations.
* **Governance & Hardened Security:** Configured with a strict Human-in-the-Loop verification layer via `exec-approvals.json` (Consent Mode), forcing autonomous scripts to pause and request operator confirmation before executing shell commands or data mutations.

## Core Infrastructure Port Mapping
Upon operational launch, the system automatically binds to the following network ports:
* `4000` - LiteLLM Router Proxy (Standardizing multi-model routing arrays)
* `6001` - Bot A Core (Brain API Entrypoint)
* `6002` - Bot B Core (Training & Patterns API)
* `6003` - Algorithmic Trading Simulation Engine
* `8000` - ChromaDB (Semantic Vector Storage Node)
* `6379` - Redis Server (Real-time Communication Bus)
* `8501` - Streamlit (Executive Command Center Dashboard)
* `11434` - Ollama Server Core (Raw Model Weights Calculations)

## Repository Architecture
* `/bot_a` - Asynchronous backend query handling, tool definitions, and system routing logic.
* `/bot_b` - Scheduled market data collection workflows, indicator calculators, and pattern analysis engines.
* `/config` - Centralized routing properties and infrastructure orchestration configurations (`litellm_config.yaml`).
* `/dashboard` - Executive visual tracking application layer built using Streamlit.
* `START_JARVIS.bat` - Master startup execution script engineered to allocate a 32,768 token context memory window directly to the model layers to eliminate data processing overflows.

## Core Engineering Competencies Demonstrated
Building and testing this proof-of-concept validated practical proficiency in:
1. Designing decoupled, containerless asynchronous microservice architectures on Windows platforms using FastAPI.
2. Building local semantic memory environments using vector databases and low-latency key-value data caching.
3. Overriding local hardware constraints through programmatic context window and weight allocation adjustments.
4. Structuring strict data compliance frameworks by embedding physical validation checkpoints into autonomous AI loops.


## System Interface & Execution Proof

To validate the multi-agent orchestration layer and verify complete operational delivery before local environment decommissioning, system outputs and interface nodes were captured during active multi-model execution:

### 1. Executive Operations Command Dashboard
A centralized enterprise Web UI constructed using Streamlit to track real-time macroeconomic indices, asset status, core multi-process backend connections, and parsed intelligence news feeds.

<p align="center">
  <img src="https://github.com/user-attachments/assets/cd26d498-6d3d-46aa-ae49-db2973f1ae0d" width="900" alt="Streamlit Jarvis Operations Command Center Dashboard" />
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/afe7bbc7-e84d-4fe4-bb61-5323b81ec542" width="900" alt="Streamlit Jarvis Operations Command Center Dashboard 2" />
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/8f7108dc-2161-4894-8505-8129296b1465" width="900" alt="Streamlit Executive Jarvis Operations Command Center Dashboard 3" />
</p>

### 2. Multi-Service Core Orchestration
Left: The master `.bat` system configuration sequence tracking automated service initializations and port mapping variables. Right: The standalone FastAPI application process runtime logs for **Bot A (Master Brain)** serving active contextual health requests on port `6001`.

<p align="center">
  <img src="https://github.com/user-attachments/assets/e9601967-315c-4776-8c0b-3f97b12fd1f0" width="440" alt="JARVIS Superbrain System Master Launcher Terminal" />
  &nbsp;&nbsp;
  <img src="https://github.com/user-attachments/assets/7d39156a-433a-432b-8b61-4f5fd31c188f" width="440" alt="JARVIS Bot A Core FastAPI Uvicorn Server Logs" />
</p>

### 3. Advanced Local Routers & Automation Gateways
Left: The local LiteLLM Router gateway server standardizing internal model calling schemas on port `4000`. Right: The dynamic runtime terminal log for the OpenClaw agent execution engine actively verifying connected device tools via the local DeepSeek-R1 framework.

<p align="center">
  <img src="https://github.com/user-attachments/assets/4f4babf2-e5f3-44ec-8a39-3436afd02321" width="440" alt="LiteLLM Router Proxy Multi Model Interface" />
  &nbsp;&nbsp;
  <img src="https://github.com/user-attachments/assets/d205af98-b7e4-405e-92c6-38dee83b9b34" width="440" alt="OpenClaw Autonomous Agent Gateway Execution Log" />
</p>

### 4. Unified Front-End Browser Client
The production-ready browser container interface (`Page Assist`) mapped directly to the local data node cache (`jarvis_brain`), displaying custom routing capabilities across the local high-capacity model array (**DeepSeek-R1**, **Qwen2.5**, and **Mistral**).

<p align="center">
  <img src="https://github.com/user-attachments/assets/bc185f98-2e3b-4d35-b607-81135ae4d210" width="900" alt="Page Assist Browser UI Dropdown Local Model Stack" />
</p>
