# 4-Gate Edge-Native AI Triage & SOAR Module

## Threat Model
* **Vectors**: SSH brute-force credential stuffing, prompt/command injection embedded via escape sequences (`\x1b]0;...`), unprivileged reconnaissance.
* **Trust Boundaries**: Local edge node (`127.0.0.1`) acts as the enforcement boundary; raw logs never egress to cloud vendor APIs. Local inference uses `phi3:latest` via Ollama.

## ASCII Sequence Flow
```
[Log Ingress] ---> [Gate 1: Noise Drop] ---> (Drop / Pass)
                                                   |
[Gate 4: SOAR Action] <--- [Gate 3: Reputation] <--+-- [Gate 2: Local LLM Deep Triage]
  (DryRun / Active)          (Threat Score / ASN)       (Phi-3 Local Inference)
```

## HPC Benchmark Parameters
* **Batch Size**: 32 concurrent evaluation windows
* **Flash Attention**: Enabled (`flash_attn=True`)
* **Context Window**: 2048 tokens
* **Target Throughput**: >= 350,000 tokens/sec on local edge hardware profile.
