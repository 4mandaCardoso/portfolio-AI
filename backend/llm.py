"""Cliente de API opcional. Nenhuma chave vai para o navegador."""
import json
import os
import urllib.request
import urllib.error
from urllib.parse import urlparse
from . import config

class ProviderError(Exception):
    pass

def configured():
    return all(os.getenv(k, "").strip() for k in ("LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY"))

def complete(system, payload):
    base = os.environ.get("LLM_BASE_URL", "").rstrip("/")
    if not configured():
        raise ProviderError("Configure os três campos LLM no .env e reinicie.")
    if urlparse(base).scheme != "https":
        raise ProviderError("LLM_BASE_URL deve usar HTTPS.")
    body = json.dumps({
        "model": os.environ["LLM_MODEL"], "temperature": 0.2,
        "max_tokens": 4000,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]
    }).encode()
    request = urllib.request.Request(base + "/chat/completions", data=body, headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + os.environ["LLM_API_KEY"]
    })
    try:
        with urllib.request.urlopen(request, timeout=55) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ProviderError("Resposta do provedor muito grande.")
        content = json.loads(raw)["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError("conteúdo ausente")
        return content
    except urllib.error.HTTPError as exc:
        raise ProviderError(f"Provedor retornou HTTP {exc.code}. Confira chave, modelo e saldo.") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ProviderError("Não foi possível consultar o provedor. Confira rede e configuração.") from None
    except (ValueError, KeyError, IndexError, TypeError):
        raise ProviderError("O provedor não retornou uma resposta compativel.") from None

def json_complete(system, payload):
    content = complete(system, payload).strip()
    if content.startswith("```"):
        lines = content.splitlines()
        content = "\n".join(lines[1:-1])
    try:
        result = json.loads(content)
    except ValueError:
        raise ProviderError("Resposta da IA não e JSON válido; tente novamente.") from None
    if not isinstance(result, dict):
        raise ProviderError("Resposta da IA deve ser um objeto JSON.")
    return result
