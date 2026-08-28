# Infraestrutura de Dados Centralizada

> Pipeline ETL que extrai, trata e carrega dados de vendas, reembolsos, campanhas (Facebook Ads) e metricas de VSL em um banco PostgreSQL centralizado, com sync automatico a cada 2h via GitHub Actions.

**Empresa:** VG Empreendimentos
**Cargo:** Analista Financeiro — Data, Fiscal & Performance
**Periodo:** Set/2025 — Atual

---

## Contexto

A VG Empreendimentos opera com marketing digital (infoprodutos e nutraceuticos) e utiliza multiplas plataformas de pagamento e anuncio. Antes deste projeto, os dados financeiros, de marketing e performance viviam espalhados em planilhas Google Sheets, sem consolidacao automatica.

## O Que Eu Fiz

Projetei e implementei infraestrutura de dados centralizada (PostgreSQL/Supabase), migrando dados financeiros, marketing e performance com sincronizacao automatica a cada 2h via CI/CD (GitHub Actions).

### Pipeline ETL Completo

Desenvolvi pipeline ETL para extracao, tratamento e carga de:
- **Dados de vendas** (pedidos de multiplas plataformas de pagamento)
- **Reembolsos e chargebacks**
- **Campanhas Facebook Ads** (gastos, impressoes, cliques, conversoes via UTMify)
- **Metricas de VSL** (plays, unique plays, conversoes via VTurb)
- **Taxas de cambio** (PTAX oficial do Banco Central do Brasil)

### Views SQL para Relatorios

Criei views SQL para:
- **P&L mensal** (DRE simplificado)
- **Performance de criativos** (atribuicao first-touch e full-funnel)
- **Funil de conversao** (Ads → VSL → Venda)
- **Analise de reembolsos** (por tipo, por mes, % da receita bruta)
- **Reconciliacao de vendas** (cruzamento entre plataformas)

Isso reduziu o tempo de geracao de relatorios de **horas para segundos**.

### Governanca de Dados

Implantei governanca de dados com:
- Backups automaticos
- Controle de acesso (row-level security)
- Auditoria de integridade (15+ verificacoes automaticas)
- Conformidade LGPD

### Arquitetura

```
+---------------------------------------------------------------+
|                     GitHub Actions (Cron)                       |
|                    A cada 2h / Diario                          |
+--------+--------+--------+--------+--------+-----------------+
         |        |        |        |        |
         v        v        v        v        v
  +----------+ +--------+ +------+ +------+ +-----------+
  |Plataformas| |Plat.   | |UTMify| |VTurb | |API Banco  |
  |de Pagto   | |Reemb.  | |(Ads) | |(VSL) | |Central    |
  |(pedidos)  | |        | |      | |      | |(PTAX)     |
  +----+------+ +---+----+ +--+---+ +--+---+ +-----+-----+
       |            |         |         |           |
       v            v         v         v           v
  +---------------------------------------------------------------+
  |                    Scripts Python (ETL)                         |
  |  - Extracao: gspread get_all_values()                          |
  |  - Validacao de headers (previne quebra silenciosa)             |
  |  - Deduplicacao por tipo de fonte                               |
  |  - Conversao cambial (PTAX com fallback fds/feriado)           |
  |  - Alertas de integridade (BRL zerado, anomalias)              |
  +------------------------------+---------------------------------+
                                 |
                                 v
  +---------------------------------------------------------------+
  |              PostgreSQL (Supabase)                              |
  |                                                                 |
  |  Tabelas: pedidos (~30k) | reembolsos (~11k)                   |
  |           financeiro_diario (~110) | taxas_cambio (~95)         |
  |           campanhas_utmify (~8.4k) | videos_vturb (~4k)        |
  |                                                                 |
  |  Views: vw_dre_mensal | vw_analise_reembolsos                  |
  |         vw_desempenho_produtos | vw_reconciliacao_vendas        |
  |         vw_desempenho_criativos | vw_desempenho_videos          |
  +---------------------------------------------------------------+
```

## Destaques Tecnicos

### Deduplicacao por Tipo de Fonte

Cada fonte exige uma estrategia diferente:

