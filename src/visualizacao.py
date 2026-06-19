"""
Módulo de Saída Visual.
Responsável por gerar artefatos visuais gráficos (PNG) e textuais (ASCII/Gantt)
para apresentar os resultados dos algoritmos matemáticos ao usuário.
"""
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

class Visualizador:
    """
    Classe utilitária puramente estática que isola a lógica de plotagem
    de dados (Matplotlib e formatação em console).
    """
    @staticmethod
    def plotar_grafo(grafo, caminho_critico, caminho_saida="grafo_projeto.png", titulo="DAG: Grafo Ideal de Escalonamento (CPM)\nCenário Base de Planejamento"):
        """Gera e salva um diagrama de rede do projeto inteiro."""
        # Cria uma figura de bom tamanho para leitura no relatório
        plt.figure(figsize=(14, 8))
        
        # Layout spring para espalhar bem os nós no espaço
        pos = nx.spring_layout(grafo, seed=42)
        
        # Cores: Vermelho se pertencer ao caminho crítico, Azul clarinho senão
        node_colors = ['#ff6666' if node in caminho_critico else '#99ccff' for node in grafo.nodes()]
        
        # Dicionário com os textos que vão aparecer dentro de cada bolinha
        labels = {}
        for node in grafo.nodes():
            duracao = grafo.nodes[node]['duracao']
            folga = grafo.nodes[node].get('folga', 0)
            recursos = grafo.nodes[node].get('recursos', 1)
            labels[node] = f"{node}\n{duracao}d\n{recursos} Devs\nFolga: {folga}d"
        
        # 1. Desenha as "Bolinhas"
        nx.draw_networkx_nodes(grafo, pos, node_size=5000, node_color=node_colors, edgecolors='black')
        
        # 2. Desenha os Textos
        nx.draw_networkx_labels(grafo, pos, labels=labels, font_size=9, font_weight='bold')
        
        # 3. Separar as Arestas comuns das Arestas críticas
        arestas_criticas = []
        arestas_comuns = []
        for u, v in grafo.edges():
            if u in caminho_critico and v in caminho_critico:
                arestas_criticas.append((u, v))
            else:
                arestas_comuns.append((u, v))
                
        # 4. Desenha as Setas (Arestas)
        nx.draw_networkx_edges(grafo, pos, edgelist=arestas_comuns, width=1.5, edge_color='gray', arrows=True, arrowsize=15)
        nx.draw_networkx_edges(grafo, pos, edgelist=arestas_criticas, width=3.0, edge_color='#ff3333', arrows=True, arrowsize=20)
        
        # Título dinâmico para o gráfico
        plt.title(titulo, fontsize=16, fontweight='bold')
        
        # 5. Adicionar Legenda Visual (Movida para o canto inferior direito para não tampar a T2)
        patch_normal = mpatches.Patch(color='#99ccff', label='Tarefa Normal (Possui Folga)')
        patch_critica = mpatches.Patch(color='#ff6666', label='Tarefa Crítica (Sem Folga / Gargalo)')
        line_critica = mlines.Line2D([], [], color='#ff3333', linewidth=3.0, label='Caminho Crítico')
        
        # Colocando a legenda no canto inferior direito
        plt.legend(handles=[patch_normal, patch_critica, line_critica], loc='lower right', fontsize=10, framealpha=0.9)
        
        plt.axis('off')
        plt.tight_layout()
        
        # Salva o arquivo de imagem no computador
        plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
        plt.close()
        
    @staticmethod
    def plotar_linha_tempo_textual(grafo, caminho_critico, agendamento=None):
        """
        Gera e exibe uma Linha do Tempo cronológica em formato de texto estruturado.
        """
        if agendamento is None:
            agendamento = {}
            for n in grafo.nodes():
                agendamento[n] = (grafo.nodes[n].get('es', 0), grafo.nodes[n].get('ef', 0))
                
        # Ordena as tarefas pelo tempo de início, e se empatar, pelo tempo de término
        tarefas_ordenadas = sorted(grafo.nodes(), key=lambda x: (agendamento.get(x, (0, 0))[0], agendamento.get(x, (0, 0))[1]))
        
        print("\n" + "="*80)
        print(" LINHA DO TEMPO CRONOLÓGICA DO DESENVOLVIMENTO WEB ".center(80))
        print("="*80)
        
        for t_id in tarefas_ordenadas:
            inicio, fim = agendamento[t_id]
            critica = t_id in caminho_critico
            recursos = grafo.nodes[t_id].get('recursos', 1)
            nome = grafo.nodes[t_id]['nome']
            
            status_str = "[CRÍTICA - GARGALO]" if critica else "[Normal]"
            
            # Mostra o intervalo de dias
            print(f" ▶ [Dias {inicio:>2} a {fim:>2}] : {t_id:<4} - {nome:<31} | {status_str:<19} ({recursos} dev)")
            
        print("="*80 + "\n")

    @staticmethod
    def plotar_distribuicao_monte_carlo_ascii(duracoes):
        """
        Renderiza uma distribuição de frequências e probabilidade cumulativa
        das durações obtidas na simulação de Monte Carlo.
        """
        from collections import Counter
        
        if not duracoes:
            return
            
        contagem = Counter(duracoes)
        valores_ordenados = sorted(contagem.keys())
        n_sim = len(duracoes)
        
        print("\n" + "="*60)
        print(" DISTRIBUIÇÃO E PROBABILIDADE ACUMULADA (MONTE CARLO) ".center(60))
        print("="*60)
        print(f" Duração Mínima: {min(duracoes)} dias")
        print(f" Duração Média:  {sum(duracoes)/n_sim:.2f} dias")
        print(f" Duração Máxima: {max(duracoes)} dias")
        print("-" * 60)
        print(" Prazo (Dias) | Frequência Relativa | Probal. Acumulada")
        print("-" * 60)
        
        acumulado = 0
        max_freq = max(contagem.values())
        largura_max = 20
        
        for val in valores_ordenados:
            freq = contagem[val]
            pct = (freq / n_sim) * 100
            acumulado += freq
            pct_acum = (acumulado / n_sim) * 100
            
            blocos = int((freq / max_freq) * largura_max)
            barra = "█" * blocos
            
            print(f" {val:>3} dias    | {barra:<20} ({pct:>4.1f}%) | {pct_acum:>5.1f}%")
            
        print("="*60 + "\n")

    @staticmethod
    def plotar_grafo_agendado(grafo, agendamento, caminho_saida="grafo_agendado.png"):
        """
        Gera um diagrama de rede com os rótulos das tarefas atualizados 
        com os dias de início e término exatos após restrição de recursos.
        """
        plt.figure(figsize=(14, 8))
        pos = nx.spring_layout(grafo, seed=42)
        
        # Cor diferente para mostrar que é um grafo restrito
        node_colors = ['#ffcc99' for node in grafo.nodes()]
        
        labels = {}
        for node in grafo.nodes():
            ini, fim = agendamento.get(node, (0, 0))
            labels[node] = f"{node}\nDia {ini}\nao {fim}"
            
        nx.draw_networkx_nodes(grafo, pos, node_size=5000, node_color=node_colors, edgecolors='black')
        nx.draw_networkx_labels(grafo, pos, labels=labels, font_size=9, font_weight='bold')
        nx.draw_networkx_edges(grafo, pos, arrows=True, arrowsize=20)
        
        plt.title("DAG: Cronograma sob Restrição de Equipe (RCPSP)\n(Dias Reais de Alocação calculados via Heurística LPT)", fontsize=16, fontweight='bold')
        
        # Adicionar Legenda Visual
        patch_restrito = mpatches.Patch(color='#ffcc99', label='Tarefa (Sob efeito da Restrição)')
        plt.legend(handles=[patch_restrito], loc='upper left', fontsize=10, framealpha=0.9)
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[*] Grafo agendado exportado com sucesso para: {caminho_saida}")

    @staticmethod
    def plotar_histograma_monte_carlo_png(duracoes, caminho_saida="histograma_monte_carlo.png"):
        """
        Gera e salva um histograma em PNG das simulações de Monte Carlo.
        """
        plt.figure(figsize=(10, 6))
        plt.hist(duracoes, bins=15, color='#99ccff', edgecolor='black', alpha=0.8)
        plt.title("Simulação de Risco (Monte Carlo) / PERT Estocástico\nDistribuição de Probabilidade do Prazo do Projeto", fontsize=14, fontweight='bold')
        plt.xlabel("Duração Total do Projeto (Dias)", fontsize=12)
        plt.ylabel("Frequência Absoluta das Ocorrências", fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[*] Histograma exportado com sucesso para: {caminho_saida}")

    @staticmethod
    def plotar_matrizes(grafo, caminho_saida_adj="imagens/matriz_adjacencia.png", caminho_saida_inc="imagens/matriz_incidencia.png"):
        """
        Gera visualizações em forma de mapa de calor (Heatmap) para as Matrizes de Adjacência e Incidência.
        """
        import os
        os.makedirs("imagens", exist_ok=True)
        
        nodelist = list(grafo.nodes())
        
        import numpy as np
        
        # ==========================================
        # 1. Matriz de Adjacência
        # ==========================================
        adj_matrix = nx.to_numpy_array(grafo, nodelist=nodelist)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(adj_matrix, cmap='Blues', interpolation='none')
        cbar = plt.colorbar(label='Conexão (0 = Nulo, 1 = Dependência)')
        cbar.set_ticks([0, 1])
        plt.xticks(ticks=range(len(nodelist)), labels=nodelist, rotation=45)
        plt.yticks(ticks=range(len(nodelist)), labels=nodelist)
        plt.title("Matriz de Adjacência do Projeto", fontsize=16, fontweight='bold', pad=20)
        
        # Adicionar os números dentro dos quadrados
        for i in range(len(nodelist)):
            for j in range(len(nodelist)):
                val = int(adj_matrix[i, j])
                cor_texto = 'white' if val > 0 else 'black'
                plt.text(j, i, str(val), ha='center', va='center', color=cor_texto, fontweight='bold')
                         
        plt.tight_layout()
        plt.savefig(caminho_saida_adj, dpi=300, bbox_inches='tight')
        plt.close()

        # ==========================================
        # 2. Matriz de Incidência
        # ==========================================
        edgelist = list(grafo.edges())
        inc_matrix = np.zeros((len(nodelist), len(edgelist)))
        for j, (u, v) in enumerate(edgelist):
            u_idx = nodelist.index(u)
            v_idx = nodelist.index(v)
            inc_matrix[u_idx, j] = -1  # Aresta saindo (Tail)
            inc_matrix[v_idx, j] = 1   # Aresta entrando (Head)
        
        # Criar rótulos para as arestas (ex: T1->T2)
        edge_labels = [f"e{idx+1}\n({u}->{v})" for idx, (u, v) in enumerate(edgelist)]
        
        plt.figure(figsize=(14, 8))
        plt.imshow(inc_matrix, cmap='coolwarm', interpolation='none', vmin=-1, vmax=1)
        cbar = plt.colorbar(label='Direção (-1 = Sai, 1 = Entra, 0 = Nulo)')
        cbar.set_ticks([-1, 0, 1])
        plt.xticks(ticks=range(len(edgelist)), labels=edge_labels, rotation=45, ha='right', fontsize=9)
        plt.yticks(ticks=range(len(nodelist)), labels=nodelist)
        plt.title("Matriz de Incidência Direcionada (DAG)", fontsize=16, fontweight='bold', pad=20)
        
        # Adicionar os números dentro dos quadrados
        for i in range(len(nodelist)):
            for j in range(len(edgelist)):
                val = int(inc_matrix[i, j])
                cor_texto = 'white' if abs(val) > 0 else 'black'
                plt.text(j, i, str(val), ha='center', va='center', color=cor_texto, fontweight='bold')
                         
        plt.tight_layout()
        plt.savefig(caminho_saida_inc, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[*] Matrizes visuais exportadas com sucesso para a pasta 'imagens/'.")
