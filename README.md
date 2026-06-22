# Escalonamento de Tarefas em Projetos com Teoria dos Grafos

## 1. Visão Geral do Projeto

Este projeto consiste em um sistema de apoio à decisão para o gerenciamento e escalonamento de tarefas em projetos complexos. O sistema utiliza conceitos fundamentais da **Teoria dos Grafos** e da **Pesquisa Operacional** para modelar o projeto como um Grafo Direcionado Acíclico (DAG - *Directed Acyclic Graph*).

Através desta modelagem, a ferramenta permite a extração de métricas críticas que suportam o planejamento gerencial, garantindo que o cronograma do projeto seja otimizado e que os gargalos sejam claramente identificados.

## 2. Fundamentos Teóricos e Algoritmos Implementados

O projeto implementa quatro pilares analíticos principais:

### 2.1. Modelagem em DAG e Ordenação Topológica
A estrutura do projeto garante que dependências circulares não ocorram (o que inviabilizaria a execução do projeto). A ordenação topológica é utilizada para determinar a sequência linear e segura de execução das tarefas, respeitando rigorosamente seus pré-requisitos lógicos.

### 2.2. Método do Caminho Crítico (CPM - Critical Path Method)
O algoritmo percorre o grafo em duas etapas matemáticas:
* **Forward Pass (Ida):** Calcula os tempos de início mais cedo (*Early Start*) e término mais cedo (*Early Finish*) de cada vértice.
* **Backward Pass (Volta):** Calcula os tempos de início mais tarde (*Late Start*) e término mais tarde (*Late Finish*).
* **Cálculo de Folga (Slack):** A diferença matemática entre os tempos mais tarde e mais cedo revela as tarefas de folga zero. A sequência contínua destas tarefas constitui o **Caminho Crítico** (o gargalo do projeto).

### 2.3. Heurística de Alocação de Recursos (RCPSP)
A sigla refere-se ao *Resource-Constrained Project Scheduling Problem*. Diferente do CPM, que pressupõe recursos infinitos, este algoritmo heurístico simula o agendamento em um cenário de escassez (ex: número limitado de desenvolvedores). A prioridade de alocação de recursos em momentos de concorrência é dada pela menor folga (*Slack*), mitigando os atrasos globais do projeto.

### 2.4. Simulação de Monte Carlo (Análise de Sensibilidade/PERT)
O sistema introduz estocasticidade nas estimativas de tempo, simulando a variação da duração das tarefas segundo premissas otimistas e pessimistas. Através de milhares de iterações randômicas iterando sobre o grafo do projeto, o sistema gera uma distribuição de probabilidade, revelando a probabilidade de término do projeto antes, durante ou depois da data ideal estabelecida pelo CPM.

## 3. Estrutura do Código-Fonte

O software foi desenvolvido adotando os princípios de separação de responsabilidades (SoC):

* `data/tarefas.csv`: Base de dados transacional. Define os vértices e arestas do grafo.
* `src/grafo.py`: Módulo responsável por fazer o parser da base de dados, instanciar a estrutura do grafo (utilizando a biblioteca `networkx`) e validar a integridade estrutural (inexistência de ciclos).
* `src/algoritmos.py`: Motor matemático principal. Isola todas as implementações dos algoritmos descritos na Seção 2.
* `src/visualizacao.py`: Módulo gráfico de exportação e plotagem espacial, formatando as saídas dos algoritmos utilizando a biblioteca `matplotlib`.
* `main.py`: Ponto de entrada (Entry Point). Orquestra as chamadas das funções, renderiza a interface em terminal com o usuário utilizando formatações tabulares, e exibe os relatórios.

## 4. Requisitos e Execução

### 4.1. Ambiente Virtual e Dependências
O sistema foi desenvolvido para ser compatível com Python 3.11+. Recomenda-se a criação de um ambiente virtual para instalação isolada das dependências.

```bash
# Criação do ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalação dos pacotes
pip install -r requirements.txt
```

O arquivo `requirements.txt` mapeia bibliotecas-chave como `networkx` (estruturas algébricas de grafos), `matplotlib` (plotagem vetorial plana), `numpy` (matemática escalar) e `pandas` (leitura otimizada de dados I/O).

### 4.2. Formatação dos Dados de Entrada
O sistema lê automaticamente o arquivo `/data/tarefas.csv`. A integridade deste arquivo é crucial. Ele deve possuir obrigatoriamente as seguintes colunas separadas por vírgula:
* `id`: Identificador único do vértice (Ex: T1, T2).
* `nome`: Rótulo descritivo do vértice.
* `duracao`: Peso do vértice (duração nominal esperada).
* `dependencias`: Lista de identificadores de pré-requisitos, separados por vírgula (Ex: T1,T2). Deixe em branco caso seja a raiz inicial.
* `duracao_otimista` / `duracao_pessimista` / `recursos` (Opcionais): Atributos extendidos utilizados nas análises de sensibilidade e RCPSP.

### 4.3. Execução do Software
No terminal bash raiz do diretório, execute:

```bash
python main.py
```

O sistema exibirá um CLI (Command-Line Interface) iterativo. Através da navegação numérica, o usuário pode invocar cálculos de simulação e gerar as saídas tabulares e vetoriais de imagem, cujos processos salvam os arquivos localmente (.png) na pasta de execução.
