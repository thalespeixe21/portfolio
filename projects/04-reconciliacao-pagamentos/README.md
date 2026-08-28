# Reconciliacao e Recuperacao de Valores

> Auditoria de dados e cruzamento de extratos entre plataformas de pagamento que resultou na recuperacao de volume significativo de valores retidos (equivalente a varios meses de faturamento).

**Empresa:** VG Empreendimentos
**Cargo:** Analista Financeiro — Data, Fiscal & Performance
**Periodo:** Set/2025 — Atual

---

## Contexto

A empresa opera com multiplas plataformas de pagamento (nacionais e internacionais), cada uma com moedas, formatos de order ID, estruturas de taxas e prazos de liquidacao diferentes. Algumas retêm percentuais das vendas por periodos longos (ex: 10% por 180 dias).

Antes, a reconciliacao era mensal e manual (levava dias), divergencias passavam despercebidas, e ninguem sabia exatamente quanto a empresa tinha retido em cada plataforma.

## O Que Eu Fiz

Recuperei **volume significativo de valores retidos** em plataformas de pagamentos (equivalente a varios meses de faturamento), por meio de:
- **Auditoria de dados**: cruzamento sistematico entre base interna e relatorios das plataformas
- **Cruzamento de extratos**: match por `order_id` entre fontes diferentes
- **Negociacao direta**: contato com plataformas para liberacao de valores retidos

### Engine de Reconciliacao

O `order_id` e a chave universal. Uma venda pode ter multiplos eventos: venda inicial, upsell, rebill, reembolso, chargeback.

```python
def reconciliar_pedidos(pedidos_db, relatorios_plataforma):
    """
    Cruza pedidos entre banco e relatorios das plataformas.
    Relacao: 1 order_id -> N eventos
    """
    todos_pedidos = {}
    for plataforma, df in relatorios_plataforma.items():
        for _, row in df.iterrows():
            oid = normalizar_order_id(row["order_id"])
            if oid not in todos_pedidos:
                todos_pedidos[oid] = []
            todos_pedidos[oid].append({
                "plataforma": plataforma,
                "tipo": row["event_type"],
                "valor_usd": row["amount"],
            })

    ids_banco = set(pedidos_db["order_id"].unique())
    ids_plataforma = set(todos_pedidos.keys())

    matched = ids_banco & ids_plataforma
    so_no_banco = ids_banco - ids_plataforma
    so_na_plataforma = ids_plataforma - ids_banco

    return resultado
```

### Deduplicacao que Detectou Inflacao de Receita

Uma plataforma reportava pedidos duplicados, inflando a receita em ~15%:

```python
# CRITICO: sem dedup por order_id, receita infla ~15%
df_pedidos = df_pedidos.drop_duplicates(subset=["order_id"], keep="last")

# Reembolsos: chave composta
df_reembolsos = df_reembolsos.drop_duplicates(
    subset=["order_id", "event_type", "date", "price_usd"], keep="last"
)
```

### Reconciliacao Cambial

Compara BRL da plataforma vs. PTAX oficial do Banco Central:

```python
def reconciliar_cambio(pedidos, taxas_cambio):
    merged = pedidos.merge(taxas_cambio[["date", "ptax_venda"]], on="date", how="left")
    merged["brl_esperado"] = merged["valor_usd"] * merged["ptax_venda"]
    merged["diff_fx_pct"] = abs(
        (merged["brl_reportado"] - merged["brl_esperado"]) / merged["brl_esperado"] * 100
    )
    merged["alerta_fx"] = merged["diff_fx_pct"] > 2.0
    return merged
```

## Resultados Reais

| O que foi feito | Resultado |
|-----------------|-----------|
| Auditoria de valores retidos | Volume recuperado equivalente a varios meses de faturamento |
| Deteccao de duplicatas | Corrigiu ~15% de inflacao de receita |
| Reconciliacao | De mensal/manual para diaria/automatizada |
| Contas a receber | Visibilidade completa de valores retidos e prazos |

## Stack

| Componente | Tecnologia |
|------------|-----------|
| Linguagem | Python (pandas) |
| Banco de dados | PostgreSQL (Supabase) |
| Taxas de cambio | API do Banco Central (PTAX) |
| Chave de reconciliacao | order_id (normalizado entre plataformas) |

---

## Valor Gerado

| Antes | Depois | Impacto |
|-------|--------|---------|
| Reconciliacao mensal e manual (levava dias) | Reconciliacao diaria e automatizada | **Reducao de ~90% no tempo** e frequencia 30x maior (mensal para diaria) |
| Divergencias passavam despercebidas por meses | Deteccao automatica com alerta de divergencia acima de 2% | **Identificacao proativa** — problemas detectados no mesmo dia |
| Receita inflada ~15% por duplicatas de uma plataforma | Deduplicacao sistematica por `order_id` | **Correcao de ~15% de distorcao na receita** — numeros agora confiaveis |
| Ninguem sabia quanto tinha retido em cada plataforma | Rastreamento de liquidacao com prazos e politicas por plataforma | **Visibilidade de 100% dos valores retidos** e previsao de fluxo de caixa |
| Conversao cambial sem padrao (cada planilha usava uma taxa) | PTAX oficial do Banco Central, com reconciliacao automatica | **Precisao cambial padronizada** — eliminou divergencias entre areas |
| Valores retidos "esquecidos" nas plataformas | Auditoria sistematica + negociacao direta | **Recuperacao de volume equivalente a varios meses de faturamento** |

**Insight principal:** O maior valor nao foi a automacao em si — foi a descoberta. Antes de cruzar os dados sistematicamente, a empresa simplesmente nao sabia que tinha valores significativos retidos em plataformas. A deduplicacao revelou que uma plataforma reportava pedidos duplicados, inflando a receita em ~15%. Sem essa correcao, todas as decisoes de investimento em marketing estavam baseadas em numeros errados.
