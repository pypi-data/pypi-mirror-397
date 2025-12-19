# HighBond SDK

[![Version](https://img.shields.io/badge/version-0.0.7-blue.svg)](https://github.com)
[![Python Version](https://img.shields.io/pypi/pyversions/highbond-sdk.svg)](https://pypi.org/project/highbond-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Versão 0.0.7** - SDK Python em desenvolvimento para a API HighBond com suporte a **Projects**, **Objectives**, **Risks**, **Controls**, **Project Types** e **Issues**.

## ✨ Features

- 🚀 **Paginação automática** - Itera sobre milhares de registros sem se preocupar com paginação
- ⚡ **Multithreading** - Busca múltiplos recursos em paralelo para máxima performance
- 🔄 **Retry automático** - Tratamento inteligente de rate limits e erros de conexão
- 📊 **DataFrames** - Retorne dados em formato pandas DataFrame para análise rápida
- 🛡️ **Tratamento de erros** - Exceções específicas para cada tipo de erro

## 📦 Instalação

```bash
pip install highbond-sdk
```


## 🚀 Quick Start

```python
from highbond_sdk import HighBondClient

# Inicializar cliente
client = HighBondClient(
    token="seu_token_aqui",
    org_id=12345,        # int - ID da organização
    region="us"          # "us", "eu", "au", "ca" ou "sa"
)

# ===== PROJETOS =====
# Listar projetos com paginação manual
response = client.projects.list(page=1, page_size=25)
for projeto in response['data']:
    print(f"Projeto: {projeto['attributes']['name']}")

# Listar todos os projetos (paginação automática)
for projeto in client.projects.list_all():
    print(f"- {projeto['id']}: {projeto['attributes']['name']}")

# Retornar como DataFrame (pandas)
df_projetos = client.projects.list_all(return_pandas=True)
print(df_projetos)

# Buscar projeto específico
projeto = client.projects.get(546355)
print(f"Projeto: {projeto['data']['attributes']['name']}")

# ===== TIPOS DE PROJETO =====
# Listar tipos de projeto como DataFrame
df_tipos = client.project_types.list_all(return_pandas=True)
print(df_tipos)

# ===== RISCOS =====
# Listar todos os riscos da organização (com project_id adicionado automaticamente)
df_todos_riscos = client.risks.list_all(return_pandas=True)
print(df_todos_riscos)

# Listar riscos de um projeto específico
df_riscos_projeto = client.risks.list_by_project(project_id=546355, return_pandas=True)
print(df_riscos_projeto)

# Listar riscos de um objetivo específico
df_riscos_objetivo = client.risks.list_by_objective(objective_id=1990741, return_pandas=True)
print(df_riscos_objetivo)

# ===== CONTROLES =====
# Listar todos os controles
df_controles = client.controls.list_all(return_pandas=True)
print(df_controles)

# Listar controles de um projeto
df_controles_projeto = client.controls.list_by_project(project_id=510117, return_pandas=True)
print(df_controles_projeto)

# Listar controles de um objetivo
df_controles_objetivo = client.controls.list_by_objective(objective_id=1924816, return_pandas=True)
print(df_controles_objetivo)
```

## 📖 Documentação Completa

### Configuração Avançada

```python
from highbond_sdk import HighBondClient

client = HighBondClient(
    token="seu_token",
    org_id=12345,
    region="us",
    timeout=60,              # Timeout em segundos
    max_retries=5,           # Tentativas em caso de erro
    retry_delay=1.0,         # Delay inicial entre tentativas
    page_size=50,            # Itens por página (max 100)
    max_pages=None,          # Sem limite de páginas
    max_workers=5,           # Workers paralelos
    threading_enabled=True   # Habilitar multithreading
)

# Usando context manager
with HighBondClient(token="...", org_id=12345) as client:
    projetos = client.projects.list_all(return_pandas=True)
```

### 📊 Retornando Dados como DataFrame

Todos os métodos de listagem agora suportam o parâmetro `return_pandas`:

```python
import pandas as pd

# JSON (padrão)
riscos_lista = client.risks.list_all()

# DataFrame (pandas)
riscos_df = client.risks.list_all(return_pandas=True)
print(riscos_df.head())

# Funciona em todos os módulos
df_projetos = client.projects.list_all(return_pandas=True)
df_controles = client.controls.list_all(return_pandas=True)
df_objetivos = client.objectives.list_by_project(project_id=123, return_pandas=True)
df_tipos = client.project_types.list_all(return_pandas=True)
```

### Projects

```python
# Listar projetos (paginação manual)
response = client.projects.list(page=1, page_size=50)

# Listar todos (retorna lista)
projetos = client.projects.list_all()
for projeto in projetos:
    print(projeto["attributes"]["name"])

# Ou como DataFrame para análise
df = client.projects.list_all(return_pandas=True)
print(df.head())

# Buscar projeto específico
projeto = client.projects.get(546355)
print(f"Projeto: {projeto['data']['attributes']['name']}")

# Buscar múltiplos em paralelo
projetos = client.projects.get_many([546355, 541532, 510092])

# Criar projeto (campos obrigatórios: name, project_type_id, start_date, target_date)
novo = client.projects.create(
    name="Auditoria 2024",
    project_type_id=42,           # ID do tipo de projeto
    start_date="2024-01-01",      # Data de início (YYYY-MM-DD)
    target_date="2024-12-31",     # Data alvo (YYYY-MM-DD)
    description="Descrição do projeto",
    background="Contexto do projeto"
)

# Atualizar projeto
client.projects.update(546355, name="Novo Nome", status="active")

# Deletar projeto
client.projects.delete(546355)
```

### Project Types

```python
# Listar tipos de projeto
tipos = client.project_types.list_all()

# Como DataFrame (útil para análise)
df_tipos = client.project_types.list_all(return_pandas=True)
print(df_tipos[['id', 'attributes.name', 'attributes.description']])

# Buscar tipo específico
tipo = client.project_types.get(42)

# Buscar múltiplos tipos em paralelo
tipos = client.project_types.get_many([1, 2, 3])
```

### Objectives

```python
# Listar objetivos de um projeto
objetivos = client.objectives.list_by_project(project_id=546355)

# Como DataFrame
df_obj = client.objectives.list_by_project(
    project_id=546355,
    return_pandas=True
)
print(df_obj)

# Buscar objetivo
objetivo = client.objectives.get(project_id=546355, objective_id=1990741)

# Criar objetivo
novo = client.objectives.create(
    project_id=546355,
    title="Revisão de Controles"
)

# Atualizar objetivo
client.objectives.update(
    project_id=546355,
    objective_id=1990741,
    title="Novo Título"
)

# Deletar objetivo
client.objectives.delete(project_id=546355, objective_id=1990741)
```

### Risks

> **IMPORTANTE**: Riscos são criados dentro de **Objectives**, não diretamente em Projects.
> O campo `project_id` é adicionado automaticamente em riscos para melhor rastreabilidade.

```python
# Listar TODOS os riscos da organização (busca projetos → objetivos → riscos)
# Retorna também o project_id de cada risco
riscos_df = client.risks.list_all(return_pandas=True)

# Listar riscos de um projeto específico
riscos_projeto_df = client.risks.list_by_project(
    project_id=546355,
    return_pandas=True  # Retorna como DataFrame
)

# Listar riscos de um objetivo específico
riscos_obj_df = client.risks.list_by_objective(
    objective_id=1990741,
    return_pandas=True
)

# Buscar risco
risco = client.risks.get(risk_id=8454148)

# Buscar múltiplos em paralelo
riscos = client.risks.get_many([8454148, 8454149, 8454150])

# Criar risco (dentro de um objetivo)
novo = client.risks.create(
    objective_id=1990741,
    description="Descrição detalhada do risco",
    title="Título do Risco",
    impact="High",
    likelihood="Medium",
    owner="responsavel@empresa.com"
)

# Atualizar risco
client.risks.update(risk_id=8454148, impact="Low", title="Novo Título")

# Deletar risco
client.risks.delete(risk_id=8454148)
```

### Controls

> **IMPORTANTE**: Controles são criados dentro de **Objectives**, não diretamente em Projects.

```python
# Listar TODOS os controles da organização
controles_df = client.controls.list_all(return_pandas=True)

# Listar controles de um projeto (busca objetivos do projeto → seus controles)
controles_projeto_df = client.controls.list_by_project(
    project_id=510117,
    return_pandas=True
)

# Listar controles de um objetivo
controles_obj_df = client.controls.list_by_objective(
    objective_id=1924816,
    return_pandas=True
)

# Buscar controle
controle = client.controls.get(control_id=789)

# Buscar múltiplos em paralelo
controles = client.controls.get_many([789, 790, 791])

# Criar controle - Internal Control workflow (obrigatórios: frequency, control_type, prevent_detect)
novo_ic = client.controls.create(
    objective_id=1924816,
    description="Descrição detalhada do controle",
    title="Controle de Aprovação",
    frequency="Daily",
    control_type="Manual Control",
    prevent_detect="Prevent",
    owner="responsavel@empresa.com"
)

# Criar controle - Workplan workflow (procedimentos)
novo_wp = client.controls.create(
    objective_id=1924816,
    description="Descrição do procedimento",
    title="Procedimento de Auditoria"
)

# Atualizar controle
client.controls.update(control_id=789, status="Key Control")

# Deletar controle
client.controls.delete(control_id=789)
```

### Issues

> **IMPORTANTE**: Issues são criadas em **Projects** (não em Objectives).
> Campos obrigatórios: `description`, `deficiency_type`, e `owner` (ou `owner_user_uid`).

```python
# Listar todas as issues da organização
issues = client.issues.list_all()

# Listar issues de um projeto
issues_projeto = client.issues.list_by_project(project_id=546355)

# Buscar issue
issue = client.issues.get(issue_id=999)

# Criar issue
nova = client.issues.create(
    project_id=546355,
    description="<p>Descrição detalhada da deficiência</p>",
    deficiency_type="Deficiency",
    owner="responsavel@empresa.com",
    title="Deficiência de Controle",
    severity="High",
    recommendation="<p>Recomendação de ação</p>",
    remediation_date="2024-12-31"
)

# OU usando UID do usuário (sobrescreve owner)
nova = client.issues.create(
    project_id=546355,
    description="Descrição da issue",
    deficiency_type="Significant Deficiency",
    owner_user_uid="3NQ6XzAUxqJMnAQ7n4KF",
    severity="Critical"
)

# Atualizar issue
client.issues.update(
    issue_id=999,
    remediation_status="Closed",
    actual_remediation_date="2024-06-15"
)

# Fechar issue
client.issues.close(issue_id=999)

# Reabrir issue
client.issues.reopen(issue_id=999)
```

## 💡 Exemplos Práticos

### Exemplo 1: Análise de Riscos por Projeto

```python
from highbond_sdk import HighBondClient

client = HighBondClient(
    token="seu_token",
    org_id=12345,
    region="us"
)

# Obter todos os riscos como DataFrame
df_riscos = client.risks.list_all(return_pandas=True)

# Filtrar por project_id
project_id = 546355
riscos_projeto = df_riscos[df_riscos['project_id'] == project_id]

# Agrupar por impacto
print("Riscos por Impacto:")
print(riscos_projeto.groupby('attributes.impact').size())

# Exportar para CSV
riscos_projeto.to_csv('riscos_projeto.csv', index=False)
```

### Exemplo 2: Controles não Vinculados a Riscos

```python
# Obter todos os controles
df_controles = client.controls.list_all(return_pandas=True)

# Identificar controles que podem precisar de riscos
print(f"Total de controles: {len(df_controles)}")

# Verificar status de implementação
print("\nControles por Status:")
print(df_controles['attributes.status'].value_counts())
```

### Exemplo 3: Criar Múltiplos Riscos em Paralelo

```python
# Listar objetivos
objetivos = client.objectives.list_all_by_project(project_id=546355)

# Criar riscos para cada objetivo
for objetivo in objetivos:
    risco = client.risks.create(
        objective_id=objetivo['id'],
        description=f"Risco padrão para {objetivo['attributes']['title']}",
        title=f"Risco - {objetivo['attributes']['title']}",
        impact="Medium",
        likelihood="Medium"
    )
    print(f"Risco criado para objetivo {objetivo['id']}")
```

### Exemplo 4: Dashboard com Estatísticas

```python
import pandas as pd

client = HighBondClient(token="seu_token", org_id=12345, region="us")

# Coletar dados
df_projetos = client.projects.list_all(return_pandas=True)
df_riscos = client.risks.list_all(return_pandas=True)
df_controles = client.controls.list_all(return_pandas=True)

print("=" * 50)
print("DASHBOARD HIGHBOND")
print("=" * 50)

print(f"\nTotal de Projetos: {len(df_projetos)}")
print(f"Total de Riscos: {len(df_riscos)}")
print(f"Total de Controles: {len(df_controles)}")

print("\nRiscos por Impacto:")
print(df_riscos['attributes.impact'].value_counts())


print("\nProjetos Ativos:")
ativos = df_projetos[df_projetos['attributes.status'] == 'active']
print(f"{len(ativos)} projetos")
```

## 🔧 Regiões Suportadas

| Região | Valor | URL Base |
|--------|-------|----------|
| Estados Unidos | `us` | https://apis-us.highbond.com/v1 |
| Europa | `eu` | https://apis-eu.highbond.com/v1 |
| Austrália | `au` | https://apis-au.highbond.com/v1 |
| Canadá | `ca` | https://apis-ca.highbond.com/v1 |
| América do Sul | `sa` | https://apis-sa.diligentoneplatform.com/v1 |

## 📊 Valores de Campos Configuráveis

A maioria dos campos da API HighBond usa **strings configuráveis** no project type.
Os valores abaixo são **exemplos comuns** - verifique as opções disponíveis no seu project type:

| Campo | Exemplos de Valores |
|-------|---------------------|
| `deficiency_type` | "Deficiency", "Significant Deficiency", "Material Weakness" |
| `severity` | "High", "Medium", "Low", "Critical" |
| `impact`/`likelihood` | "High", "Medium", "Low", "Very High", "Very Low" |
| `frequency` | "Daily", "Weekly", "Monthly", "Quarterly", "Annually" |
| `control_type` | "Application/System Control", "Manual Control" |
| `prevent_detect` | "Prevent", "Detect", "N/A" |
| `remediation_status` | "Opened", "In Progress", "Closed" |
| `scope` | "Local", "Regional", "Enterprise" |

## 📋 Requisitos

- Python 3.8+
- requests >= 2.28.0

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.
