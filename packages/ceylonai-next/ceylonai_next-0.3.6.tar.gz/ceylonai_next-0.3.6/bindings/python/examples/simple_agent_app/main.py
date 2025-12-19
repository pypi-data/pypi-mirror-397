import ceylonai_next

agent = ceylonai_next.PyLlmAgent(name="py_llm_agent", model="ollama::gemma3:latest")

agent.act("echo", {"message": "Hello from Python!"})
