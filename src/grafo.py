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
        """
        Lê o arquivo CSV de entrada e constrói a estrutura matemática do grafo.
        Cada linha do CSV é convertida em um Vértice (Tarefa) com pesos (Duração, Recursos),
        e as dependências indicadas na coluna são convertidas em Arestas Direcionadas.
        """
        try:
            # Carrega os dados preenchendo as dependências em branco com string vazia
            df = pd.read_csv(self.caminho_csv, skipinitialspace=True)
            df.columns = df.columns.str.strip()
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
        """
        Valida matematicamente se o grafo gerado é um Directed Acyclic Graph (DAG).
        Isso é vital em Gerenciamento de Projetos, pois ciclos indicariam dependências 
        infinitas (ex: T1 depende de T2, que depende de T1), o que é impossível de resolver.
        
        Returns:
            bool: True se não houver ciclos, False caso contrário.
        """
        return nx.is_directed_acyclic_graph(self.grafo)

    def obter_ciclos(self):
        """
        Retorna uma lista com os ciclos lógicos encontrados no grafo,
        o que facilita imensamente o debug e a correção por parte do usuário no CSV.
        """
        try:
            return list(nx.simple_cycles(self.grafo))
        except nx.NetworkXNoCycle:
            return []
