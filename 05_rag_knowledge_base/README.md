# Step 05 - Local RAG Knowledge Base

这一课建立第一版离线 RAG。这里的 RAG 不是先上复杂向量数据库，而是先做一个可理解、可调试的关键词检索版。

## 这一步在学什么

第四步已经做到：

```text
自然语言 -> JSON -> AFSIM -> mission.exe
```

第五步加入：

```text
自然语言 -> 检索本地知识库 -> 带上下文生成 JSON -> AFSIM -> mission.exe
```

这就是“开卷生成”。以后换成本地 embedding 和向量库时，整体流程不变。

## 目录

```text
knowledge/afsim_snippets/       AFSIM 语法片段说明
components/                     第三步继承来的组件库
requests/eoir_rag_request.txt   用户自然语言需求
examples/rag_drafted_scenario.json
build/knowledge_index.json
build/retrieval_results.json
build/main_generated.txt
build/scenario_generated.txt
```

## 怎么运行

```powershell
cd D:\AFsim\Agent\05_rag_knowledge_base

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py index

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py retrieve --query-file .\requests\eoir_rag_request.txt

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py draft .\requests\eoir_rag_request.txt

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py validate .\examples\rag_drafted_scenario.json

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py generate .\examples\rag_drafted_scenario.json

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py run .\build\main_generated.txt
```

## 重点理解

`retrieve` 的作用是从本地文件中找相关材料，例如：

```text
knowledge/afsim_snippets/eoir_platform_instance.md
knowledge/afsim_snippets/ground_site_targets.md
components/platform_types/uav_eoir.json
```

`draft` 会把这些命中文档记录到 JSON 里：

```json
"rag_context": [
  {
    "id": "knowledge/afsim_snippets/eoir_platform_instance.md",
    "kind": "knowledge",
    "score": 6.386
  }
]
```

这让你能审计：这个 JSON 到底参考了哪些本地资料。

## 为什么不用向量库

第一版不用向量库，是为了让你先看懂 RAG 的本质：

```text
把资料放本地
根据需求查资料
把查到的资料交给生成器
生成 JSON
再由 CLI 严格验证
```

后面可以把关键词检索替换成：

```text
本地 embedding 模型 + FAISS/Chroma/Qdrant
```

但项目接口不需要推倒重来。
