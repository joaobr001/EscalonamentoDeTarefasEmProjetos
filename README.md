# Escalonamento de Tarefas em Projetos

Repositório da solução para a **III Avaliação de Matemática Discreta – Teoria dos Grafos**.

## Projeto
O projeto aplica a Teoria dos Grafos para planejar a construção de um sistema web de gestão. Modelando as etapas de desenvolvimento como um Grafo Direcionado Acíclico (DAG), a ferramenta calcula a atribuição ideal das tarefas, otimiza o tempo total e prevê os gargalos do cronograma.

## Requisitos Originais
- [x] **Modelagem DAG:** Estruturação visual de como as tarefas de desenvolvimento se conectam e dependem entre si.
- [x] **Ordenação Topológica:** Geração automática de um "passo a passo" seguro para a execução do software.
- [x] **Caminho Crítico (CPM):** Identificação das tarefas mais urgentes e que não possuem folga de tempo no cronograma.
- [x] **Balanceamento de Carga (Processadores):** Simulação do escalonamento de múltiplos desenvolvedores (agindo como processadores concorrentes) para as tarefas, sem exceder a capacidade máxima da equipe.

## Diferenciais
A CLI interativa incorpora técnicas avançadas de Pesquisa Operacional para aproximar o modelo acadêmico da realidade do mercado de software:
- **PERT Estocástico (Monte Carlo):** Simula o projeto milhares de vezes (usando durações otimistas e pessimistas) para prever a probabilidade real de atrasos.
- **Restrição de Recursos (RCPSP):** Recalcula o cronograma considerando o limite máximo da equipe (ex: apenas 4 desenvolvedores simultâneos).
- **Análise de Sensibilidade ("What-If"):** Permite alterar a duração de uma tarefa em tempo real para visualizar o impacto em cascata.
- **Visualização Gráfica:** Exporta a rede do projeto automaticamente em PNG, destacando o Caminho Crítico em vermelho.

## Como Executar

**1. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**2. Inicie o menu CLI:**
```bash
python3 main.py
```

## Estrutura de Diretórios
- `data/tarefas.csv`: Banco de dados do projeto (durações, dependências, tamanho da equipe).
- `src/grafo.py`: Módulo responsável por carregar os dados e construir o Grafo.
- `src/algoritmos.py`: Motor matemático contendo o CPM, RCPSP e as simulações estatísticas.
- `src/visualizacao.py`: Exportador gráfico usando *Matplotlib* e *NetworkX*.
