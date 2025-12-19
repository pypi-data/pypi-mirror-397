# Python Examples Execution Report

**Date:** 2025-12-18 13:53:14
**Total Examples:** 27

| Example | Status | Duration | Error |
|---------|--------|----------|-------|
| demo_agent_memory.py | ❌ FAIL | 0.28s | Exit code: 1 |
| demo_agent_mesh_local.py | ✅ PASS | 0.87s |  |
| demo_agent_rag_memory.py | ❌ FAIL | 0.18s | Exit code: 1 |
| demo_async_agent.py | ✅ PASS | 0.16s |  |
| demo_async_llm.py | ⏱️ TIMEOUT | 30.02s | Timed out after 30s |
| demo_async_mesh_results.py | ⏱️ TIMEOUT | 30.02s | Timed out after 30s |
| demo_broadcast_mesh.py | ✅ PASS | 11.69s |  |
| demo_conversation.py | ✅ PASS | 25.43s |  |
| demo_custom_memory.py | ❌ FAIL | 0.16s | Exit code: 1 |
| demo_distributed.py | ✅ PASS | 3.21s |  |
| demo_llm_actions.py | ✅ PASS | 1.82s |  |
| demo_llm_agents_mesh.py | ✅ PASS | 21.66s |  |
| demo_llm_mesh.py | ✅ PASS | 3.78s |  |
| demo_memory.py | ✅ PASS | 7.69s |  |
| demo_multi_agent_mesh.py | ✅ PASS | 7.00s |  |
| demo_rag_embeddings.py | ❌ FAIL | 0.05s | Exit code: 1 |
| demo_react.py | ✅ PASS | 1.77s |  |
| demo_redis_memory.py | ⏱️ TIMEOUT | 30.02s | Timed out after 30s |
| demo_simple_agent.py | ✅ PASS | 0.95s |  |
| demo_vertex_ai.py | ❌ FAIL | 0.16s | Exit code: 1 |
| distributed_demo.py | ✅ PASS | 2.19s |  |
| metrics_demo.py | ✅ PASS | 7.12s |  |
| metrics_openai_tokens.py | ✅ PASS | 18.24s |  |
| metrics_quickstart.py | ✅ PASS | 1.19s |  |
| metrics_token_counter.py | ✅ PASS | 5.46s |  |
| test_llm_mesh_minimal.py | ✅ PASS | 0.15s |  |
| test_token_fix.py | ✅ PASS | 0.16s |  |


## Detailed Output

### demo_agent_memory.py (FAIL)
```
============================================================
🤖 LlmAgent Memory Demo
============================================================

🧠 Initializing Memory Backend...
✅ Memory backend created

🤖 Initializing LLM Agent with Memory...
✅ Agent created with model 'ollama::llama3.2:latest'

📝 Instructing agent to save a fact...
User: Please remember this important fact: The secret code is 'BLUE-HORIZON-99'.

Traceback (most recent call last):
  File "F:\projects\ceylon\next-processor\bindings\python\examples\demo_agent_memory.py", line 82, in <module>
    asyncio.run(main())
  File "C:\Users\dewma\AppData\Roaming\uv\python\cpython-3.12.11-windows-x86_64-none\Lib\asyncio\runners.py", line 195, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "C:\Users\dewma\AppData\Roaming\uv\python\cpython-3.12.11-windows-x86_64-none\Lib\asyncio\runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\dewma\AppData\Roaming\uv\python\cpython-3.12.11-windows-x86_64-none\Lib\asyncio\base_events.py", line 691, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "F:\projects\ceylon\next-processor\bindings\python\examples\demo_agent_memory.py", line 41, in main
    response = await agent.send_message(prompt)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "f:\projects\ceylon\next-processor\bindings\python\ceylonai_next\agent\llm.py", line 103, in send_message
    return await self._agent.send_message(message)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Mesh error: LLM error: HTTP Error: HTTP status client error (404 Not Found) for url (http://127.0.0.1:11434/api/chat)

```

