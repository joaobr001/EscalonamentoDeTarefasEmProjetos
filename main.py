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
    try:
        projeto = GrafoProjeto(caminho_csv)
    except FileNotFoundError as e:
        print(f"[!] ERRO: {e}")
        return
    
    # A verificação teórica se existem ciclos (se não houver, o programa segue)
    if not projeto.is_dag_valido():
        print("[!] ERRO GRAVE: O Grafo não é acíclico! Encontramos ciclos nas dependências:")
        ciclos = projeto.obter_ciclos()
        for ciclo in ciclos:
            print(f"    Ciclo Encontrado: {' -> '.join(ciclo)} -> {ciclo[0]}")
        print("Corrija o arquivo CSV e tente novamente.")
        return
        
    print("[*] DAG Validado! Não foram encontrados ciclos.")
    
    # Inicia a classe com a lógica matemática
    matematica = AlgoritmosGrafos(projeto)
    
    print("\n[Passo 2] Ordenação Topológica:")
    print(" (A ordem mais segura para não travar nenhuma dependência)")
    ordem_segura = matematica.obter_ordenacao_topologica()
    print(" -> ".join(ordem_segura))
    
    print("\n[Passo 3] Cálculos do Método do Caminho Crítico (CPM):")
    duracao_minima, caminho_critico, todas_folgas = matematica.calcular_caminho_critico()
    
    print(f"[*] Duração Mínima do Projeto Inteiro: {duracao_minima} dias")
    print(f"\n[*] Caminho Crítico (Tarefas GARGALO - Folga ZERO):")
    print(" -> ".join(caminho_critico))
    
    print(f"\n[*] Análise de Folgas (Slack) das demais tarefas:")
    for tarefa, folga in todas_folgas.items():
        if folga > 0:
            print(f"    - A tarefa {tarefa} possui folga de {folga} dia(s).")
            
    print("\n[Passo 4] Exportando a Visualização para Relatório e Slides...")
    Visualizador.plotar_grafo(projeto.grafo, caminho_critico, "grafo_projeto.png")
    
    print("\n" + "="*60)
    print(" EXECUÇÃO CONCLUÍDA COM SUCESSO! ")
    print("="*60)

if __name__ == "__main__":
    executar_sistema()
