# Proposal

## Title

Add LiteLLM Proxy as an alternative inference provider

## Why

The project currently routes inference through a local API that was originally coupled to Ollama. We now need to support an enterprise LiteLLM Proxy with many remotely available models, while preserving the same API contract for the Python tool runners and user-facing tools.

This change also enables apples-to-apples latency comparisons between local Ollama and remote providers for interactive workflows like `selected-text-correction`.

## Scope

- Add provider selection to `local-inference-api`
- Keep existing project endpoints stable
- Support OpenAI-compatible chat completion calls through LiteLLM Proxy
- Document `.env` switching between `ollama` and `litellm_proxy`
- Record latency evidence for at least one remote model

## Out of Scope

- Full multimodal validation of every remote model
- Routing different tools to different providers simultaneously
- UI-level provider switching
