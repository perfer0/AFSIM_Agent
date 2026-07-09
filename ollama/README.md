# Ollama Local Model Storage

This folder is reserved for local Ollama model files used by this project.

The actual model blobs live in:

```text
D:\AFsim\Agent\ollama\models
```

That directory is ignored by Git because model files are large and should not be uploaded to GitHub.

Current Windows user environment variable:

```powershell
OLLAMA_MODELS=D:\AFsim\Agent\ollama\models
```

After setting this variable, restart Ollama before pulling new models.
