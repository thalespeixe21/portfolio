# Dashboard Financeiro Web

> Dashboard P&L interativo com DRE, simulador de cenarios e KPIs em tempo real, deployado na Netlify e acessivel de qualquer dispositivo.

**Empresa:** VG Empreendimentos
**Cargo:** Analista Financeiro — Data, Fiscal & Performance
**Periodo:** Set/2025 — Atual

---

## Contexto

A empresa usava um dashboard Streamlit que rodava localmente em uma unica maquina. A diretoria dependia de alguem ligar o computador e rodar o script para ver os numeros. Nao havia simulacao de cenarios nem alertas.

## O Que Eu Fiz

Construi um dashboard web acessivel de qualquer lugar, conectado diretamente ao PostgreSQL via funcoes RPC do Supabase.

### Funcionalidades

**Aba Saude Financeira:**
- 4 KPIs hero: Receita Liquida, ROAS, Margem Liquida %, Receita de Assinaturas
- Graficos de evolucao mensal (receita vs. despesas, 12 meses rolling)
- Composicao de custos (marketing, folha, software, operacional)
- DRE simplificado
- Taxas de reembolso e chargeback

**Aba Simulador de Cenarios:**
- Cenario dinamico com sliders (ROAS, gasto ads, taxa reembolso, custos)
- 6 cenarios preset ("Cortar marketing 30%", "ROAS cai para 1.5x", etc.)
- Calculadora de ROAS breakeven
- Alerta de dependencia de assinaturas

**Interface:**
- Sidebar colapsavel, topbar com presets de periodo (3M, 6M, 12M, YTD)
- Dark theme (#0d1117 / #161b22)
- Login via Supabase Auth (email/senha)

### Arquitetura

```
Navegador (qualquer dispositivo)
    |
    | HTTPS (chamadas RPC)
    v
Supabase
    fn_dashboard_monthly() — dados historicos
    fn_dashboard_atual() — mes corrente ao vivo
    Ambas: SECURITY DEFINER
```

### Insight que Mudou a Estrategia

Descobri que `subscription_revenue` e **separado** de `revenue_net`. Assinaturas sao aditivas apos despesas operacionais. Em determinado mes, a operacao principal estava **negativa**, mas a receita recorrente de assinaturas — que representava mais de **85% da receita total** no periodo — virou o resultado para **positivo**. Essa distincao nao era visivel antes — a diretoria achava que a operacao principal era lucrativa por si so.

### Funcao RPC (exemplo)

```sql
CREATE OR REPLACE FUNCTION fn_dashboard_monthly(
    p_start_date DATE DEFAULT '2025-01-01',
    p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    mes TEXT, receita_bruta NUMERIC, receita_liquida NUMERIC,
    despesas_totais NUMERIC, gasto_marketing NUMERIC,
    receita_assinaturas NUMERIC, total_reembolsos NUMERIC,
    qtd_pedidos INTEGER, roas NUMERIC, margem_liquida NUMERIC
) AS $$
    SELECT
        TO_CHAR(date_trunc('month', d.date), 'YYYY-MM'),
        SUM(d.gross_revenue), SUM(d.net_revenue),
        SUM(d.total_expenses), SUM(d.marketing_spend),
        SUM(d.subscription_revenue), SUM(d.refund_total),
        SUM(d.order_count)::INTEGER,
        CASE WHEN SUM(d.marketing_spend) > 0
             THEN ROUND(SUM(d.net_revenue) / SUM(d.marketing_spend), 2) ELSE 0 END,
        CASE WHEN SUM(d.gross_revenue) > 0
             THEN ROUND((SUM(d.net_revenue) - SUM(d.total_expenses))
                        / SUM(d.gross_revenue) * 100, 1) ELSE 0 END
    FROM daily_finance d
    WHERE d.date BETWEEN p_start_date AND p_end_date
    GROUP BY date_trunc('month', d.date) ORDER BY 1;
$$ LANGUAGE sql SECURITY DEFINER;
```

### Decisoes de Design

1. **JS Vanilla** — Dashboard read-heavy, framework adicionaria complexidade sem beneficio. Bundle total: ~200KB.
2. **RPC ao inves de REST** — Duas funcoes SQL retornam exatamente o que o frontend precisa. Sem servidor de API.
3. **Receita de assinaturas como linha separada** — Decisao de negocio. Sem isso, nao da pra ver se a operacao principal e lucrativa.

## Stack

| Componente | Tecnologia |
|------------|-----------|
| Frontend | HTML + CSS + JS (vanilla, arquivo unico) |
| Graficos | ApexCharts 3.49 |
| Backend | Supabase RPC (funcoes SQL, SECURITY DEFINER) |
| Auth | Supabase Auth (email/senha) |
| Hospedagem | Netlify |

---

## Valor Gerado

| Antes | Depois | Impacto |
|-------|--------|---------|
| Dashboard rodava localmente em 1 maquina (Streamlit) | Dashboard web acessivel de qualquer dispositivo | **Acesso 24/7** — diretoria consulta dados sem depender de ninguem |
| Sem simulacao de cenarios | 7 cenarios (1 dinamico + 6 preset) com sliders interativos | **Tomada de decisao em tempo real** — "e se cortarmos marketing 30%?" respondido em segundos |
| Assinaturas misturadas com receita operacional | Separacao clara: receita operacional vs. receita recorrente | **Mudou a estrategia da empresa** — revelou dependencia de assinaturas que ninguem enxergava |
| Dados defasados (precisava rodar script manual) | RPCs conectados direto ao banco, dados ao vivo | **Latencia zero** — mes corrente atualizado em tempo real |
| Sem alertas ou breakeven | Calculadora de ROAS breakeven + alerta de dependencia | **Prevencao proativa** — diretoria sabe o ponto minimo de ROAS antes de decidir investimento |

**Insight principal:** O dashboard revelou que em determinado mes a operacao principal estava negativa, mas assinaturas recorrentes (mais de 85% da receita total) salvaram o resultado. Antes, a diretoria achava que a operacao era lucrativa por si so. Essa visibilidade mudou a forma como a empresa avalia o proprio negocio.
