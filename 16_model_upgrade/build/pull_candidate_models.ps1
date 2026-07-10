$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
& 'C:\Users\lenovo\AppData\Local\Programs\Ollama\ollama.exe' list

# Recommended next model. Uncomment when ready to download several GB.
# ollama pull qwen2.5:7b
# ollama pull qwen2.5-coder:7b
# ollama pull qwen2.5:14b

# After pulling, verify with:
# cd D:\AFsim\Agent\07_agent_loop
# python .\agent_loop.py agent .\requests\eoir_agent_request.txt --model qwen2.5:7b --run
