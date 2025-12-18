# Akto LLM Guard

LLM-Guard is a comprehensive tool designed to fortify the security of Large Language Models (LLMs).

## Features

- **Prompt Injection Detection**: Detect and prevent prompt injection attacks
- **PII Detection**: Identify and handle personally identifiable information
- **Toxicity Detection**: Filter harmful and toxic content
- **Code Detection**: Identify and manage code in prompts
- **Data Leakage Prevention**: Prevent sensitive information leakage
- **URL Scanning**: Detect malicious URLs in outputs
- **Bias Detection**: Identify biased content in model outputs

## Installation

```bash
pip install akto-llm-guard
```

For ONNX runtime support:

```bash
pip install akto-llm-guard[onnxruntime]
```

For GPU support:

```bash
pip install akto-llm-guard[onnxruntime-gpu]
```

## Quick Start

```python
from llm_guard.input_scanners import PromptInjection

scanner = PromptInjection()
sanitized_prompt, is_valid, risk_score = scanner.scan("Your prompt here")

if is_valid:
    print("Prompt is safe")
else:
    print(f"Prompt failed security check. Risk score: {risk_score}")
```

## Repository

GitHub: [https://github.com/akto-api-security/llm-guard](https://github.com/akto-api-security/llm-guard)

## License

MIT License