```python
ESTRATEGIAS_DEDUP = {
    "pedidos": {
        "key": ["order_id"],
        "method": "distinct_on",
        # CRITICO: sem isso, receita infla ~15% (confirmado em auditoria)
    },
    "reembolsos": {
        "key": ["order_id", "event_type", "date", "price_usd"],
        "method": "drop_duplicates",
    },
    "campanhas_utmify": {
        "key": ["date", "name"],
        "method": "aggregate_sum",
        # NAO deduplicar — AGREGAR (SUM) por (date, name)
    },
    "videos_vturb": {
        "key": ["account", "date", "nomenclatura"],
        "method": "aggregate_sum",
    },
}
```

### Conversao Cambial (PTAX)

```python
def buscar_ptax(data: str) -> float:
    """Busca taxa PTAX de venda oficial do Banco Central."""
    url = f"{API_BCB}/CotacaoDolarDia(dataCotacao=@d)"
    params = {"@d": f"'{data}'", "$format": "json"}
    response = requests.get(url, params=params)
    dados = response.json()["value"]
    if not dados:
        return buscar_ultima_taxa_disponivel(data)
    return dados[-1]["cotacaoVenda"]
```

### GitHub Actions Workflow

```yaml
name: Sync Dados Financeiros
on:
  schedule:
    - cron: '0 */2 * * *'
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python sync.py
        env:
          DATABASE_URL: ${{ secrets.SUPABASE_URL }}
          DATABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_TOKEN_JSON }}
```

## Licoes Aprendidas (Bugs Reais Corrigidos)

1. **BRL zerado por uma semana inteira** — O sync inseriu valores com BRL = 0 porque a taxa PTAX nao foi buscada corretamente. Adicionei alerta automatico que flageia `usd > 0 AND brl = 0`.

2. **Mapeamento por indice de coluna e fragil** — Quando a planilha fonte ganhou/perdeu colunas, o sync quebrou silenciosamente. Adicionei validacao de header como primeiro passo.

3. **ON CONFLICT nao resolve duplicatas no mesmo batch** — PostgreSQL rejeita duplicatas dentro do mesmo batch. Precisa deduplicar em Python antes de enviar.

4. **Reembolsos zerados por formula apontando para aba inativa** — As formulas no `db_dash_diario` apontavam para `db_digistore` (plataforma encerrada). Dados reais estavam na tabela `reembolsos` mas nao apareciam nos relatorios.

## Stack

| Componente | Tecnologia |
|------------|-----------|
| Linguagem | Python 3.11 (pandas, requests, gspread) |
| Banco de Dados | PostgreSQL (Supabase) |
| Agendador | GitHub Actions (cron a cada 2h) |
| Fonte de Dados | Google Sheets API |
| Taxas de Cambio | API do Banco Central do Brasil (PTAX) |
| Secrets | GitHub Actions Secrets (nunca hardcoded) |

---

## Valor Gerado

| Antes | Depois | Impacto |
|-------|--------|---------|
| Dados espalhados em +10 planilhas sem conexao | Banco PostgreSQL centralizado com 6 tabelas e 6+ views | **100% dos dados financeiros, marketing e performance centralizados** |
| Relatorios montados manualmente (copiar/colar entre abas) | Views SQL prontas, consulta instantanea | **Reducao de ~95% no tempo de geracao de relatorios** (de horas para segundos) |
| Sync manual (alguem precisava rodar scripts) | GitHub Actions rodando a cada 2h, 24/7 | **Zero intervencao humana** — dados sempre atualizados |
| Sem validacao — dados corrompidos passavam despercebidos | 15+ checagens automaticas (BRL zerado, header, duplicatas) | **Deteccao proativa de anomalias** antes de afetar relatorios |
| Conversao cambial feita "no olho" ou planilha | PTAX oficial do Banco Central, com fallback automatico | **Precisao cambial de 100%** — eliminando divergencias de conversao |
| Deduplicacao inexistente | Estrategia por tipo de fonte (DISTINCT, SUM, chave composta) | **Correcao de ~15% de inflacao de receita** que passava despercebida |

**Insight principal:** A infraestrutura viabilizou todos os outros projetos do portfolio. Sem o banco centralizado, nao haveria dashboard web, reconciliacao automatizada nem gestao de RH integrada. Foi o alicerce que transformou decisoes baseadas em "achismo" em decisoes baseadas em dados.
