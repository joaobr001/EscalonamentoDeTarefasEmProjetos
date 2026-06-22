# Escalonamento de Tarefas em Projetos com Teoria dos Grafos

Sistema computacional em Python para modelar, analisar e simular o escalonamento de tarefas em projetos por meio de Teoria dos Grafos. O projeto representa um cronograma como um Grafo Direcionado Aciclico (DAG), calcula a sequencia de execucao das tarefas, identifica o caminho critico, avalia restricoes de recursos e estima riscos de atraso por Simulacao de Monte Carlo.

## 1. Objetivo

O objetivo do sistema e apoiar a tomada de decisao no gerenciamento de projetos, transformando tarefas e dependencias em uma estrutura matematica de grafo. A partir dessa modelagem, o programa permite:

* validar se o cronograma possui ciclos de dependencia;
* obter uma ordenacao topologica valida das tarefas;
* calcular a duracao minima do projeto pelo Metodo do Caminho Critico (CPM);
* identificar tarefas criticas e folgas;
* simular escalonamento com quantidade limitada de recursos;
* realizar analise de sensibilidade alterando a duracao de uma tarefa;
* estimar risco de atraso por Simulacao de Monte Carlo;
* exportar diagramas, histograma e matrizes do grafo.

## 2. Modelagem Formal do Problema

O projeto e modelado como um grafo direcionado aciclico:

```text
G = (V, E)
```

Em que:

* `V` e o conjunto de vertices, representando as tarefas do projeto.
* `E` e o conjunto de arestas direcionadas, representando dependencias logicas entre tarefas.
* Uma aresta `(u, v)` indica que a tarefa `u` precisa ser concluida antes do inicio da tarefa `v`.

### 2.1. Tipo de Grafo

O grafo utilizado e:

* **direcionado**, pois as dependencias possuem sentido: uma tarefa antecede outra;
* **aciclico**, pois ciclos tornariam o cronograma impossivel de executar;
* **ponderado nos vertices**, pois as duracoes e recursos estao associados as tarefas, nao as arestas;
* **fracamente conexo**, no cenario atual, pois todas as tarefas pertencem ao mesmo cronograma quando a direcao das arestas e desconsiderada;
* **nao fortemente conexo**, como esperado em um DAG, ja que caminhos de retorno criariam ciclos.

### 2.2. Vertices, Arestas e Pesos

Cada vertice possui os seguintes atributos:

* `id`: identificador da tarefa, como `T1`, `T2`, `T3`;
* `nome`: descricao textual da tarefa;
* `duracao`: duracao nominal usada no CPM deterministico;
* `duracao_otimista`: estimativa inferior usada na Simulacao de Monte Carlo;
* `duracao_pessimista`: estimativa superior usada na Simulacao de Monte Carlo;
* `recursos`: quantidade de recursos necessaria para executar a tarefa.

As arestas representam apenas precedencia. Elas nao possuem duracao propria; o peso temporal do projeto esta concentrado nos vertices.

## 3. Representacoes do Grafo

O sistema utiliza tres representacoes principais:

* **Lista de adjacencia interna do NetworkX**: usada para construir e percorrer o grafo em memoria.
* **Matriz de adjacencia**: matriz `n x n` em que `A[i][j] = 1` quando existe dependencia direta da tarefa `i` para a tarefa `j`.
* **Matriz de incidencia direcionada**: matriz `n x m` que relaciona vertices e arestas, usando `-1` para origem da aresta, `1` para destino e `0` quando o vertice nao participa da aresta.

As matrizes podem ser exportadas pelo menu do sistema na opcao `6`.

## 4. Propriedades Estruturais

O sistema considera propriedades classicas de grafos aplicadas ao cronograma:

* **Grau de entrada**: quantidade de pre-requisitos diretos de uma tarefa.
* **Grau de saida**: quantidade de tarefas que dependem diretamente de uma tarefa.
* **Caminhos**: sequencias validas de tarefas conectadas por dependencias.
* **Ciclos**: dependencias circulares que invalidam o projeto.
* **Componentes**: grupos conectados de tarefas. No cenario atual, o projeto forma um unico componente fracamente conexo.
* **Subgrafos relevantes**: o caminho critico pode ser interpretado como um subgrafo induzido pelas tarefas de folga zero.

