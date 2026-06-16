"""
Módulo de Modelagem do Grafo.
Responsável por converter os dados do projeto (CSV) em uma estrutura matemática
de Grafo Direcionado Acíclico (DAG) utilizando a biblioteca NetworkX.
"""
import pandas as pd
import networkx as nx

class GrafoProjeto:
    """
    Classe central que representa a rede do projeto. 
    Gerencia os Vértices (tarefas com seus pesos de duração e recursos) 
    e as Arestas Direcionadas (dependências lógicas).
    """
    def __init__(self, caminho_csv):
        self.caminho_csv = caminho_csv
        self.grafo = nx.DiGraph()
        self.carregar_dados()

    def carregar_dados(self):
        """Lê o arquivo CSV e constrói os Vértices (Tarefas) e Arestas (Dependências)."""
        try:
            # Carrega os dados preenchendo as dependências em branco com string vazia
            df = pd.read_csv(self.caminho_csv)
            df['dependencias'] = df['dependencias'].fillna('')
            
            for index, row in df.iterrows():
                tarefa_id = str(row['id']).strip()
                nome = str(row['nome']).strip()
                duracao = int(row['duracao'])
                
                # Suporte opcional a colunas adicionais de PERT (otimista, pessimista) e Recursos
                otimista = int(row['duracao_otimista']) if 'duracao_otimista' in df.columns and pd.notna(row['duracao_otimista']) else max(1, round(duracao * 0.8))
                pessimista = int(row['duracao_pessimista']) if 'duracao_pessimista' in df.columns and pd.notna(row['duracao_pessimista']) else round(duracao * 1.5)
                recursos = int(row['recursos']) if 'recursos' in df.columns and pd.notna(row['recursos']) else 1
                
                # Adiciona o Vértice no grafo com todos os atributos
                self.grafo.add_node(
                    tarefa_id, 
                    duracao=duracao, 
                    nome=nome,
                    duracao_otimista=otimista,
                    duracao_pessimista=pessimista,
                    recursos=recursos
                )
                
                # Pega a lista de dependências separadas por vírgula
                dependencias_str = str(row['dependencias'])
                if dependencias_str:
                    lista_deps = dependencias_str.split(',')
                    for dep in lista_deps:
                        dep = dep.strip()
                        if dep:
                            # Adiciona a Aresta (Seta) saindo da dependência e entrando na tarefa atual
                            self.grafo.add_edge(dep, tarefa_id)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_csv}. Verifique se a pasta 'data' existe e contém o arquivo 'tarefas.csv'.")

    def is_dag_valido(self):
        """Valida matematicamente se não existem ciclos de dependência."""
        return nx.is_directed_acyclic_graph(self.grafo)

    def obter_ciclos(self):
        """Retorna uma lista com os ciclos encontrados, para facilitar a correção no CSV."""
        try:
            return list(nx.simple_cycles(self.grafo))
        except nx.NetworkXNoCycle:
            return []
