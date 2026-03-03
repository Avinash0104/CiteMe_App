# Information Extraction Module / 信息提取模块

## 🇬🇧 English Overview

### Introduction
The **Information Extraction** module is a core component of the backend system designed to analyze raw text and extract structured intelligence. It combines multiple Natural Language Processing (NLP) techniques to identify factual claims, named entities, and significant keywords from user inputs or documents.

### Folder Structure
```text
Information_Extraction/
├── claim_detection.py       # Logic for distinguishing factual claims from opinions
├── entity_extraction.py     # Logic for identifying people, orgs, locations, etc.
├── keyword_extraction.py    # Logic for extracting main topics/keywords
├── nlp_pipeline.py          # The orchestrator that combines the three services above
├── __pycache__/             # Compiled Python files
└── api/                     # External interface package
    ├── __init__.py          # Makes 'api' a Python package
    ├── nlp_api.py           # The main entry point for other backend modules
    └── personal_example_usage.py  # Script demonstrating how to run the code locally
```

### File Descriptions & Functionality

1.  **`claim_detection.py`**
    *   **Role:** Claim vs. Opinion Classifier.
    *   **Functionality:** Uses machine learning models (e.g., Transformers/BERT) to analyze sentences. It assigns a score indicating whether a sentence is a checkable factual claim or a subjective opinion.

2.  **`entity_extraction.py`**
    *   **Role:** Named Entity Recognition (NER).
    *   **Functionality:** Scans text to identify specific entities such as Person Names, Organizations, Geopolitical Entities (Countries/Cities), and Dates.

3.  **`keyword_extraction.py`**
    *   **Role:** Topic Extraction.
    *   **Functionality:** Extracts the most relevant words or phrases that summarize the content of the text.

4.  **`nlp_pipeline.py`**
    *   **Role:** Internal Controller.
    *   **Functionality:** This class initializes the three extractors above. It takes raw text, splits it into sentences, runs all three analyses, and aggregates the results into a single data structure.

5.  **`api/nlp_api.py`**
    *   **Role:** Public Interface.
    *   **Functionality:** This is the "wrapper" designed for the rest of the backend to use. It simplifies the complex pipeline into easy-to-call functions like `analyze_text`.

---

## 🇨🇳 中文总览

### 简介
**Information Extraction（信息提取）** 模块是后端系统的核心组件，旨在分析原始文本并提取结构化信息。它结合了多种自然语言处理 (NLP) 技术，用于从用户输入或文档中识别事实主张 (Claims)、命名实体 (Entities) 和关键主题词 (Keywords)。

### 文件夹结构
```text
Information_Extraction/
├── claim_detection.py       # 用于区分事实主张与观点的逻辑代码
├── entity_extraction.py     # 用于识别人物、组织、地点等的逻辑代码
├── keyword_extraction.py    # 用于提取主要主题/关键词的逻辑代码
├── nlp_pipeline.py          # 协调器，将上述三个服务组合在一起
├── __pycache__/             # 编译后的 Python 文件
└── api/                     # 外部接口包
    ├── __init__.py          # 将 'api' 标记为 Python 包
    ├── nlp_api.py           # 其他后端模块调用的主要入口点
    └── personal_example_usage.py  # 演示如何在本地运行代码的脚本
```

### 文件描述与功能

1.  **`claim_detection.py`**
    *   **作用:** 主张与观点分类器。
    *   **功能:** 使用机器学习模型（如 Transformers/BERT）分析句子。它会给出一个分数，表明该句子是可核查的事实主张还是主观观点。

2.  **`entity_extraction.py`**
    *   **作用:** 命名实体识别 (NER)。
    *   **功能:** 扫描文本以识别特定实体，例如人名、组织机构、地缘政治实体（国家/城市）和日期。

3.  **`keyword_extraction.py`**
    *   **作用:** 主题提取。
    *   **功能:** 提取最能概括文本内容的关键词或短语。

4.  **`nlp_pipeline.py`**
    *   **作用:** 内部控制器。
    *   **功能:** 该类初始化上述三个提取器。它接收原始文本，将其拆分为句子，运行所有分析，并将结果汇总为单一的数据结构。

5.  **`api/nlp_api.py`**
    *   **作用:** 公共接口。
    *   **功能:** 这是为后端其他部分设计的“包装器”。它将复杂的管道简化为易于调用的函数，如 `analyze_text`。
