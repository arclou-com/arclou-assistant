"""Modelo de custo de IA por usuário/mês da Arclou.

Rode com: python3 scripts/custos_ia.py
Todos os números (preços, tokens, perfis de uso) ficam nas constantes abaixo
para recalcular quando preço, prompt ou comportamento de uso mudarem.

Fontes de preço (consultadas em 13/10/2026, endpoint global do Vertex AI):
- https://cloud.google.com/vertex-ai/generative-ai/pricing
- https://ai.google.dev/gemini-api/docs/pricing
"""

USD_BRL = 5.50  # Focus ~5,20 + IOF cartão internacional + folga cambial
SAFETY_MARGIN = 1.25  # retries, conversas mais longas, prompts que crescem

# USD por 1M tokens (global). "cached" = input lido do cache de contexto.
MODELS = {
    "gemini-3.1-flash-lite": {"in": 0.25, "cached": 0.025, "out": 1.50},
    "gemini-3.5-flash-lite": {"in": 0.30, "cached": 0.03, "out": 2.50},
    "gemini-3.8-flash (intro até 31/12/26)": {"in": 0.75, "cached": 0.075, "out": 3.75},
    "gemini-3.8-flash (a partir de 01/01/27)": {
        "in": 1.50,
        "cached": 0.15,
        "out": 7.50,
    },
}

TEXT_MODEL = "gemini-3.1-flash-lite"
IMAGE_MODEL = "gemini-3.8-flash (a partir de 01/01/27)"

# Tokens por evento. Prefixo = system prompt + definições de tools (cacheável).
PREFIX = 2_500
EVENTS = {
    # conversa comum (texto ou áudio já transcrito pelo Whisper local)
    "turn": {
        "model": "text",
        "calls": 1.6,
        "prefix": PREFIX,
        "dynamic": 1_590,
        "out": 250,
        "extra_in": 350,
        "extra_out": 10,
    },  # extra = classificador de escopo (1x por turno)
    # resumo diário das 7h (agenda + contas + cabeçalhos de e-mail)
    "daily_summary": {
        "model": "text",
        "calls": 1,
        "prefix": PREFIX,
        "dynamic": 4_000,
        "out": 350,
    },
    # resumir/buscar/redigir e-mail (corpo dos e-mails entra no contexto)
    "email_op": {
        "model": "text",
        "calls": 1.5,
        "prefix": PREFIX,
        "dynamic": 7_000,
        "out": 500,
    },
    # foto de comprovante: 1.120 tokens da imagem (media_resolution alta) + prompt
    "image": {"model": "image", "calls": 1, "prefix": 0, "dynamic": 1_820, "out": 550},
}

PROFILES = {
    "Essencial · típico": {"turn": 300, "image": 10, "daily_summary": 0, "email_op": 0},
    "Essencial · teto do plano": {
        "turn": 600,
        "image": 30,
        "daily_summary": 0,
        "email_op": 0,
    },
    "Pro · típico": {"turn": 700, "image": 40, "daily_summary": 30, "email_op": 40},
    "Pro · teto do plano": {
        "turn": 1_200,
        "image": 100,
        "daily_summary": 30,
        "email_op": 100,
    },
    "Casal · teto por pessoa": {
        "turn": 900,
        "image": 60,
        "daily_summary": 30,
        "email_op": 60,
    },
    "Pro · teto antigo (2.000/200)": {
        "turn": 2_000,
        "image": 200,
        "daily_summary": 30,
        "email_op": 120,
    },
}


def event_cost(ev: dict, use_cache: bool, text_model: str, image_model: str) -> float:
    price = MODELS[text_model if ev["model"] == "text" else image_model]
    calls = ev["calls"]
    prefix_tokens = ev["prefix"] * calls
    dynamic_tokens = ev["dynamic"] * calls + ev.get("extra_in", 0)
    out_tokens = ev["out"] * calls + ev.get("extra_out", 0)
    cost_in = prefix_tokens * (price["cached"] if use_cache else price["in"]) + dynamic_tokens * price["in"]
    return (cost_in + out_tokens * price["out"]) / 1_000_000


def profile_cost(usage: dict, use_cache: bool, text_model=TEXT_MODEL, image_model=IMAGE_MODEL) -> dict:
    parts = {k: n * event_cost(EVENTS[k], use_cache, text_model, image_model) for k, n in usage.items()}
    total = sum(parts.values())
    return {"parts": parts, "usd": total, "usd_safe": total * SAFETY_MARGIN}


def main() -> None:
    print(f"Câmbio US$ 1 = R$ {USD_BRL:.2f} · margem de segurança {int((SAFETY_MARGIN - 1) * 100)}%\n")
    print("Custo por evento (sem cache / com cache do prefixo):")
    for k, ev in EVENTS.items():
        a = event_cost(ev, False, TEXT_MODEL, IMAGE_MODEL)
        b = event_cost(ev, True, TEXT_MODEL, IMAGE_MODEL)
        print(f"  {k:<14} US$ {a:.5f} / US$ {b:.5f}")
    print()
    header = f"{'Perfil':<28}{'Sem cache':>14}{'Com cache':>14}{'Com cache +margem':>20}"
    print(header)
    print("-" * len(header))
    for name, usage in PROFILES.items():
        nc = profile_cost(usage, False)
        c = profile_cost(usage, True)
        print(
            f"{name:<28}{'R$ %.2f' % (nc['usd'] * USD_BRL):>14}{'R$ %.2f' % (c['usd'] * USD_BRL):>14}"
            f"{'R$ %.2f' % (c['usd_safe'] * USD_BRL):>20}"
        )
    print("\nDetalhe com cache (US$):")
    for name, usage in PROFILES.items():
        c = profile_cost(usage, True)
        detail = ", ".join(f"{k} {v:.3f}" for k, v in c["parts"].items() if v)
        print(f"  {name:<28}{detail}")
    print("\nComparativo de modelos (Pro · teto, com cache + margem):")
    for tm in ("gemini-3.1-flash-lite", "gemini-3.5-flash-lite"):
        for im in (
            "gemini-3.5-flash-lite",
            "gemini-3.8-flash (intro até 31/12/26)",
            "gemini-3.8-flash (a partir de 01/01/27)",
        ):
            c = profile_cost(PROFILES["Pro · teto do plano"], True, tm, im)
            print(f"  texto={tm:<24} imagem={im:<40} R$ {c['usd_safe'] * USD_BRL:.2f}")


if __name__ == "__main__":
    main()