A validacao de ciclos e executada antes dos calculos principais. Caso o CSV contenha uma dependencia circular, o sistema informa o ciclo detectado e interrompe a execucao.

## 5. Algoritmos Implementados

### 5.1. Ordenacao Topologica

Determina uma sequencia segura de execucao das tarefas, garantindo que cada tarefa apareca apenas depois de seus pre-requisitos.

No projeto, a ordenacao e obtida com `nx.topological_sort()`, equivalente ao principio do Algoritmo de Kahn: processar vertices com grau de entrada zero e atualizar seus sucessores.

Complexidade:

```text
O(V + E)
```

### 5.2. Deteccao de Ciclos

Antes da execucao dos algoritmos de cronograma, o sistema verifica se o grafo e um DAG usando `nx.is_directed_acyclic_graph()`. Se houver ciclo, `nx.simple_cycles()` auxilia a indicar quais tarefas estao envolvidas.

Complexidade esperada:

```text
O(V + E)
```

### 5.3. Metodo do Caminho Critico (CPM)

O CPM calcula:

* `ES` (*Early Start*): inicio mais cedo;
* `EF` (*Early Finish*): termino mais cedo;
* `LS` (*Late Start*): inicio mais tarde;
* `LF` (*Late Finish*): termino mais tarde;
* `folga`: margem de atraso permitida sem alterar o prazo final.

O algoritmo executa duas passagens:

* **Forward Pass**: percorre o grafo em ordem topologica para calcular `ES` e `EF`.
* **Backward Pass**: percorre o grafo em ordem topologica reversa para calcular `LS`, `LF` e folgas.

Tarefas com folga zero pertencem ao caminho critico.

Complexidade:

```text
O(V + E)
```

### 5.4. Escalonamento com Restricao de Recursos (RCPSP)

O CPM assume recursos ilimitados. Para simular uma situacao mais realista, o sistema implementa uma heuristica para o *Resource-Constrained Project Scheduling Problem*.

A cada instante da simulacao:

* identifica tarefas com dependencias satisfeitas;
* ordena candidatas por menor folga;
* desempata por maior duracao, seguindo a heuristica LPT (*Longest Processing Time*);
* aloca tarefas enquanto houver recursos disponiveis.

O RCPSP e um problema NP-dificil em sua forma geral. Por isso, o sistema usa uma heuristica: ela nao garante solucao otima global, mas produz cronogramas viaveis e interpretaveis para analise.

Complexidade aproximada da implementacao:

```text
O(V^2 log V)
```

### 5.5. Simulacao de Monte Carlo / PERT Estocastico

Para lidar com incerteza nas estimativas, o sistema sorteia duracoes para cada tarefa usando uma distribuicao triangular definida por:

* duracao otimista;
* duracao mais provavel;
* duracao pessimista.

Em cada iteracao, o CPM e recalculado. Ao final, o sistema apresenta:

* distribuicao das duracoes totais simuladas;
* duracao minima, media e maxima;
* probabilidade acumulada por prazo;
* indice de criticidade das tarefas.

Complexidade:

```text
O(n * (V + E))
```

Em que `n` e o numero de simulacoes.

## 6. Resultados do Cenario Atual

Com os dados presentes em `data/tarefas.csv`, o sistema identifica:

* total de tarefas: `10`;
* total de dependencias: `12`;
* grafo valido: `DAG`;
* duracao minima deterministica: `115 dias`;
* ordenacao topologica:

```text
T1 -> T2 -> T3 -> T4 -> T5 -> T6 -> T7 -> T8 -> T9 -> T10
```

* caminho critico:

```text
T1 -> T2 -> T6 -> T7 -> T8 -> T9 -> T10
```

Folgas principais:

* `T3`: 5 dias;
* `T4`: 7 dias;
* `T5`: 5 dias;
* demais tarefas do caminho critico: 0 dias.

Na simulacao com restricao de recursos, o prazo pode aumentar quando tarefas que seriam paralelas precisam ser serializadas por falta de capacidade. Por exemplo, com 5 recursos simultaneos, o cronograma passa para 155 dias no cenario atual.

