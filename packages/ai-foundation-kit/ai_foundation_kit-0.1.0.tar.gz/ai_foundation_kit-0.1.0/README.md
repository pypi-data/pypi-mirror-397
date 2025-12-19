# 🏗️ AI Foundation Kit

**The Professional / Development-First Standard for AI/ML Applications**

`ai-foundation-kit` is an enterprise-grade Python library designed to provide the bedrock for building scalable, robust, and maintainable AI systems. It unifies core utilities—logging, exception handling, file management, model loading, and configuration—under a single, cohesive namespace: `AIFoundationKit`.

Designed for: **RAG**, **Generative AI**, **Agentic Workflows**, **Deep Learning**, and **Machine Learning**.

---

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install ai-foundation-kit
```

### From Source (Development)
```bash
git clone https://github.com/your-repo/ai-foundation-kit.git
cd ai-foundation-kit
pip install -e .
```

---

## 🏛️ Package Architecture

The package is structured under the `AIFoundationKit` namespace. Each submodule targets a specific domain of AI application development.

| Module | Import Path | Description | Key Components |
| :--- | :--- | :--- | :--- |
| **Base** | `AIFoundationKit.base` | **The Core Foundation.** Essential utilities required by every application. | `BaseFileManager`, `ApiKeyManager`, `AppException`, `Logger` |
| **RAG** | `AIFoundationKit.rag` | **Retrieval-Augmented Generation.** Tools for LLM loading and prompting. | `ModelLoader`, `BaseProvider`, `GenericPrompts` |
| **GenAI** | `AIFoundationKit.genai` | **Generative AI.** *(Upcoming)* Specialized tools for image/video generation. | *Planned* |
| **Agentic** | `AIFoundationKit.agentic` | **Agentic AI.** *(Upcoming)* Frameworks for autonomous agents. | *Planned* |
| **ML** | `AIFoundationKit.ml` | **Machine Learning.** *(Upcoming)* Scikit-learn wrappers & utilities. | *Planned* |
| **DL** | `AIFoundationKit.dl` | **Deep Learning.** *(Upcoming)* Torch/Tensorflow helpers. | *Planned* |

---

## 🛠️ Usage Guide

### 1. File Management (`AIFoundationKit.base`)
Stop writing boilerplate file readers. Use the `BaseFileManager` to handle PDFs, DOCX, JSON, and more seamlessly.

```python
from AIFoundationKit.base.file_manager import BaseFileManager

file_manager = BaseFileManager()

# Read ANY file type (PDF, DOCX, CSV, TXT, etc.)
content = file_manager.read_file("path/to/document.pdf")
print(content[:100])

# Save files (handling bytes or file-like objects)
saved_path = file_manager.save_file(
    file_obj=b"Binary data", 
    save_dir="data/uploads", 
    file_name="invoice.pdf"
)
```

### 2. Model Loading (`AIFoundationKit.rag`)
Instantly switch between Google Gemini, Groq, or your own custom providers without changing application logic.

```python
from AIFoundationKit.rag.model_loader import ModelLoader

# Initialize (loads config.yaml automatically or uses defaults)
loader = ModelLoader()

# Load LLM (Gemini Pro by default or configured)
llm = loader.load_llm(model_name="gemini-1.5-pro")

# Load Embeddings
embeddings = loader.load_embeddings()

# Use in LangChain
chain = prompt | llm
```

### 3. API Key Management (`AIFoundationKit.base`)
Securely manage keys from Environment Variables or Secret Stores.

```python
from AIFoundationKit.base.model import ApiKeyManager

key_mgr = ApiKeyManager()
google_key = key_mgr.get("GOOGLE_API_KEY")
```

### 4. Enterprise Logging & Exceptions
Standardized structured logging and error handling.

```python
from AIFoundationKit.base.logger.custom_logger import logger
from AIFoundationKit.base.exception.custom_exception import AppException

try:
    logger.info("Starting process", extra={"user_id": "12345"})
    # ... logic ...
except Exception as e:
    # Auto-wraps with standard error codes
    raise AppException(f"Process failed: {str(e)}") from e
```

---

## 🔮 Futuristic Example: The Agentic Workflow

Here is a glimpse of how you can build an autonomous file analysis agent using `AIFoundationKit`.

```python
from AIFoundationKit.base.file_manager import BaseFileManager
from AIFoundationKit.rag.model_loader import ModelLoader
from AIFoundationKit.rag.prompts import get_generic_prompt

async def run_autonomous_analyst(file_path: str):
    # 1. Perception: Read the File
    fm = BaseFileManager()
    file_content = fm.read_file(file_path)
    
    # 2. Brain: Initialize Neural Core (LLM)
    loader = ModelLoader()
    llm = loader.load_llm(provider="groq", model_name="llama-3.3-70b-versatile")
    
    # 3. Cognition: Analyze with Generic Prompt
    analysis_prompt = get_generic_prompt("summary")
    chain = analysis_prompt | llm
    
    result = chain.invoke({"input_text": file_content})
    
    print("🤖 Analyst Report:")
    print(result.content)

# Execution
# await run_autonomous_analyst("contracts/q4_financials.pdf")
```

---

## 📝 Changelog

| Version | Changes |
| :--- | :--- |
| **v0.1.0** | • **Initial Release**: Fresh launch of `ai-foundation-kit` (Stable).<br>• **Core**: Includes `base` (File/Key Utils), `rag` (Model Loading), logging, exceptions. |

---

## License

MIT License
