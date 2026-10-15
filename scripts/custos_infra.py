"""Custo de infraestrutura + economia unitária (margem por plano) da Arclou.

Rode com: python3 scripts/custos_infra.py
Usa o custo de IA de scripts/custos_ia.py. Valores em R$/mês.
Itens marcados como estimativa devem ser confirmados no checkout/fornecedor.
"""

import importlib.util
import pathlib

_spec = importlib.util.spec_from_file_location("custos_ia", pathlib.Path(__file__).with_name("custos_ia.py"))
ia = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ia)

USD_BRL = ia.USD_BRL

PLANS = {
    "Essencial": {
        "price": 19.90,
        "ai_profile": "Essencial · típico",
        "wa_templates": 15,
    },
    "Pro": {"price": 34.90, "ai_profile": "Pro · típico", "wa_templates": 45},
    # Casal: 2 contas Pro + Casa compartilhada (RN-11). Custos de IA/WhatsApp por pessoa x2.
    "Casal": {
        "price": 49.90,
        "ai_profile": "Pro · típico",
        "wa_templates": 45,
        "seats": 2,
    },
}
FOUNDER_PRO_PRICE = 24.90  # RN-03.4: 50 primeiros, 12 meses
PLAN_MIX = {"Essencial": 0.5, "Pro": 0.3, "Casal": 0.2}  # % das assinaturas

WA_TEMPLATE_USD = 0.008  # template de utilidade fora da janela de 24h (estimativa, Brasil)
GATEWAY_PCT, GATEWAY_FIXED = (
    0.0299,
    0.49,
)  # Asaas cartão à vista/recorrente (tabela padrão)
TAX_BEST, TAX_WORST = 0.06, 0.155  # Simples Nacional Anexo III (Fator R) x Anexo V
CHARGEBACK_PCT = 0.01

# Custos fixos mensais por cenário (R$)
SCENARIOS = {
    "Beta · 50 usuários": {
        "users": 50,
        "fixed": {
            "VPS Hostinger KVM 2 (já contratada, renovação est.)": 69.99,
            "Domínio .com.br (R$ 40/ano)": 3.33,
            "Backup off-site (GCS ~10 GB)": 2.00,
            "Linha/chip dedicado do WhatsApp": 15.00,
            "Firebase Auth, Firestore, Sentry, Langfuse (faixas grátis)": 0.00,
        },
    },
    "Lançamento · 300 usuários": {
        "users": 300,
        "fixed": {
            "VPS Hostinger KVM 2 (já contratada, renovação est.)": 69.99,
            "Domínio .com.br (R$ 40/ano)": 3.33,
            "Backup off-site (GCS ~20 GB)": 3.00,
            "Linha/chip dedicado do WhatsApp": 15.00,
            "Google CASA Tier 2 p/ Gmail (US$ 540/ano, est.)": 540 * USD_BRL / 12,
            "Firebase Auth, Firestore, Sentry, Langfuse (faixas grátis)": 0.00,
        },
    },
    "Crescimento · 1.000 usuários": {
        "users": 1_000,
        "fixed": {
            "VPS Hostinger KVM 4 (4 vCPU/16 GB, upgrade est.)": 139.99,
            "Domínio .com.br (R$ 40/ano)": 3.33,
            "Backup off-site (GCS ~50 GB)": 7.00,
            "Linha/chip dedicado do WhatsApp": 15.00,
            "Google CASA Tier 2 p/ Gmail (US$ 540/ano, est.)": 540 * USD_BRL / 12,
            "Langfuse Cloud Core (US$ 29) ou self-host": 29 * USD_BRL,
            "Firestore acima da cota grátis (est.)": 10.00,
            "Sentry/Firebase Auth (faixas grátis)": 0.00,
        },
    },
}


def plan_unit(plan: str, tax: float) -> dict:
    p = PLANS[plan]
    seats = p.get("seats", 1)
    ai_cost = ia.profile_cost(ia.PROFILES[p["ai_profile"]], True)["usd_safe"] * USD_BRL * seats
    wa = p["wa_templates"] * WA_TEMPLATE_USD * USD_BRL * seats
    gateway = p["price"] * GATEWAY_PCT + GATEWAY_FIXED
    taxes = p["price"] * tax
    chargeback = p["price"] * CHARGEBACK_PCT
    variable = ai_cost + wa + gateway + taxes + chargeback
    return {
        "price": p["price"],
        "IA": ai_cost,
        "WhatsApp": wa,
        "Gateway": gateway,
        "Impostos": taxes,
        "Estornos": chargeback,
        "variable": variable,
        "margin": p["price"] - variable,
    }


def main() -> None:
    for label, tax in (
        ("melhor caso (Anexo III, 6%)", TAX_BEST),
        ("pior caso (Anexo V, 15,5%)", TAX_WORST),
    ):
        print(f"\n== Margem de contribuição por assinante · uso típico · {label}")
        for plan in PLANS:
            u = plan_unit(plan, tax)
            parts = " · ".join(f"{k} {u[k]:.2f}" for k in ("IA", "WhatsApp", "Gateway", "Impostos", "Estornos"))
            print(
                f"  {plan:<10} preço {u['price']:.2f} | variável {u['variable']:.2f} ({parts}) | "
                f"margem {u['margin']:.2f} ({u['margin'] / u['price'] * 100:.0f}%)"
            )

    print("\n== Pior caso (usuário que esgota o plano)")
    for plan, prof, tpl in (
        ("Essencial", "Essencial · teto do plano", 60),
        ("Pro", "Pro · teto do plano", 100),
        ("Casal", "Casal · teto por pessoa", 60),
    ):
        for label, tax in (("6%", TAX_BEST), ("15,5%", TAX_WORST)):
            price = PLANS[plan]["price"]
            seats = PLANS[plan].get("seats", 1)
            ai_cost = ia.profile_cost(ia.PROFILES[prof], True)["usd_safe"] * USD_BRL * seats
            var = (
                ai_cost
                + tpl * WA_TEMPLATE_USD * USD_BRL * seats
                + price * GATEWAY_PCT
                + GATEWAY_FIXED
                + price * tax
                + price * CHARGEBACK_PCT
            )
            print(f"  {plan:<10} imposto {label:<6} variável {var:.2f} margem {price - var:.2f}")
    print("\n== Cenários (assinaturas: 50% Essencial / 30% Pro / 20% Casal, uso típico, impostos 6%)")
    for name, sc in SCENARIOS.items():
        fixed = sum(sc["fixed"].values())
        n = sc["users"]
        revenue = sum(PLANS[p]["price"] * PLAN_MIX[p] * n for p in PLANS)
        variable = sum(plan_unit(p, TAX_BEST)["variable"] * PLAN_MIX[p] * n for p in PLANS)
        avg_margin = sum(plan_unit(p, TAX_BEST)["margin"] * PLAN_MIX[p] for p in PLANS)
        result = revenue - variable - fixed
        print(f"\n  {name}")
        for k, v in sc["fixed"].items():
            print(f"    {k:<62} R$ {v:>8.2f}")
        print(f"    {'Total infraestrutura fixa':<62} R$ {fixed:>8.2f}  (R$ {fixed / n:.2f}/usuário)")
        print(
            f"    Receita R$ {revenue:,.2f} · custos variáveis R$ {variable:,.2f} · resultado R$ {result:,.2f}"
            f" ({result / revenue * 100:.0f}%) · ponto de equilíbrio ≈ {fixed / avg_margin:.0f} assinantes"
        )


if __name__ == "__main__":
    main()