### demo_agent_rag_memory.py (FAIL)
```
============================================================
🤖 LlmAgent Memory RAG Demo
============================================================

🧠 Initializing Memory Backend...

📚 Processing documents...
Created 6 chunks.
💾 Storing chunks in memory...
✅ Stored 6 entries in memory.

🤖 Initializing Agent...
✅ Agent created.

❓ Question: Who were the 'Shell Indians' and why were they called that?
------------------------------

Traceback (most recent call last):
  File "F:\projects\ceylon\next-processor\bindings\python\examples\demo_agent_rag_memory.py", line 118, in <module>
    asyncio.run(main())
  File "C:\Users\dewma\AppData\Roaming\uv\python\cpython-3.12.11-windows-x86_64-none\Lib\asyncio\runners.py", line 195, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "C:\Users\dewma\AppData\Roaming\uv\python\cpython-3.12.11-windows-x86_64-none\Lib\asyncio\runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\dewma\AppData\Roaming\uv\python\cpython-3.12.11-windows-x86_64-none\Lib\asyncio\base_events.py", line 691, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "F:\projects\ceylon\next-processor\bindings\python\examples\demo_agent_rag_memory.py", line 107, in main
    response = await agent.send_message(q)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "f:\projects\ceylon\next-processor\bindings\python\ceylonai_next\agent\llm.py", line 103, in send_message
    return await self._agent.send_message(message)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Mesh error: LLM error: HTTP Error: HTTP status client error (404 Not Found) for url (http://127.0.0.1:11434/api/chat)

```

### demo_async_llm.py (TIMEOUT)
```
Timeout - output truncated
```

### demo_async_mesh_results.py (TIMEOUT)
```
Timeout - output truncated
```

### demo_custom_memory.py (FAIL)
```
============================================================
🧪 Custom Memory Backend Demo
============================================================

🔧 Creating custom memory backend...
📦 SimpleVectorMemory initialized

📝 Testing basic memory operations...
  ✅ Stored entry ae9b6c78... content: 'The Eiffel Tower is in Paris, France....'
  ✅ Stored entry 86a20944... content: 'The Great Wall of China is in China....'
  ✅ Stored entry 3a1dae92... content: 'The Statue of Liberty is in New York, USA....'

📊 Total entries: 3

🤖 Integrating with LlmAgent...
✅ Agent built with custom memory backend

❓ Testing agent with custom memory...
User: Where is the Eiffel Tower located?

Traceback (most recent call last):
  File "F:\projects\ceylon\next-processor\bindings\python\examples\demo_custom_memory.py", line 143, in <module>
    asyncio.run(main())
  File "C:\Users\dewma\AppData\Roaming\uv\python\cpython-3.12.11-windows-x86_64-none\Lib\asyncio\runners.py", line 195, in run
    return runner.run
... [truncated] ...
      ^^^^^^^^^^^^^^^^
  File "C:\Users\dewma\AppData\Roaming\uv\python\cpython-3.12.11-windows-x86_64-none\Lib\asyncio\runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\dewma\AppData\Roaming\uv\python\cpython-3.12.11-windows-x86_64-none\Lib\asyncio\base_events.py", line 691, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "F:\projects\ceylon\next-processor\bindings\python\examples\demo_custom_memory.py", line 125, in main
    response = await agent.send_message(question)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "f:\projects\ceylon\next-processor\bindings\python\ceylonai_next\agent\llm.py", line 103, in send_message
    return await self._agent.send_message(message)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Mesh error: LLM error: HTTP Error: HTTP status client error (404 Not Found) for url (http://127.0.0.1:11434/api/chat)

```

### demo_rag_embeddings.py (FAIL)
```

Traceback (most recent call last):
  File "F:\projects\ceylon\next-processor\bindings\python\examples\demo_rag_embeddings.py", line 19, in <module>
    import numpy as np
ModuleNotFoundError: No module named 'numpy'

```

### demo_redis_memory.py (TIMEOUT)
```
Timeout - output truncated
```

### demo_vertex_ai.py (FAIL)
```
============================================================
Ceylon LlmAgent - Vertex AI Demo
============================================================

⚠️  VERTEX_API_KEY environment variable not set.
Please set your Vertex AI API key:
  export VERTEX_API_KEY='your-api-key'

Or on Windows PowerShell:
  $env:VERTEX_API_KEY='your-api-key'


```
