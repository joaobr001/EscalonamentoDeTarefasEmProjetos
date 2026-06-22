import os
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


class Visualizador:
    """
    Classe utilitária puramente estática que isola a lógica de plotagem
    de dados (Matplotlib e formatação em console).
    """

    # ------------------------------------------------------------------
    # Utilitário interno: layout hierárquico para DAGs
    # ------------------------------------------------------------------
    @staticmethod
    def _calcular_layout_hierarquico(grafo):
        """
        Calcula posições (x, y) para cada nó baseadas no nível topológico,
        sem modificar os atributos do grafo original.
        Produz um layout esquerda → direita, com os nós de cada coluna
        distribuídos verticalmente e centralizados.
        """
        # Nível de cada nó = caminho mais longo a partir das raízes
        niveis = {}
        for node in nx.topological_sort(grafo):
            preds = list(grafo.predecessors(node))
            niveis[node] = 0 if not preds else max(niveis[p] for p in preds) + 1

        # Agrupa nós por nível (coluna)
        por_nivel: dict[int, list] = {}
        for node, nivel in niveis.items():
            por_nivel.setdefault(nivel, []).append(node)

        max_nivel = max(por_nivel.keys(), default=0)

        pos = {}
        for nivel, nos in por_nivel.items():
            x = nivel / max(max_nivel, 1)          # x ∈ [0, 1]
            n = len(nos)
            for i, node in enumerate(sorted(nos)):  # ordenado para reprodutibilidade
                y = (i - (n - 1) / 2) * 0.4  # y com espaçamento maior para não sobrepor
                pos[node] = (x, y)

        return pos

    @staticmethod
    def plotar_grafo(grafo, caminho_critico, caminho_saida="grafo_projeto.png", titulo="DAG: Grafo Ideal de Escalonamento (CPM)\nCenário Base de Planejamento"):
        """
        Gera e salva um diagrama de rede completo do projeto usando Matplotlib e NetworkX.
        Esta função pinta de vermelho as tarefas e arestas que compõem o Caminho Crítico,
        e de azul as tarefas normais que possuem folga.
        
        Args:
            grafo (nx.DiGraph): O grafo do projeto a ser plotado.
            caminho_critico (list): Lista de nós que pertencem ao caminho crítico.
            caminho_saida (str): O caminho do arquivo de imagem PNG que será salvo.
            titulo (str): O título do gráfico.
        """
        # Cria uma figura e eixo estruturado para evitar vazamento de memória e sobreposição
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Layout hierárquico da esquerda para a direita (organiza o fluxo cronológico)
        pos = Visualizador._calcular_layout_hierarquico(grafo)
        
        # Cores: Vermelho se pertencer ao caminho crítico, Azul clarinho senão
        node_colors = ['#ff6666' if node in caminho_critico else '#99ccff' for node in grafo.nodes()]
        
        # Dicionário com os textos que vão aparecer dentro de cada bolinha (generalizado para recursos)
        labels = {}
        for node in grafo.nodes():
            duracao = grafo.nodes[node]['duracao']
            folga = grafo.nodes[node].get('folga', 0)
            recursos = grafo.nodes[node].get('recursos', 1)
            labels[node] = f"{node}\n{duracao}d | R:{recursos}\nFolga:{folga}d"
        
        # 1. Desenha as "Bolinhas"
        nx.draw_networkx_nodes(grafo, pos, ax=ax, node_size=5500, node_color=node_colors, edgecolors='black')
        
        # 2. Desenha os Textos
        nx.draw_networkx_labels(grafo, pos, ax=ax, labels=labels, font_size=8, font_weight='bold')
        
        # 3. Separar as Arestas comuns das Arestas críticas
        arestas_criticas = []
        arestas_comuns = []
        for u, v in grafo.edges():
            if u in caminho_critico and v in caminho_critico:
                arestas_criticas.append((u, v))
            else:
                arestas_comuns.append((u, v))
                
        # 4. Desenha as Setas (Arestas) com folga e conexões limpas (mais visíveis e nítidas)
        nx.draw_networkx_edges(grafo, pos, ax=ax, edgelist=arestas_comuns, width=2.2, edge_color='#555555', arrows=True, arrowsize=18, node_size=5500, connectionstyle='arc3,rad=0.12')
        nx.draw_networkx_edges(grafo, pos, ax=ax, edgelist=arestas_criticas, width=4.0, edge_color='#c0392b', arrows=True, arrowsize=22, node_size=5500, connectionstyle='arc3,rad=0.12')
        
        # Título dinâmico para o gráfico
        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=15)
        
        # 5. Adicionar Legenda Visual (canto inferior direito)
        patch_normal = mpatches.Patch(color='#99ccff', label='Tarefa Normal (Possui Folga)')
        patch_critica = mpatches.Patch(color='#ff6666', label='Tarefa Crítica (Sem Folga / Gargalo)')
        line_critica = mlines.Line2D([], [], color='#c0392b', linewidth=4.0, label='Caminho Crítico')
        
        ax.legend(handles=[patch_normal, patch_critica, line_critica], loc='lower right', fontsize=10, framealpha=0.9)
        
        # Margem de respiro para evitar nós e labels cortados nas bordas
        x_values = [p[0] for p in pos.values()]
        y_values = [p[1] for p in pos.values()]
        x_min, x_max = min(x_values, default=0), max(x_values, default=1)
        y_min, y_max = min(y_values, default=0), max(y_values, default=1)
        ax.set_xlim(x_min - 0.15, x_max + 0.15)
        ax.set_ylim(y_min - 0.25, y_max + 0.25)
        
        ax.axis('off')
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
        print(" LINHA DO TEMPO CRONOLÓGICA DO PROJETO ".center(80))
        print("="*80)
        
        for t_id in tarefas_ordenadas:
            inicio, fim = agendamento[t_id]
            critica = t_id in caminho_critico
            recursos = grafo.nodes[t_id].get('recursos', 1)
            nome = grafo.nodes[t_id]['nome']
            
            status_str = "[CRÍTICA - GARGALO]" if critica else "[Normal]"
            
            # Mostra o intervalo de dias (generalizado para recursos)
            print(f" ▶ [Dias {inicio:>2} a {fim:>2}] : {t_id:<4} - {nome:<31} | {status_str:<19} ({recursos} rec)")
            
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
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Layout hierárquico consistente para o fluxo de dependências
        pos = Visualizador._calcular_layout_hierarquico(grafo)
        
        # Cor diferente para mostrar que é um grafo restrito (bege clássico)
        node_colors = ['#ffcc99' for node in grafo.nodes()]
        
        labels = {}
        for node in grafo.nodes():
            ini, fim = agendamento.get(node, (0, 0))
            labels[node] = f"{node}\nDia {ini}\nao {fim}"
            
        nx.draw_networkx_nodes(grafo, pos, ax=ax, node_size=5500, node_color=node_colors, edgecolors='black')
        nx.draw_networkx_labels(grafo, pos, ax=ax, labels=labels, font_size=8, font_weight='bold')
        nx.draw_networkx_edges(grafo, pos, ax=ax, arrows=True, arrowsize=20, node_size=5500, edge_color='#333333', width=2.2, connectionstyle='arc3,rad=0.12')
        
        ax.set_title("DAG: Cronograma sob Restrição de Recursos (RCPSP)\n(Dias Reais de Alocação calculados via Heurística LPT)", fontsize=16, fontweight='bold', pad=15)
        
        # Adicionar Legenda Visual
        patch_restrito = mpatches.Patch(color='#ffcc99', label='Tarefa (Sob Restrição de Recursos)')
        ax.legend(handles=[patch_restrito], loc='lower right', fontsize=10, framealpha=0.9)
        
        # Margem de respiro para evitar nós cortados nas bordas
        x_values = [p[0] for p in pos.values()]
        y_values = [p[1] for p in pos.values()]
        x_min, x_max = min(x_values, default=0), max(x_values, default=1)
        y_min, y_max = min(y_values, default=0), max(y_values, default=1)
        ax.set_xlim(x_min - 0.15, x_max + 0.15)
        ax.set_ylim(y_min - 0.25, y_max + 0.25)
        
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[*] Grafo agendado exportado com sucesso para: {caminho_saida}")

    @staticmethod
    def plotar_histograma_monte_carlo_png(duracoes, caminho_saida="histograma_monte_carlo.png"):
        """
        Gera e salva um histograma em PNG das simulações de Monte Carlo,
        com linhas estatísticas de média e percentis importantes (P50, P80, P90).
        """
        arr = np.array(duracoes)
        p50 = np.percentile(arr, 50)
        p80 = np.percentile(arr, 80)
        p90 = np.percentile(arr, 90)
        media = np.mean(arr)

        fig, ax = plt.subplots(figsize=(11, 6.5))
        
        # Histograma clássico com fundo branco e cores consistentes
        ax.hist(duracoes, bins=15, color='#99ccff', edgecolor='black', alpha=0.8, label="Frequência")
        
        # Linhas de percentil e média
        ax.axvline(media, color='black', linestyle='--', linewidth=1.5,
                   label=f'Média: {media:.1f}d')
        ax.axvline(p50,  color='#2ca02c', linestyle='-',  linewidth=2.0,
                   label=f'P50: {p50:.0f}d (50% de chance)')
        ax.axvline(p80,  color='#ff7f0e', linestyle='-',  linewidth=2.0,
                   label=f'P80: {p80:.0f}d (80% de chance)')
        ax.axvline(p90,  color='#d62728', linestyle='-',  linewidth=2.0,
                   label=f'P90: {p90:.0f}d (90% de chance)')

        ax.set_title("Simulação de Risco (Monte Carlo) / PERT Estocástico\nDistribuição de Probabilidade do Prazo do Projeto", fontsize=14, fontweight='bold')
        ax.set_xlabel("Duração Total do Projeto (Dias)", fontsize=11)
        ax.set_ylabel("Frequência Absoluta das Ocorrências", fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        ax.legend(loc='upper right', fontsize=9.5, framealpha=0.9)
        
        plt.tight_layout()
        plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[*] Histograma exportado com sucesso para: {caminho_saida}")

    @staticmethod
    def plotar_matrizes(grafo, caminho_saida_adj="imagens/matriz_adjacencia.png", caminho_saida_inc="imagens/matriz_incidencia.png"):
        """
        Gera visualizações em forma de mapa de calor (Heatmap) para as Matrizes de Adjacência e Incidência.
        """
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
