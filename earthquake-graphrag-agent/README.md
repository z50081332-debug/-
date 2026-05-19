# Earthquake GraphRAG Agent

基于 **风险因果链 + 事故案例图谱 + GraphRAG + 多 Agent 编排** 的地震应急策略生成原型工程。

该工程适合作为课程作业、科研原型、论文方法验证或项目申报演示版本。它不依赖外部数据库，默认使用本地 JSON 案例库和内存图谱即可运行；后续可以替换为 Qdrant、Neo4j、本地大模型等工程组件。

---

## 1. 项目解决的问题

地震应急策略生成中常见问题包括：

1. 灾情信息碎片化：震级、地点、人员伤亡、交通、通信、次生灾害等信息分散，难以形成完整风险判断。
2. 历史案例难以复用：已有地震事故案例通常是文本记录，缺少结构化风险链和处置链。
3. 单纯大模型生成依据不足：直接让大模型生成应急方案，容易出现泛化、空泛、不可追溯的问题。
4. 策略更新能力不足：灾情随余震、降雨、道路抢通、伤亡变化而动态变化，需要持续更新策略。

本项目采用 GraphRAG 思路：

- 从历史案例中抽取风险因果链和处置措施链；
- 构建事故案例图谱；
- 对新输入灾情进行风险链抽取；
- 将当前风险链与历史案例链进行对齐；
- 检索相似案例、风险路径和措施链；
- 生成有依据、可追溯、可更新的应急策略。

---

## 2. 核心模块

```text
用户输入灾情文本
        │
        ▼
EventExtractorAgent       灾情要素抽取：地点、震级、风险关键词
        │
        ▼
RiskChainAgent            当前风险因果链构建
        │
        ▼
CaseAlignmentAgent        当前风险链与历史案例链对齐
        │
        ▼
GraphRAGAgent             图谱检索：相似案例、风险节点、处置措施
        │
        ▼
StrategyAgent             生成应急策略
        │
        ▼
DynamicUpdateAgent        保存结果、记录反馈、支持动态更新
```

---

## 3. 工程结构

```text
earthquake-graphrag-agent/
├── main.py                         # 统一启动入口
├── requirements.txt                # Python 依赖
├── .env.example                    # 可选环境变量
├── data/
│   └── cases.json                  # 示例地震事故案例库
├── app/
│   ├── config.py                   # 配置
│   ├── schemas.py                  # 数据模型
│   ├── api.py                      # FastAPI 接口
│   ├── cli.py                      # 命令行交互
│   ├── orchestrator.py             # 多 Agent 编排
│   ├── agents/
│   │   ├── event_extractor.py      # 灾情抽取 Agent
│   │   ├── risk_chain_agent.py     # 风险链构建 Agent
│   │   ├── case_alignment_agent.py # 案例对齐 Agent
│   │   ├── graphrag_agent.py       # GraphRAG 检索 Agent
│   │   ├── strategy_agent.py       # 策略生成 Agent
│   │   └── dynamic_update_agent.py # 动态更新 Agent
│   └── services/
│       ├── graph.py                # 简单事故案例图谱
│       ├── text_retriever.py       # 本地 TF-IDF 检索器
│       └── llm.py                  # 可选 Ollama 调用
└── tests/
    └── test_pipeline.py            # 简单测试
```

---

## 4. 安装与运行

### 4.1 创建虚拟环境

```bash
cd earthquake-graphrag-agent
python -m venv .venv
```

Windows PowerShell：

```bash
.venv\Scripts\activate
```

Linux / macOS：

```bash
source .venv/bin/activate
```

### 4.2 安装依赖

```bash
pip install -r requirements.txt
```

### 4.3 命令行运行

```bash
python main.py --cli
```

输入示例：

```text
某山区发生6.8级地震，震中附近乡镇房屋倒塌，道路塌方，通信中断，部分群众被困，并且仍有余震风险。
```

### 4.4 API 运行

```bash
python main.py --api --host 127.0.0.1 --port 8000
```

浏览器打开：

```text
http://127.0.0.1:8000/docs
```

测试接口：

```bash
curl -X POST "http://127.0.0.1:8000/generate_strategy" ^
  -H "Content-Type: application/json" ^
  -d "{\"disaster_text\":\"某山区发生6.8级地震，道路塌方，通信中断，群众被困，存在余震风险。\"}"
```

Linux / macOS：

```bash
curl -X POST "http://127.0.0.1:8000/generate_strategy" \
  -H "Content-Type: application/json" \
  -d '{"disaster_text":"某山区发生6.8级地震，道路塌方，通信中断，群众被困，存在余震风险。"}'
```

---

## 5. 可选：接入本地 Ollama 大模型

默认情况下，工程使用规则模板生成策略，不需要大模型也能运行。

如果本机安装了 Ollama，可以启用本地大模型生成：

```bash
set USE_OLLAMA=1
set OLLAMA_MODEL=qwen2.5:7b
python main.py --api
```

Linux / macOS：

```bash
export USE_OLLAMA=1
export OLLAMA_MODEL=qwen2.5:7b
python main.py --api
```

没有 Ollama 或模型调用失败时，程序会自动回退到模板生成。

---

## 6. 后续扩展建议

当前工程是可运行原型。论文或项目中可以继续扩展：

1. 案例库扩展：把真实地震案例整理为 `data/cases.json`。
2. 向量数据库：将 `TextRetriever` 替换为 BGE / Qwen Embedding + Qdrant。
3. 图数据库：将 `SimpleCaseGraph` 替换为 Neo4j。
4. 信息抽取：将规则抽取替换为 LLM 结构化抽取。
5. 动态更新：接入实时灾情流、余震信息、道路抢通状态、医院容量等数据。
6. 评价指标：增加策略准确性、案例命中率、事实一致性、可追溯性、人工评分等指标。

---

## 7. 适合作为申报表成果描述

我设计并实现了一个基于风险因果链、事故案例图谱与动态 GraphRAG 的地震应急策略生成 Agent 原型。系统从历史地震事故案例中抽取灾害事件、风险因素、次生灾害、处置措施和处置结果，构建风险因果链和事故案例图谱；当输入新的地震灾情后，系统自动抽取当前风险节点，并与历史案例事件链进行语义对齐和图结构匹配，再通过 GraphRAG 检索相似案例、风险传播路径和措施链，生成可解释、可追溯、可动态更新的应急处置建议。
