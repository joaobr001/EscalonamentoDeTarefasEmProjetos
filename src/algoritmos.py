import networkx as nx

class AlgoritmosGrafos:
    def __init__(self, projeto_grafo):
        # Acessa o atributo 'grafo' que criamos na classe GrafoProjeto
        self.G = projeto_grafo.grafo

    def obter_ordenacao_topologica(self):
        """Gera a lista segura de tarefas baseada em pré-requisitos."""
        return list(nx.topological_sort(self.G))

    def calcular_caminho_critico(self):
        """Executa a matemática do CPM (Ida e Volta) para achar o gargalo."""
        G_temp = self.G.copy()
        
        # PASSO 1: Forward Pass (Ida) - Tempo mais cedo (Early Start e Early Finish)
        for node in nx.topological_sort(G_temp):
            es = 0 # Early Start começa no Dia 0
            
            predecessores = list(G_temp.predecessors(node))
            if predecessores:
                # O ES atual precisa esperar o maior EF de todas as dependências
                es = max([G_temp.nodes[p].get('ef', 0) for p in predecessores])
            
            G_temp.nodes[node]['es'] = es
            G_temp.nodes[node]['ef'] = es + G_temp.nodes[node]['duracao']
            
        # A duração mínima do projeto é o término mais cedo da última tarefa
        duracao_total = max([G_temp.nodes[n]['ef'] for n in G_temp.nodes])
        
        # PASSO 2: Backward Pass (Volta) - Tempo mais tarde (Late Start e Late Finish)
        for node in reversed(list(nx.topological_sort(G_temp))):
            lf = duracao_total # Late Finish não pode estourar o tempo total
            
            sucessores = list(G_temp.successors(node))
            if sucessores:
                # O LF atual deve ser o menor LS dentre os sucessores
                lf = min([G_temp.nodes[s].get('ls', duracao_total) for s in sucessores])
                
            G_temp.nodes[node]['lf'] = lf
            G_temp.nodes[node]['ls'] = lf - G_temp.nodes[node]['duracao']
            
            # PASSO 3: Cálculo da Folga (Slack) -> Late Start - Early Start
            G_temp.nodes[node]['folga'] = G_temp.nodes[node]['ls'] - G_temp.nodes[node]['es']
            
        # PASSO 4: Identifica as tarefas críticas e gera o dicionário completo de folgas
        caminho_critico = []
        todas_folgas = {}
        for n in G_temp.nodes:
            folga = G_temp.nodes[n]['folga']
            todas_folgas[n] = folga
            if folga == 0:
                caminho_critico.append(n)
        
        return duracao_total, caminho_critico, todas_folgas
