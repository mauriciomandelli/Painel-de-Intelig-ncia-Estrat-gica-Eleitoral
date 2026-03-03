# 📊 Radar Eleitoral SC

Plataforma de inteligência eleitoral para Santa Catarina. Permite analisar dados de votação das eleições de 2018 e 2022 para deputados federais e estaduais.

---

## Funcionalidades

**Acesso livre (após login):**
- Mapa de redutos eleitorais
- Mapa coroplético por município
- Ganhos e perdas 2018 vs 2022
- Evolução temporal
- Performance detalhada por cidade/escola
- Rankings por candidato
- Comparação direta entre candidatos
- Índice de concentração (HHI)
- Análise de coligação
- Benchmark regional
- Alertas de oportunidade
- Ranking geral

**Acesso Premium (⭐):**
- Simulador de coligação 2026
- Análise de transferência de votos
- Relatório automático em PDF
- Comparação rápida com snapshots

---

## Como rodar localmente

### 1. Instale as dependências

```bash
pip install streamlit pandas folium streamlit-folium plotly openpyxl reportlab PyYAML statsmodels
```

### 2. Configure os usuários

Copie o arquivo de exemplo e edite com seus usuários e senhas:

```bash
cp users_exemplo.yaml users.yaml
```

Abra o `users.yaml` e substitua os valores:
- `name`: nome de exibição do usuário
- `password`: senha em texto puro
- `role`: `premium` para acesso total, `free` para acesso básico

> ⚠️ **O arquivo `users.yaml` nunca deve ser enviado ao GitHub.** Ele contém senhas e é ignorado pelo `.gitignore`.

### 3. Adicione os arquivos de dados

Coloque os arquivos `.parquet` na raiz do projeto:
- `depfederalsc2018.parquet`
- `depfederalsc2022.parquet`
- `depestaduasc2018.parquet`
- `depestaduasc2022.parquet`

### 4. Rode o app

```bash
streamlit run app.py
```

---

## Estrutura do projeto

```
radar_eleitoral/
├── app.py                  # Arquivo principal
├── users.yaml              # Credenciais (não enviar ao GitHub)
├── users_exemplo.yaml      # Modelo de credenciais
├── assets/
│   ├── coords_sc.json      # Coordenadas dos municípios
│   └── mesorregioes_sc.json
├── auth/
│   └── login.py            # Sistema de autenticação
├── data/
│   └── loader.py           # Carregamento de dados
├── analysis/
│   └── metrics.py          # Cálculos e métricas
└── ui/                     # Módulos de cada aba
    ├── mapa.py
    ├── mapa_coropletico.py
    ├── ganhos.py
    ├── evolucao.py
    ├── performance.py
    ├── rankings.py
    ├── comparacao.py
    ├── concentracao.py
    ├── coligacao.py
    ├── benchmark.py
    ├── alertas.py
    ├── geral.py
    ├── resumo_executivo.py
    ├── simulador.py
    ├── transferencia.py
    ├── relatorio.py
    └── snapshot.py
```

---

## Adicionar novos usuários

Edite o `users.yaml` seguindo o formato do `users_exemplo.yaml`. Cada usuário precisa de:
- Um nome de login (sem espaços)
- Um nome de exibição
- Uma senha
- Um papel: `premium` ou `free`
