# NLP API Usage Guide / NLP API 使用指南

This document provides a detailed guide on how to use the `api` package within the Information Extraction module. It is designed for developers who need to integrate NLP features into other parts of the backend.

本文档详细介绍了如何使用信息提取模块中的 `api` 包。它是为需要将 NLP 功能集成到后端其他部分的开发人员设计的。

---

## 🇬🇧 English Guide

### 1. Overview
The `api` package acts as a bridge between the complex NLP logic (claim detection, entity extraction, etc.) and the rest of the application. You should **always** use the functions provided in `nlp_api.py` instead of importing the internal service files directly.

### 2. How to Import
To use the NLP capabilities, import the necessary functions from the `nlp_api` module.
*Assumption: Your project root is `backend/`.*

```python
from app.services.Information_Extraction.api.nlp_api import analyze_text, analyze_sentence, get_keywords_only
```

### 3. Available Functions

#### A. `analyze_text` (Main Function)
This is the primary function you will use. It runs the entire pipeline (Claim Detection + Entity Extraction + Keyword Extraction) on the input text.

**Signature:**
```python
def analyze_text(
    text: str,
    include_claims: bool = True,
    include_entities: bool = True,
    include_keywords: bool = True,
    max_keywords: int = 10
) -> dict
```

**Parameters:**
*   `text` (str): The raw text content you want to analyze.
*   `include_claims` (bool): Whether to detect factual claims (default: True).
*   `include_entities` (bool): Whether to extract named entities (default: True).
*   `include_keywords` (bool): Whether to extract keywords (default: True).
*   `max_keywords` (int): Maximum number of keywords to extract per sentence (default: 10).

**Returns:**
*   `dict`: A dictionary containing the analysis results, including a list of sentences with their respective claims, entities, and keywords.

#### B. `analyze_sentence`
Analyzes a single sentence. Useful if you have already split your text or only need to check a short string.

**Signature:**
```python
def analyze_sentence(
    sentence: str,
    include_claims: bool = True,
    include_entities: bool = True,
    include_keywords: bool = True,
    max_keywords: int = 5
) -> dict
```

#### C. `get_keywords_only`
A helper function to quickly extract keywords from a text without running the full claim/entity analysis.

**Signature:**
```python
def get_keywords_only(text: str, top_n: int = 10) -> list
```

### 4. Complete Usage Example
Here is a script demonstrating how to call the API in a real scenario.

```python
from app.services.Information_Extraction.api.nlp_api import analyze_text

def run_analysis():
    # 1. Define input text
    sample_text = "Elon Musk stated that SpaceX will launch a new rocket from Texas next month. I think it is amazing."

    # 2. Process the text
    print("Processing text...")
    # Note: The first call might take a few seconds to load the models.
    result = analyze_text(sample_text)

    # 3. Access the results
    if result['success']:
        print("\n--- Analysis Results ---")
        print(f"Total Sentences: {result['total_sentences']}")
        
        for i, sentence_data in enumerate(result['sentences']):
            print(f"\nSentence {i+1}: {sentence_data['text']}")
            
            # Check for claims
            if sentence_data.get('is_claim'):
                print(f"  [!] Claim Detected (Confidence: {sentence_data['claim_score']})")
            
            # Check for entities
            entities = sentence_data.get('entities', [])
            if entities:
                print(f"  Entities: {entities}")
                
            # Check for keywords
            keywords = sentence_data.get('keywords', [])
            if keywords:
                print(f"  Keywords: {keywords}")
    else:
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    run_analysis()
```

### 5. Response Data Structure
The `analyze_text` function returns a JSON-compatible dictionary structure:

```json
{
  "success": true,
  "total_sentences": 1,
  "sentences": [
    {
      "text": "SpaceX will launch a new rocket from Texas next month",
      "is_claim": true,
      "claim_score": 0.98,
      "entities": [
        ["SpaceX", "ORG"],
        ["Texas", "GPE"],
        ["next month", "DATE"]
      ],
      "keywords": ["SpaceX", "Rocket", "Launch", "Texas"]
    }
  ],
  "statistics": {
      "claim_count": 1,
      "entity_count": 3,
      "keyword_count": 4
  }
}
```