## 7. Estrutura do Codigo-Fonte

```text
.
├── data/
│   └── tarefas.csv
├── imagens/
│   └── histograma_monte_carlo.png
├── src/
│   ├── __init__.py
│   ├── algoritmos.py
│   ├── grafo.py
│   └── visualizacao.py
├── main.py
├── README.md
└── requirements.txt
```

Responsabilidades:

* `data/tarefas.csv`: base de dados com tarefas, duracoes, recursos e dependencias.
* `src/grafo.py`: leitura do CSV, construcao do grafo e validacao de ciclos.
* `src/algoritmos.py`: ordenacao topologica, CPM, Monte Carlo e escalonamento com recursos restritos.
* `src/visualizacao.py`: diagramas, linha do tempo textual, histograma e matrizes.
* `main.py`: interface de linha de comando e integracao dos modulos.

## 8. Formato dos Dados de Entrada

O arquivo `data/tarefas.csv` deve conter as colunas:

```csv
id,nome,duracao,duracao_otimista,duracao_pessimista,recursos,dependencias
```

Exemplo:

```csv
T5,Desenvolvimento do Backend,40,30,55,4,"T3,T4"
```

Campos:

* `id`: identificador unico da tarefa;
* `nome`: descricao da tarefa;
* `duracao`: duracao nominal;
* `duracao_otimista`: melhor caso;
* `duracao_pessimista`: pior caso;
* `recursos`: recursos necessarios;
* `dependencias`: tarefas predecessoras separadas por virgula.

Quando houver mais de uma dependencia, o campo deve ficar entre aspas, como `"T3,T4"`, para preservar a estrutura do CSV.

## 9. Instalacao

Recomenda-se Python 3.11 ou superior.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Dependencias principais:

* `networkx`: modelagem e algoritmos de grafos;
* `pandas`: leitura da base CSV;
* `matplotlib`: geracao de graficos e diagramas;
* `numpy`: calculos numericos;
* `tabulate`: tabelas no terminal.

## 10. Execucao

Na raiz do projeto:

```bash
python main.py
```

O menu principal apresenta:

```text
1. Relatorio Geral do Projeto (CPM Deterministico)
2. Simular Restricao de Recursos
3. Executar Simulacao de Monte Carlo (PERT Estocastico)
4. Analise de Sensibilidade ('E Se?' - Modificar Duracao)
5. Exportar Diagrama de Rede (Grafo PNG)
6. Exportar Matrizes Matematicas do Grafo (Adjacencia e Incidencia)
7. Sair
```

## 11. Saidas Geradas

O sistema pode gerar arquivos PNG na pasta `imagens/`, incluindo:

* diagrama do grafo com caminho critico destacado;
* diagrama do cronograma sob restricao de recursos;
* histograma da Simulacao de Monte Carlo;
* matriz de adjacencia;
* matriz de incidencia direcionada.

Essas saidas apoiam a interpretacao dos resultados e podem ser usadas no relatorio tecnico e na apresentacao.

## 12. Relacao com a Avaliacao

Este projeto atende ao tema de escalonamento de tarefas em projetos, proposto na avaliacao de Teoria dos Grafos Aplicada a Computacao. A aplicacao cobre:

* modelagem de um problema real usando grafos;
* uso explicito de DAG;
* vertices, arestas, pesos e propriedades estruturais;
* representacao por matriz de adjacencia e matriz de incidencia;
* ordenacao topologica;
* deteccao de ciclos;
* algoritmo classico de grafos aplicado a um contexto real;
* visualizacoes e resultados numericos;
* analise de eficiencia e complexidade dos algoritmos.

## 13. Possiveis Extensoes

Melhorias futuras possiveis:

* adicionar testes automatizados para validar CPM, ciclos e dados invalidos;
* validar dependencias inexistentes no CSV antes da criacao das arestas;
* gerar grafico de Gantt;
* implementar interface web ou GUI;
* comparar diferentes heuristicas para RCPSP;
* permitir atualizacao dinamica do cronograma durante o projeto.
