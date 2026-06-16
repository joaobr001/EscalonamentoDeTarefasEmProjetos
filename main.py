import os
from src.grafo import GrafoProjeto
from src.algoritmos import AlgoritmosGrafos
from src.visualizacao import Visualizador

def executar_sistema():
    print("="*60)
    print(" SISTEMA DE ESCALONAMENTO DE TAREFAS (GRAFOS) ")
    print("="*60)
    
    # Define o caminho do arquivo de dados base
    caminho_csv = os.path.join("data", "tarefas.csv")
    
    print("\n[Passo 1] Construindo o DAG a partir do arquivo CSV...")
    projeto = GrafoProjeto(caminho_csv)
    
    # A verificação teórica se existem ciclos (se não houver, o programa segue)
    if not projeto.is_dag_valido():
        print("[!] ERRO GRAVE: O Grafo não é acíclico! Encontramos ciclos nas dependências.")
        return
    print("[*] DAG Validado! Não foram encontrados ciclos.")
    
    # Inicia a classe com a lógica matemática
    matematica = AlgoritmosGrafos(projeto)
    
    print("\n[Passo 2] Ordenação Topológica:")
    print(" (A ordem mais segura para não travar nenhuma dependência)")
    ordem_segura = matematica.obter_ordenacao_topologica()
    print(" -> ".join(ordem_segura))
    
    print("\n[Passo 3] Cálculos do Método do Caminho Crítico (CPM):")
    duracao_minima, caminho_critico = matematica.calcular_caminho_critico()
    
    print(f"[*] Duração Mínima do Projeto Inteiro: {duracao_minima} dias")
    print(f"[*] As Tarefas Críticas (Folga ZERO - Gargalo):")
    print(" -> ".join(caminho_critico))
    
    print("\n[Passo 4] Exportando a Visualização para Relatório e Slides...")
    Visualizador.plotar_grafo(projeto.grafo, caminho_critico, "grafo_projeto.png")
    
    print("\n" + "="*60)
    print(" EXECUÇÃO CONCLUÍDA COM SUCESSO! ")
    print("="*60)

if __name__ == "__main__":
    executar_sistema()
