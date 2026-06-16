import matplotlib.pyplot as plt
import networkx as nx

class Visualizador:
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
        for (u, v) in grafo.edges():
            if u in caminho_critico and v in caminho_critico:
                arestas_criticas.append((u, v))
            else:
                arestas_comuns.append((u, v))
                
        # 4. Desenha as "Setinhas" normais
        nx.draw_networkx_edges(grafo, pos, edgelist=arestas_comuns, arrows=True, arrowsize=20)
        
        # 5. Desenha as "Setinhas" críticas bem destacadas em vermelho
        nx.draw_networkx_edges(grafo, pos, edgelist=arestas_criticas, width=3.0, edge_color='red', arrows=True, arrowsize=25)
        
        # Título para o gráfico
        plt.title("DAG: Escalonamento de Tarefas Web\n(Vermelho = Caminho Crítico)", fontsize=16)
        
        plt.axis('off')
        plt.tight_layout()
        
        # Salva o arquivo de imagem no computador
        plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[*] Visualização Gráfica exportada com sucesso para: {caminho_saida}")
