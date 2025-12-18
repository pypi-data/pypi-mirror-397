# Project 03: LLM Providers Deep

Exhaustive testing of all 4 LLM providers with all their capabilities.

## Purpose
Test each provider's features:
- Anthropic: Claude models, streaming, vision
- OpenAI: GPT-4 models, function calling
- Google: Gemini models, multimodal
- Groq: Fast Llama inference

## Time Required
~1.5 hours

## Prerequisites
- API keys configured for all 4 providers:
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`
  - `GOOGLE_API_KEY`
  - `GROQ_API_KEY`

## Provider Tests

### 3.1 Anthropic (Claude)
- Basic generation (Sonnet, Haiku, Opus)
- Streaming responses
- Vision (image analysis)
- Token/cost tracking

### 3.2 OpenAI (GPT)
- GPT-4, GPT-4o, GPT-4-turbo
- o1 reasoning models
- Streaming
- Function calling

### 3.3 Google (Gemini)
- Gemini 1.5 Pro/Flash
- Streaming
- Multimodal

### 3.4 Groq
- Llama 3 models
- Fast inference
- Latency comparison

### 3.5 Cross-Provider
- Provider switching in single pipeline
- Same prompt comparison
- Cost/latency analysis

## Success Criteria
All provider tests pass with correct outputs and metrics.
