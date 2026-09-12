# LiteLLM AI Tutor Integration

## Goal
Embed a grounded chat interface inside the onboarding guidebook so newcomers (and the original developer) can ask any question about the **entire codebase** and receive answers that cite real modules, files, and the generated diagrams.

## Configuration (never commit secrets)
Create `docs/onboarding/config.example.json`:
```json
{
  "litellmBase": "http://localhost:4000",
  "litellmToken": "YOUR_LITELLM_TOKEN_OR_MASTER_KEY",
  "model": "gpt-4o",
  "systemPromptFile": "./system-prompt.md"
}
```
Instruct the user to copy it to `config.json` (gitignored) and fill in their real token.

## System prompt construction
The system prompt must contain:

1. The Phase-0 onboarding guide (summary)
2. The full Phase-1 architecture model — every major module, entry points, relations, and risks
3. List of available diagrams and module pages
4. Explicit instruction:
   - Always ground answers in the analyzed knowledge of the whole project
   - Cite concrete file paths and module names
   - If the answer is uncertain or a module was only partially analyzed, say so and suggest which files or areas to inspect next
   - Offer to “learn more” by proposing additional analysis of a specific module or an update to the guidebook

## Frontend skeleton
A minimal chat UI (vanilla JS or a tiny React/Vue component) that:
- Reads config.json
- Maintains conversation history
- Sends OpenAI-compatible requests to the LiteLLM endpoint
- Renders markdown answers
- Provides a “Refresh knowledge” button that can call a local script to re-analyze changed or under-documented modules

## Learning loop
When the user (or the AI) decides more knowledge is needed:
1. Re-analyze the relevant modules or recent changes
2. Optionally re-generate the affected module page(s) and knowledge files
3. Reload the system prompt with the freshest architecture model
4. Continue the conversation with the richer context

This turns the onboarding site into a living knowledge base for the whole project instead of a static snapshot.
