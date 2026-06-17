"""
Módulo de Saída Visual.
Responsável por gerar artefatos visuais gráficos (PNG) e textuais (ASCII/Gantt)
para apresentar os resultados dos algoritmos matemáticos ao usuário.
"""
import matplotlib.pyplot as plt
import networkx as nx

class Visualizador:
    """
    Classe utilitária puramente estática que isola a lógica de plotagem
    de dados (Matplotlib e formatação em console).
    """
    @staticmethod
    def plotar_grafo(grafo, caminho_critico, caminho_saida="grafo_projeto.png"):
        """Gera e salva um diagrama de rede do projeto inteiro."""
        # Cria uma figura de bom tamanho para leitura no relatório
        plt.figure(figsize=(14, 8))
        
        # Layout spring para espalhar bem os nós no espaço
        pos = nx.spring_layout(grafo, seed=42)
        
        # Cores: Vermelho se pertencer ao caminho crítico, Azul clarinho senão
        node_colors = ['#ff6666' if node in caminho_critico else '#99ccff' for node in grafo.nodes()]
        
        # Dicionário com os textos que vão aparecer dentro de cada bolinha
        labels = {node: f"{node}\n({grafo.nodes[node]['duracao']}d)" for node in grafo.nodes()}
        
        # 1. Desenha as "Bolinhas"
        nx.draw_networkx_nodes(grafo, pos, node_size=3000, node_color=node_colors, edgecolors='black')
        
        # 2. Desenha os Textos
        nx.draw_networkx_labels(grafo, pos, labels=labels, font_size=10, font_weight='bold')
        
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
        
        # Título para o gráfico
        plt.title("DAG: Escalonamento de Tarefas Web\n(Vermelho = Caminho Crítico)", fontsize=16)
        
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
            labels[node] = f"{node}\n(Dia {ini} ao {fim})"
            
        nx.draw_networkx_nodes(grafo, pos, node_size=3500, node_color=node_colors, edgecolors='black')
        nx.draw_networkx_labels(grafo, pos, labels=labels, font_size=9, font_weight='bold')
        nx.draw_networkx_edges(grafo, pos, arrows=True, arrowsize=20)
        
        plt.title("DAG: Escalonamento com Restrição de Recursos\n(Mostrando os Dias de Início e Término Reais)", fontsize=16)
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
        plt.title("Distribuição de Probabilidade do Prazo do Projeto (Monte Carlo)", fontsize=14)
        plt.xlabel("Duração Total do Projeto (Dias)", fontsize=12)
        plt.ylabel("Frequência Absoluta das Ocorrências", fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[*] Histograma exportado com sucesso para: {caminho_saida}")
