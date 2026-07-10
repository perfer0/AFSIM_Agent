# MCP Reference For This Project

## Local MCP Server

Step 08 provides a minimal stdio MCP server:

```text
D:\AFsim\Agent\08_mcp_tools\mcp_server.py
```

It exposes:

```text
afsim_agent_run
afsim_agent_status
```

## Test Command

From `D:\AFsim\Agent\08_mcp_tools`:

```powershell
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
python .\mcp_client_test.py
```

Success evidence:

```text
tools/list contains afsim_agent_run
tools/call returns isError=false
mcp.returncode = 0
scenario.draft_provider = ollama
run event exit_code = 0
```

The saved test result is:

```text
build/mcp_test_result.json
```

## Debugging Notes

If `model not found` appears, restart Ollama with the correct model path:

```powershell
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
Get-Process | Where-Object { $_.ProcessName -like 'ollama*' } | Stop-Process -Force
Start-Process -FilePath 'C:\Users\lenovo\AppData\Local\Programs\Ollama\ollama.exe' -ArgumentList 'serve' -WindowStyle Hidden
```

Then verify:

```powershell
& 'C:\Users\lenovo\AppData\Local\Programs\Ollama\ollama.exe' list
```
