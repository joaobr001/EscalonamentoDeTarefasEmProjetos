"""
Módulo do Motor Matemático.
Contém a implementação isolada de algoritmos de Teoria dos Grafos e 
Pesquisa Operacional (CPM, Ordenação Topológica, Monte Carlo e RCPSP).
"""
import networkx as nx
import random

class AlgoritmosGrafos:
    """
    Classe que recebe um grafo validado e executa os cálculos matemáticos avançados
    de gestão de cronogramas.
    """
    def __init__(self, projeto_grafo):
        # Acessa o atributo 'grafo' que criamos na classe GrafoProjeto
        self.G = projeto_grafo.grafo

    def obter_ordenacao_topologica(self):
        """
        Gera uma lista linear (ordenação topológica) onde cada tarefa aparece 
        apenas depois de todos os seus pré-requisitos lógicos serem cumpridos.
        Útil para garantir que o projeto seja executado de forma sequencial válida.
        """
        return list(nx.topological_sort(self.G))

    def calcular_caminho_critico(self):
        """
        Executa a matemática do Critical Path Method (CPM) em duas fases (Ida e Volta).
        Identifica o "gargalo" do projeto: a sequência de tarefas que, se atrasar 1 dia, 
        atrasará o projeto inteiro (folga = 0).
        """
        # PASSO 1: Forward Pass (Ida) - Tempo mais cedo (Early Start e Early Finish)
        for node in nx.topological_sort(self.G):
            es = 0 # Early Start começa no Dia 0
            
            predecessores = list(self.G.predecessors(node))
            if predecessores:
                # O ES atual precisa esperar o maior EF de todas as dependências
                es = max([self.G.nodes[p].get('ef', 0) for p in predecessores])
            
            self.G.nodes[node]['es'] = es
            self.G.nodes[node]['ef'] = es + self.G.nodes[node]['duracao']
            
        # A duração mínima do projeto é o término mais cedo da última tarefa
        duracao_total = max([self.G.nodes[n]['ef'] for n in self.G.nodes])
        
        # PASSO 2: Backward Pass (Volta) - Tempo mais tarde (Late Start e Late Finish)
        for node in reversed(list(nx.topological_sort(self.G))):
            lf = duracao_total # Late Finish não pode estourar o tempo total
            
            sucessores = list(self.G.successors(node))
            if sucessores:
                # O LF atual deve ser o menor LS dentre os sucessores
                lf = min([self.G.nodes[s].get('ls', duracao_total) for s in sucessores])
                
            self.G.nodes[node]['lf'] = lf
            self.G.nodes[node]['ls'] = lf - self.G.nodes[node]['duracao']
            
            # PASSO 3: Cálculo da Folga (Slack) -> Late Start - Early Start
            self.G.nodes[node]['folga'] = self.G.nodes[node]['ls'] - self.G.nodes[node]['es']
            
        # PASSO 4: Identifica as tarefas críticas e gera o dicionário completo de folgas
        caminho_critico = []
        todas_folgas = {}
        for n in self.G.nodes:
            folga = self.G.nodes[n]['folga']
            todas_folgas[n] = folga
            if folga == 0:
                caminho_critico.append(n)
        
        return duracao_total, caminho_critico, todas_folgas

    def simular_monte_carlo(self, n_simulacoes=1000):
        """
        Executa simulação de Monte Carlo amostrando durações usando a distribuição
        triangular de PERT (otimista, provável, pessimista).
        Retorna as durações simuladas e a criticidade de cada tarefa.
        """
        
        duracoes_simuladas = []
        contador_critico = {node: 0 for node in self.G.nodes()}
        
        for _ in range(n_simulacoes):
            # Cria um objeto temporário com durações amostradas
            G_temp = self.G.copy()
            for node in G_temp.nodes:
                otimista = G_temp.nodes[node].get('duracao_otimista', 1)
                provavel = G_temp.nodes[node].get('duracao', 1)
                pessimista = G_temp.nodes[node].get('duracao_pessimista', 2)
                
                # Garante que os limites sejam coerentes para a distribuição triangular
                if otimista > provavel:
                    otimista = provavel
                if pessimista < provavel:
                    pessimista = provavel
                if otimista == pessimista:
                    duracao_amostrada = provavel
                else:
                    duracao_amostrada = random.triangular(otimista, pessimista, provavel)
                
                G_temp.nodes[node]['duracao'] = round(duracao_amostrada)
            
            # Calcula o CPM no grafo temporário
            # Forward pass
            for node in nx.topological_sort(G_temp):
                es = 0
                preds = list(G_temp.predecessors(node))
                if preds:
                    es = max([G_temp.nodes[p].get('ef', 0) for p in preds])
                G_temp.nodes[node]['es'] = es
                G_temp.nodes[node]['ef'] = es + G_temp.nodes[node]['duracao']
                
            duracao_total = max([G_temp.nodes[n]['ef'] for n in G_temp.nodes])
            duracoes_simuladas.append(duracao_total)
            
            # Backward pass
            for node in reversed(list(nx.topological_sort(G_temp))):
                lf = duracao_total
                succs = list(G_temp.successors(node))
                if succs:
                    lf = min([G_temp.nodes[s].get('ls', duracao_total) for s in succs])
                G_temp.nodes[node]['lf'] = lf
                G_temp.nodes[node]['ls'] = lf - G_temp.nodes[node]['duracao']
                G_temp.nodes[node]['folga'] = G_temp.nodes[node]['ls'] - G_temp.nodes[node]['es']
                
                if G_temp.nodes[node]['folga'] == 0:
                    contador_critico[node] += 1
                    
        # Calcula porcentagens de criticidade
        criticidade = {node: (count / n_simulacoes) * 100 for node, count in contador_critico.items()}
        
        return duracoes_simuladas, criticidade

    def simular_recursos_restritos(self, limite_recursos):
        """
        Escalona tarefas respeitando a ordenação do grafo e um limite estrito 
        de recursos simultâneos. Retorna a duração total, 
        o agendamento individual e o histórico de uso de recursos.
        """
        # Primeiro calculamos o CPM determinístico para usar a folga como prioridade
        _, _, folgas = self.calcular_caminho_critico()
        
        # Validação prévia: nenhuma tarefa pode exigir mais do que o limite de recursos sozinha
        for t_id in self.G.nodes():
            req_rec = self.G.nodes[t_id].get('recursos', 1)
            if req_rec > limite_recursos:
                raise Exception(
                    f"A tarefa '{t_id}' ({self.G.nodes[t_id].get('nome', '')}) exige {req_rec} recurso(s), "
                    f"mas o limite máximo informado é {limite_recursos} recurso(s)."
                )

        # Tarefas pendentes
        pendentes = list(self.G.nodes())
        # Estado de cada tarefa
        concluidas = set()
        em_andamento = {} # tarefa: tempo_término
        agendamento = {} # tarefa: (inicio, fim)
        
        tempo = 0
        uso_recursos_tempo = {}
        
        while pendentes or em_andamento:
            # 1. Atualiza tarefas concluídas
            for t_id, fim_t in list(em_andamento.items()):
                if fim_t == tempo:
                    concluidas.add(t_id)
                    del em_andamento[t_id]
            
            # 2. Identifica quais tarefas pendentes podem iniciar agora (dependências satisfeitas)
            candidatas = []
            for t_id in pendentes:
                deps = list(self.G.predecessors(t_id))
                if all(d in concluidas for d in deps):
                    candidatas.append(t_id)
            
            # Ordena as candidatas por prioridade:
            # Prioridade 1: Pertencer ao caminho crítico (folga menor)
            # Prioridade 2: Maior duração (heurística LPT - Longest Processing Time)
            candidatas.sort(key=lambda x: (folgas.get(x, 0), -self.G.nodes[x]['duracao']))
            
            # 3. Aloca recursos para as candidatas viáveis
            recursos_em_uso = sum(self.G.nodes[t_id]['recursos'] for t_id in em_andamento)
            
            for t_id in list(candidatas):
                req_rec = self.G.nodes[t_id]['recursos']
                if recursos_em_uso + req_rec <= limite_recursos:
                    em_andamento[t_id] = tempo + self.G.nodes[t_id]['duracao']
                    agendamento[t_id] = (tempo, tempo + self.G.nodes[t_id]['duracao'])
                    recursos_em_uso += req_rec
                    pendentes.remove(t_id)
            
            uso_recursos_tempo[tempo] = recursos_em_uso
            
            # 4. Avança o tempo para o próximo evento (término de alguma tarefa)
            if em_andamento:
                tempo = min(em_andamento.values())
            else:
                if pendentes:
                    raise Exception(f"A quantidade de {limite_recursos} recurso(s) é muito pequena para assumir a tarefa mais pesada restante.")
                break
                
        duracao_total = tempo
        return duracao_total, agendamento, uso_recursos_tempo

