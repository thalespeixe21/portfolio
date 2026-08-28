[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=28&pause=1000&color=4FC3F7&width=600&lines=Thales+Peixe;Analista+de+Dados+%26+BI;ETL+%7C+Dashboards+%7C+Automa%C3%A7%C3%A3o)](https://git.io/typing-svg)

# Portfolio — Projetos Reais

[![LinkedIn](https://img.shields.io/badge/LinkedIn-thalespeixe-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/thalespeixe)
[![Email](https://img.shields.io/badge/Email-fabriciopeixe23@gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:fabriciopeixe23@gmail.com)
[![Location](https://img.shields.io/badge/Aracaju,_SE-Brasil-009739?style=for-the-badge&logo=googlemaps&logoColor=white)](#)

---

## Sobre Mim

Analista de Dados com expertise em **infraestrutura de dados, automacao e inteligencia analitica**. Formacao em **Gestao Financeira** (UNIFACS) e **Analise e Desenvolvimento de Sistemas** (CAIRU).

Experiencia solida em construcao de pipelines ETL, modelagem de dados, dashboards estrategicos e rastreamento avancado web/server-side. Proficiente em PostgreSQL, Supabase, Power BI, GA4, Firebase, Make.com, GitHub Actions e CI/CD.

Foco em transformar dados complexos em **insights acionaveis** que impulsionam faturamento, eficiencia operacional e tomada de decisao estrategica.

> **O que me diferencia:** Nao sou so um analista que consome dashboards — eu projeto e construo toda a infraestrutura por tras: da extracao e automacao ETL, passando pelo banco de dados e views SQL, ate os dashboards e relatorios que a diretoria usa no dia a dia.

---

## Stack de Tecnologias

### Dados e Analytics
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Excel](https://img.shields.io/badge/Excel_Avan%C3%A7ado-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)

### Programacao e Automacao
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Make](https://img.shields.io/badge/Make.com-6D00CC?style=for-the-badge&logo=make&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

### Tracking e Marketing Analytics
![GA4](https://img.shields.io/badge/Google_Analytics_4-E37400?style=for-the-badge&logo=googleanalytics&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-DD2C00?style=for-the-badge&logo=firebase&logoColor=white)
![Stape.io](https://img.shields.io/badge/Stape.io_(Server--Side)-333333?style=for-the-badge&logo=googletagmanager&logoColor=white)

### IA e Ferramentas Modernas
![Claude Code](https://img.shields.io/badge/Claude_Code-CC785C?style=for-the-badge&logo=anthropic&logoColor=white)
![MCP Servers](https://img.shields.io/badge/MCP_Servers-000000?style=for-the-badge&logo=anthropic&logoColor=white)

### Frontend e Design
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Figma](https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white)
![Netlify](https://img.shields.io/badge/Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white)

---

## Projetos em Destaque

> Todos os projetos abaixo sao **reais e em producao**. Dados sensiveis (valores financeiros, credenciais, dados pessoais) foram removidos. As empresas e o trabalho feito sao verdadeiros.

| # | Projeto | O que e | Stack | O que gerou de valor |
|:-:|---------|---------|-------|----------------------|
| 1 | **[Infraestrutura de Dados Centralizada](projects/01-infraestrutura-dados/)** | Pipeline ETL com sync automatico a cada 2h via GitHub Actions | `Python` `GitHub Actions` `PostgreSQL/Supabase` `Google Sheets API` | Migrou dados financeiros, marketing e performance para banco centralizado. Reduziu relatorios de horas para segundos. |
| 2 | **[Dashboard Financeiro Web](projects/02-dashboard-financeiro/)** | Dashboard P&L interativo com simulador de cenarios, acessivel de qualquer lugar | `HTML/CSS/JS` `ApexCharts` `Supabase RPC` `Netlify` | Diretoria acessa saude financeira em tempo real sem depender de ferramenta local. |
| 3 | **[Automacao de RH Operacional](projects/03-automacao-rh/)** | Geracao de contratos PJ, admissao/desligamento automatizado, sync de colaboradores | `Python` `Google Sheets API` `PDF/DOCX` `PostgreSQL` | Processo de contratacao de 2h para 15min. Desligamentos padronizados. |
| 4 | **[Reconciliacao e Recuperacao de Valores](projects/04-reconciliacao-pagamentos/)** | Cruzamento de extratos entre plataformas de pagamento, auditoria de dados | `Python` `SQL` `APIs REST` `API Banco Central (PTAX)` | Recuperou volume significativo de valores retidos em plataformas (equivalente a varios meses de faturamento). |

---

## Detalhes dos Projetos

### 1. Infraestrutura de Dados Centralizada (PostgreSQL/Supabase)
**Empresa:** VG Empreendimentos | **Cargo:** Analista Financeiro — Data, Fiscal & Performance

Projetei e implementei infraestrutura de dados centralizada, migrando dados financeiros, marketing e performance para PostgreSQL (Supabase), com sincronizacao automatica a cada 2h via CI/CD (GitHub Actions).

**O que foi construido:**
- **Pipeline ETL completo** para extracao, tratamento e carga de dados de vendas, reembolsos, campanhas (Facebook Ads) e metricas de VSL
- **Views SQL** para P&L mensal, performance de criativos, funil de conversao (Ads → VSL → Venda) — reduzindo tempo de relatorios de horas para segundos
- **Governanca de dados**: backups automaticos, controle de acesso, auditoria e conformidade LGPD
- **Deduplicacao por tipo de fonte**: pedidos (`DISTINCT ON`), gastos com ads (`SUM/GROUP BY`), reembolsos (chave composta)
- **Conversao cambial automatica** usando taxa PTAX oficial do Banco Central, com fallback para fins de semana/feriados
- **Alertas automaticos** de integridade: BRL zerado, anomalias de receita, order IDs nulos

**Numeros reais do banco:** ~30k pedidos, ~11k reembolsos, ~8.4k campanhas, ~4k metricas de video, ~110 registros financeiros diarios

**[Ver case study completo →](projects/01-infraestrutura-dados/)**

---

### 2. Dashboard Financeiro Web
**Empresa:** VG Empreendimentos | **Cargo:** Analista Financeiro — Data, Fiscal & Performance

Antes, os dados financeiros viviam num dashboard Streamlit que rodava localmente em uma maquina. Construi um dashboard web acessivel de qualquer dispositivo.

**O que foi construido:**
- **App web single-page** (HTML/CSS/JS vanilla, ~200KB) com 6 graficos interativos (ApexCharts)
- **Duas funcoes RPC** no PostgreSQL (`SECURITY DEFINER`) — `fn_dashboard_monthly` (historico) e `fn_dashboard_atual` (mes corrente)
- **DRE simplificado** mostrando receita bruta → taxas → receita liquida → despesas → lucro operacional → assinaturas → resultado final
- **Simulador de cenarios** com sliders: ajuste ROAS, gasto com ads, taxa de reembolso — veja o P&L projetado em tempo real
- **7 cenarios** (1 dinamico + 6 preset): "Cortar marketing 30%", "ROAS cai para 1.5x", "Dobrar assinaturas", etc.
- **Calculadora de ROAS breakeven** e **alerta de dependencia de assinaturas**
- Deploy na Netlify com Supabase Auth (email/senha)

**Insight que mudou a estrategia:** Descobri que `subscription_revenue` era separado de `revenue_net`. Assinaturas sao aditivas apos despesas. Em determinado mes, a operacao principal estava negativa, mas a receita recorrente de assinaturas (que representava mais de 85% da receita total no periodo) virou o resultado para positivo — uma distincao que a diretoria nao enxergava antes.

**[Ver case study completo →](projects/02-dashboard-financeiro/)**

---

### 3. Automacao de RH Operacional
**Empresa:** VG Empreendimentos | **Cargo:** Analista Financeiro — Data, Fiscal & Performance

Alem do financeiro, estruturei processos operacionais de RH: contratos PJ, admissoes, desligamentos e gestao de colaboradores.

**O que foi construido:**
- **Gerador de contratos PJ** (Python → DOCX → PDF) com 13 templates, preenchimento automatico de dados
- **Sync diario** (GitHub Actions, 06:00 UTC): planilha RH (Google Sheets) → PostgreSQL via `TRUNCATE + INSERT`
- **Preservacao de emails**: emails corporativos sao salvos antes do TRUNCATE e restaurados apos o INSERT
- **Workflows automatizados** de admissao e desligamento com checklist padronizado
- **Views SQL**: headcount por departamento, folha total, taxa de turnover mensal
- No desligamento: email e **suspenso** (nao deletado), preservando comunicacoes historicas

**Escala:** Multiplos departamentos, dezenas de cargos e niveis de senioridade, dezenas de colaboradores (ativos + desligados)

**[Ver case study completo →](projects/03-automacao-rh/)**

---

### 4. Reconciliacao e Recuperacao de Valores
**Empresa:** VG Empreendimentos | **Cargo:** Analista Financeiro — Data, Fiscal & Performance

Recuperei volume significativo de valores retidos em plataformas de pagamentos (equivalente a varios meses de faturamento), por meio de auditoria de dados, cruzamento de extratos e negociacao direta.

**O que foi construido:**
- **Engine de reconciliacao** que cruza pedidos entre banco de dados e relatorios das plataformas por `order_id`
- **Deduplicacao** que detectou plataforma inflando receita em ~15% por reportar pedidos duplicados
- **Reconciliacao cambial**: compara BRL reportado pela plataforma vs. conversao oficial PTAX, flageia divergencias acima de 2%
- **Rastreamento de liquidacao**: modela prazos e politicas de reserva de cada plataforma (algumas retêm 10% por 180 dias)
- **Gestao de contas a pagar/receber**: conciliacoes e projecoes de fluxo de caixa
- **Relatorios automaticos** de reconciliacao com taxa de match e breakdown de divergencias

**Contexto real:** A empresa opera com multiplas plataformas de pagamento (nacionais e internacionais), cada uma com moedas, formatos e prazos de liquidacao diferentes. Antes da automacao, a reconciliacao era mensal e manual, levando dias. Hoje e diaria e automatizada.

**[Ver case study completo →](projects/04-reconciliacao-pagamentos/)**

---

## Experiencia Profissional

*(Conforme curriculo — mesmas informacoes do LinkedIn)*

| Periodo | Cargo | Empresa | Principais Entregas |
|---------|-------|---------|---------------------|
| Set/2025 — Atual | **Analista Financeiro** — Data, Fiscal & Performance | **VG Empreendimentos** | Infraestrutura de dados centralizada (PostgreSQL/Supabase), pipeline ETL, views SQL para P&L e funil de conversao, governanca de dados, recuperacao de valores retidos em plataformas, processos financeiros/fiscais/operacionais. |
| Set/2025 — Dez/2025 | **Analista de Dados** — Consulting, BI & Analytics | **VK Metriks** | Modelagem fato/dimensao, dashboards Power BI com refresh incremental, integracoes com linguagem M e APIs (Make), lead scoring e segmentacoes. |
| Nov/2024 — Set/2025 | **Analista de Dados** — Marketing & BI Pleno | **EngPlay** | Tracking avancado web/server-side (Stape.io, Firebase), contribuicao para faturamento "6 em 7" com otimizacao de campanhas, automacao de relatorios (Make, VBA, AppScript), dashboards de Marketing/Produto/Vendas. |
| Dez/2024 — Jul/2025 | **Analista de Dados Pleno** | **PasseiMed!** | Dashboards Power BI para areas estrategicas, modelos analiticos (funil, CAC, LTV, cohort, previsoes), automacao de relatorios (M, SQL, VBA, AppScript), ETL, LGPD. |
| Mar/2024 — Out/2024 | **Analista Financeiro Jr.** | **APX NET Telecom** | Indicadores de retencao e cancelamento, dashboards Excel e Power BI, analises para reduzir churn e prever tendencias. |

### Formacao
| Curso | Instituicao | Status |
|-------|-------------|--------|
| Gestao Financeira | UNIFACS | Completa |
| Analise e Desenvolvimento de Sistemas | CAIRU | Completa |

### Certificacoes
- Power BI — Data Mundo
- SQL — Data Mundo
- Tracking Avancado — Web & Server-Side

---

## Como Funciona a Infraestrutura que Construi

```
Dados Brutos (plataformas de pagamento, Facebook Ads, analytics de video, planilhas)
    |
    v
+-----------------------------+
|   Pipeline ETL              |  Python + GitHub Actions (a cada 2h)
|   - Extrair (Sheets API)    |  gspread: get_all_values()
|   - Validar headers         |  Prevenir quebra silenciosa de schema
|   - Deduplicar              |  Estrategia por tipo de fonte
|   - Converter moeda         |  PTAX do Banco Central (taxa oficial)
|   - Carregar                |  Batch upsert no PostgreSQL
+-------------+---------------+
              |
              v
+-----------------------------+
|   PostgreSQL (Supabase)     |
|   - ~30k pedidos            |  Tabelas + Views + Funcoes RPC
|   - ~11k reembolsos         |  Row-level security
|   - ~8.4k campanhas ads     |  Backups automaticos
|   - ~4k metricas video      |  Conformidade LGPD
+-------------+---------------+
              |
        +-----+-----+
        v           v
+------------+ +------------+
| Dashboard  | | Relatorios |  PDF (fpdf2), apresentacoes
| Web (HTML) | | P&L mensal |  Slides, resumos semanais
| Netlify    | | Semanal    |
+------------+ +------------+
```

---

## Estatisticas do GitHub

![Estatisticas](https://github-readme-stats.vercel.app/api?username=thalespeixe21&show_icons=true&theme=tokyonight&hide_border=true&locale=pt-br)

---

> *Todos os projetos sao reais e em producao. Valores financeiros especificos, credenciais e dados pessoais de colaboradores foram omitidos para proteger a confidencialidade. As empresas, cargos e entregas sao verdadeiros e podem ser verificados.*