---

## 🇨🇳 中文指南

### 1. 概述
`api` 包充当了复杂的 NLP 逻辑（主张检测、实体提取等）与应用程序其余部分之间的桥梁。你应该**始终**使用 `nlp_api.py` 中提供的函数，而不是直接导入内部服务文件。

### 2. 如何导入
要使用 NLP 功能，请从 `nlp_api` 模块导入必要的函数。
*假设：你的项目根目录是 `backend/`。*

```python
from app.services.Information_Extraction.api.nlp_api import analyze_text, analyze_sentence, get_keywords_only
```

### 3. 可用函数

#### A. `analyze_text` (主函数)
这是你将使用的主要函数。它会对输入文本运行整个管道（主张检测 + 实体提取 + 关键词提取）。

**函数签名:**
```python
def analyze_text(
    text: str,
    include_claims: bool = True,
    include_entities: bool = True,
    include_keywords: bool = True,
    max_keywords: int = 10
) -> dict
```

**参数:**
*   `text` (str): 你想要分析的原始文本内容。
*   `include_claims` (bool): 是否检测事实主张（默认：True）。
*   `include_entities` (bool): 是否提取命名实体（默认：True）。
*   `include_keywords` (bool): 是否提取关键词（默认：True）。
*   `max_keywords` (int): 每个句子提取的最大关键词数量（默认：10）。

**返回值:**
*   `dict`: 包含分析结果的字典，其中包括句子列表及其相应的主张、实体和关键词。

#### B. `analyze_sentence`
分析单个句子。如果你已经分割了文本或只需要检查一个短字符串，这很有用。

**函数签名:**
```python
def analyze_sentence(
    sentence: str,
    include_claims: bool = True,
    include_entities: bool = True,
    include_keywords: bool = True,
    max_keywords: int = 5
) -> dict
```

#### C. `get_keywords_only`
一个辅助函数，用于从文本中快速提取关键词，而不运行完整的主张/实体分析。

**函数签名:**
```python
def get_keywords_only(text: str, top_n: int = 10) -> list
```

### 4. 完整使用示例
以下是一个演示如何在实际场景中调用 API 的脚本。

```python
from app.services.Information_Extraction.api.nlp_api import analyze_text

def run_analysis():
    # 1. 定义输入文本
    sample_text = "Elon Musk stated that SpaceX will launch a new rocket from Texas next month. I think it is amazing."

    # 2. 处理文本
    print("正在处理文本...")
    # 注意：首次调用可能需要几秒钟来加载模型。
    result = analyze_text(sample_text)

    # 3. 访问结果
    if result['success']:
        print("\n--- 分析结果 ---")
        print(f"句子总数: {result['total_sentences']}")
        
        for i, sentence_data in enumerate(result['sentences']):
            print(f"\n句子 {i+1}: {sentence_data['text']}")
            
            # 检查主张
            if sentence_data.get('is_claim'):
                print(f"  [!] 检测到主张 (置信度: {sentence_data['claim_score']})")
            
            # 检查实体
            entities = sentence_data.get('entities', [])
            if entities:
                print(f"  实体: {entities}")
                
            # 检查关键词
            keywords = sentence_data.get('keywords', [])
            if keywords:
                print(f"  关键词: {keywords}")
    else:
        print(f"错误: {result.get('error')}")

if __name__ == "__main__":
    run_analysis()
```

### 5. 响应数据结构
`analyze_text` 函数返回一个兼容 JSON 的字典结构：

```json
{
  "success": true,
  "total_sentences": 1,
  "sentences": [
    {
      "text": "SpaceX will launch a new rocket from Texas next month",
      "is_claim": true,
      "claim_score": 0.98,
      "entities": [
        ["SpaceX", "ORG"],
        ["Texas", "GPE"],
        ["next month", "DATE"]
      ],
      "keywords": ["SpaceX", "Rocket", "Launch", "Texas"]
    }
  ],
  "statistics": {
      "claim_count": 1,
      "entity_count": 3,
      "keyword_count": 4
  }
}
```
