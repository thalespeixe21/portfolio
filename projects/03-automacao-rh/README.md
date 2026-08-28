# Automacao de RH Operacional

> Geracao de contratos PJ, admissao/desligamento automatizado e sync de dados organizacionais.

**Empresa:** VG Empreendimentos
**Cargo:** Analista Financeiro — Data, Fiscal & Performance
**Periodo:** Set/2025 — Atual

---

## Contexto

Alem do financeiro, estruturei processos operacionais de RH. A empresa opera com prestadores PJ, organizados em multiplos departamentos e niveis de senioridade. Antes, tudo era manual: contratos preenchidos no Word, planilhas atualizadas a mao, desligamentos sem padrao.

## O Que Eu Fiz

### Geracao Automatica de Contratos PJ

Script Python que gera contrato pronto para assinar (DOCX + PDF):
- 13 templates para diferentes tipos de contrato
- Preenchimento automatico de todos os campos

```python
def gerar_contrato(dados: dict) -> tuple[str, str]:
    template = carregar_template("pj_padrao")
    contrato = template.render(
        nome_prestador=dados["nome"],
        documento=dados["documento"],
        cargo=dados["cargo"],
        valor_mensal=formatar_brl(dados["salario"]),
        data_inicio=dados["data_inicio"].strftime("%d/%m/%Y"),
    )
    docx = salvar_docx(contrato, dados["nome"])
    pdf = converter_para_pdf(docx)
    return docx, pdf
```

### Sync Diario de Colaboradores

GitHub Actions rodando as 06:00 UTC:
- Le planilha de RH (Google Sheets — fonte de verdade)
- Carrega no PostgreSQL via TRUNCATE + INSERT
- **Preserva emails corporativos** (campo derivado, nao existe na planilha)

```python
def sync_colaboradores(dados_planilha, db):
    emails = {r["nome"]: r["email"] for r in db.query("SELECT nome, email FROM colaboradores")}
    db.execute("TRUNCATE colaboradores CASCADE")
    for row in dados_planilha:
        row["email"] = emails.get(row["nome"])
        if row["status"] == "desligado":
            row["email_suspenso"] = True
        db.insert("colaboradores", row)
```

### Workflows Automatizados

**Admissao:** Gerar contrato → Atualizar planilha → Sync banco → Criar email → Adicionar no Slack

**Desligamento:** Gerar distrato → Marcar desligado → Suspender email (nao deletar) → Sync banco → Calcular pagamento final

### Views Analiticas

```sql
CREATE VIEW vw_headcount_departamento AS
SELECT d.nome, COUNT(*) as headcount, SUM(c.salario) as folha_total
FROM colaboradores c
JOIN cargos ca ON c.cargo_id = ca.id
JOIN departamentos d ON ca.departamento_id = d.id
WHERE c.status = 'ativo'
GROUP BY d.nome;
```

## Escala

O sistema gerencia multiplos departamentos, dezenas de cargos, diversos niveis de senioridade e dezenas de colaboradores (ativos + desligados). Numeros exatos omitidos por confidencialidade.

## Stack

| Componente | Tecnologia |
|------------|-----------|
| Contratos | Python (docx, fpdf2) |
| Fonte de dados | Google Sheets API (gspread) |
| Banco de dados | PostgreSQL (Supabase) |
| Agendador | GitHub Actions (diario, 06:00 UTC) |

---

## Valor Gerado

| Antes | Depois | Impacto |
|-------|--------|---------|
| Contrato preenchido manualmente no Word (~2h por admissao) | Script gera DOCX + PDF em segundos com todos os campos preenchidos | **Reducao de ~87% no tempo** (de 2h para ~15min por admissao) |
| Planilha de RH atualizada manualmente | Sync diario automatico (GitHub Actions, 06:00 UTC) | **Zero atraso** — banco sempre reflete a planilha fonte |
| Emails corporativos perdidos no TRUNCATE | Preservacao automatica: salva antes, restaura depois | **100% dos emails preservados** — historico de comunicacao intacto |
| Desligamento sem padrao (cada gestor fazia diferente) | Workflow padronizado: distrato + suspensao de email + sync | **Processo padronizado e auditavel** — nenhum passo esquecido |
| Sem visao consolidada de headcount e custos | Views SQL com headcount por departamento, turnover, distribuicao | **Visibilidade completa** para decisoes de contratacao e orcamento |

**Insight principal:** A automacao nao so economizou tempo — eliminou erros humanos. Antes, ja aconteceu de um colaborador ser desligado e o email continuar ativo por semanas, ou de um contrato sair com dados errados. Com o workflow padronizado, cada etapa e executada na ordem certa, sem depender de checklist manual.
