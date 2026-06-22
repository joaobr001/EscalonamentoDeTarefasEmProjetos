import os
import sys
from src.grafo import GrafoProjeto
from src.algoritmos import AlgoritmosGrafos
from src.visualizacao import Visualizador

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

def limpar_tela():
    """Limpa o terminal de acordo com o Sistema Operacional."""
    os.system('cls' if os.name == 'nt' else 'clear')

def imprimir_tabela_tarefas(grafo, caminho_critico, todas_folgas):
    """
    Imprime uma tabela formatada no terminal detalhando todas as tarefas do projeto.
    Se a biblioteca 'tabulate' estiver instalada, usa um formato de grade avançado (fancy_grid).
    Caso contrário, faz o fallback manual com formatação de strings do Python.
    
    Args:
        grafo (nx.DiGraph): O grafo do projeto contendo os atributos de cada nó.
        caminho_critico (list): Lista de nós (tarefas) que pertencem ao caminho crítico.
        todas_folgas (dict): Dicionário mapeando cada tarefa para a sua respectiva folga (slack) calculada.
    """
    tabela = []
    for n in grafo.nodes():
        info = grafo.nodes[n]
        critica = "CRÍTICA" if n in caminho_critico else "Normal"
        
        tabela.append([
            n, # ID da tarefa (ex: T1)
            info.get('nome', ''), # Nome descritivo da tarefa
            f"{info['duracao']} dias", # Duração provável
            f"{info.get('duracao_otimista', '?')}/{info.get('duracao', '?')}/{info.get('duracao_pessimista', '?')}", # Tempos de PERT
            f"{info.get('recursos', 1)} recurso(s)", # Esforço exigido
            f"{todas_folgas.get(n, 0)} dias", # Margem de atraso permitida sem afetar o projeto
            critica # Status
        ])
    
    headers = ["ID", "Nome da Tarefa", "Duração", "Otim/Prov/Pess", "Recursos", "Folga", "Status"]
    
    if HAS_TABULATE:
        print(tabulate(tabela, headers=headers, tablefmt="fancy_grid"))
    else:
        # Formatação fallback caso não tenha tabulate instalado no ambiente
        print("-" * 105)
        print(f"{'ID':<4} | {'Nome da Tarefa':<32} | {'Duração':<8} | {'Otim/Prov/Pess':<14} | {'Recursos':<8} | {'Folga':<8} | {'Status':<8}")
        print("-" * 105)
        for r in tabela:
            print(f"{r[0]:<4} | {r[1]:<32} | {r[2]:<8} | {r[3]:<14} | {r[4]:<8} | {r[5]:<8} | {r[6]:<8}")
        print("-" * 105)

def executar_sistema():
    """
    Ponto de entrada principal do sistema CLI.
    Lida com o carregamento do grafo, validação inicial de ciclos (DAG)
    e controla o loop principal do menu interativo de escolhas.
    """
    limpar_tela()
    caminho_csv = os.path.join("data", "tarefas.csv")
    os.makedirs("imagens", exist_ok=True)
    
    print("="*60)
    print(" SISTEMA DE ESCALONAMENTO DE TAREFAS EM PROJETOS".center(60))
    print("="*60)
    
    try:
        projeto = GrafoProjeto(caminho_csv)
        print(f"[+] CSV '{caminho_csv}' carregado com sucesso!")
        print(f"    Total de tarefas: {len(projeto.grafo.nodes)}")
    except FileNotFoundError as e:
        print(f"[!] ERRO: {e}")
        input("\nPressione [Enter] para sair...")
        return
        
    if not projeto.is_dag_valido():
        print("[!] ERRO: O grafo possui ciclos de dependência!")
        ciclos = projeto.obter_ciclos()
        for ciclo in ciclos:
            print(f"    Ciclo: {' -> '.join(ciclo)} -> {ciclo[0]}")
        input("\nPressione [Enter] para sair...")
        return
        
    # Inicializa os algoritmos matemáticos no grafo do projeto
    matematica = AlgoritmosGrafos(projeto)
    
    input("\n[OK] Pressione [Enter] para entrar no sistema...")
    
    while True:
        limpar_tela()
        print("=============================================")
        print("                MENU PRINCIPAL               ")
        print("=============================================")
        print("1. Relatório Geral do Projeto (CPM Determinístico)")
        print("2. Simular Restrição de Recursos")
        print("3. Executar Simulação de Monte Carlo (PERT Estocástico)")
        print("4. Análise de Sensibilidade ('E Se?' - Modificar Duração)")
        print("5. Exportar Diagrama de Rede (Grafo PNG)")
        print("6. Exportar Matrizes Matemáticas do Grafo (Adjacência e Incidência)")
        print("7. Sair")
        print("=============================================")
        opcao = input("\nEscolha uma opção (1-7): ").strip()
        
        # =======================================================
        # OPÇÃO 1: RELATÓRIO GERAL (CPM CLÁSSICO)
        # Calcula o Caminho Crítico determinístico, gera o
        # cronograma cronológico e a tabela detalhada de folgas.
        # =======================================================
        if opcao == "1":
            limpar_tela()
            duracao_minima, caminho_critico, todas_folgas = matematica.calcular_caminho_critico()
            ordem_segura = matematica.obter_ordenacao_topologica()
            
            print("\n" + "="*75)
            print(" ANÁLISE CPM DETERMINÍSTICA ".center(75))
            print("="*75)
            print(f"[*] Duração Mínima Estimada: {duracao_minima} dias")
            print(f"[*] Ordenação Topológica de Execução:")
            print("    " + " -> ".join(ordem_segura))
            print(f"[*] Caminho Crítico (Tarefas Gargalo):")
            print("    " + " -> ".join(caminho_critico))
            print("\n[*] Tabela Detalhada de Tarefas:")
            imprimir_tabela_tarefas(projeto.grafo, caminho_critico, todas_folgas)
            
            # Linha de tempo textual
            Visualizador.plotar_linha_tempo_textual(projeto.grafo, caminho_critico)
            input("\nPressione [Enter] para voltar ao menu...")
            
        # =======================================================
        # OPÇÃO 2: SIMULAÇÃO DE RECURSOS (RCPSP)
        # Escalona as tarefas respeitando um limite máximo de devs,
        # priorizando tarefas com menor folga matemática.
        # =======================================================
        elif opcao == "2":
            limpar_tela()
            print("\n" + "="*60)
            print(" SIMULAR RECURSOS RESTRITOS ".center(60))
            print("="*60)
            try:
                entrada = input("Digite a quantidade máxima de recursos simultâneos (ou Enter para voltar): ").strip()
                if not entrada:
                    continue
                limite = int(entrada)
                if limite <= 0:
                    raise ValueError
            except ValueError:
                print("[!] Entrada inválida. Digite um número inteiro maior que 0.")
                input("\nPressione [Enter] para continuar...")
                continue
                
            try:
                duracao_recursos, agendamento, _ = matematica.simular_recursos_restritos(limite)
            except Exception as e:
                print(f"\n[!] ERRO NA SIMULAÇÃO: {e}")
                print("[!] Aumente a quantidade de recursos ou diminua a exigência de alguma tarefa no CSV.")
                input("\nPressione [Enter] para voltar ao menu...")
                continue
            duracao_minima, caminho_critico, _ = matematica.calcular_caminho_critico()
            
            print("\n" + "="*75)
            print(f" ESCALONAMENTO COM RESTRIÇÃO DE RECURSOS ({limite} UNID) ".center(75))
            print("="*75)
            print(f"[*] Duração teórica mínima (sem limite de recursos): {duracao_minima} dias")
            print(f"[*] Duração real simulada (com restrição de recursos): {duracao_recursos} dias")
            
            atraso = duracao_recursos - duracao_minima
            if atraso > 0:
                print(f"[!] IMPACTO: A falta de recursos gerou um gargalo que atrasou o projeto em {atraso} dia(s).")
            else:
                print("[*] IMPACTO: A quantidade de recursos é perfeitamente dimensionada. Nenhuma tarefa sofreu atraso.")
                
            # Linha de tempo textual sob restrição de recursos
            Visualizador.plotar_linha_tempo_textual(projeto.grafo, caminho_critico, agendamento)
            
            exportar = input("Deseja exportar o diagrama de rede com este agendamento restrito? (s/n): ").strip().lower()
            if exportar == 's':
                nome_arquivo = os.path.join("imagens", f"grafo_recursos_{limite}.png")
                Visualizador.plotar_grafo_agendado(projeto.grafo, agendamento, nome_arquivo)
                
            input("\nPressione [Enter] para voltar ao menu...")
            
        # =======================================================
        # OPÇÃO 3: MONTE CARLO (PERT ESTOCÁSTICO)
        # Simula o projeto N vezes usando durações aleatórias para
        # prever a probabilidade estatística de atrasos e gargalos.
        # =======================================================
        elif opcao == "3":
            limpar_tela()
            print("\n" + "="*60)
            print(" SIMULAÇÃO DE MONTE CARLO ".center(60))
            print("="*60)
            try:
                iteracoes_input = input("Número de simulações (padrão 1000, ou 0 para voltar): ").strip()
                if iteracoes_input == "0":
                    continue
                n_sim = int(iteracoes_input) if iteracoes_input else 1000
                if n_sim <= 0:
                    raise ValueError
            except ValueError:
                print("[!] Entrada inválida. Usando padrão de 1000 simulações.")
                n_sim = 1000
                
            print(f"\nRodando {n_sim} simulações de Monte Carlo no grafo...")
            duracoes_sim, criticidade = matematica.simular_monte_carlo(n_sim)
            
            # Mostra criticidade de tarefas
            print("\n[*] Índice de Criticidade das Tarefas (Frequência no Caminho Crítico):")
            tabela_crit = []
            for node, percent in sorted(criticidade.items(), key=lambda x: -x[1]):
                status = "Alto Risco" if percent > 50 else ("Médio Risco" if percent > 10 else "Baixo Risco")
                tabela_crit.append([node, projeto.grafo.nodes[node]['nome'], f"{percent:.1f}%", status])
                
            headers_crit = ["ID", "Nome da Tarefa", "Frequência no Caminho Crítico", "Classificação de Risco"]
            if HAS_TABULATE:
                print(tabulate(tabela_crit, headers=headers_crit, tablefmt="fancy_grid"))
            else:
                print("-" * 90)
                print(f"{'ID':<4} | {'Nome da Tarefa':<32} | {'Freq. Crítica':<15} | {'Classificação':<15}")
                print("-" * 90)
                for r in tabela_crit:
                    print(f"{r[0]:<4} | {r[1]:<32} | {r[2]:<15} | {r[3]:<15}")
                print("-" * 90)
                
            # Plot da distribuição
            Visualizador.plotar_distribuicao_monte_carlo_ascii(duracoes_sim)
            
            exportar = input("Deseja exportar o histograma de probabilidade em PNG? (s/n): ").strip().lower()
            if exportar == 's':
                Visualizador.plotar_histograma_monte_carlo_png(duracoes_sim, os.path.join("imagens", "histograma_monte_carlo.png"))
                
            input("\nPressione [Enter] para voltar ao menu...")
            
        # =======================================================
        # OPÇÃO 4: ANÁLISE DE SENSIBILIDADE (WHAT-IF)
        # Permite alterar a duração de um nó isolado e recalcula o
        # CPM para medir o impacto no prazo de entrega do projeto.
        # =======================================================
        elif opcao == "4":
            limpar_tela()
            print("\n" + "="*60)
            print(" ANÁLISE DE SENSIBILIDADE ".center(60))
            print("="*60)
            print("\nTarefas disponíveis:")
            for n in projeto.grafo.nodes():
                print(f"  [{n}] {projeto.grafo.nodes[n]['nome']} (Duração atual: {projeto.grafo.nodes[n]['duracao']} dias)")
                
            t_escolhida = input("\nDigite o ID da tarefa para alterar (ex: T3) ou vazio para voltar: ").strip().upper()
            if not t_escolhida:
                continue
            if t_escolhida not in projeto.grafo.nodes():
                print("[!] Tarefa não encontrada.")
                input("\nPressione [Enter] para continuar...")
                continue
                
            try:
                entrada_dur = input(f"Digite a nova duração para {t_escolhida} (dias) ou vazio para cancelar: ").strip()
                if not entrada_dur:
                    continue
                nova_dur = int(entrada_dur)
                if nova_dur < 0:
                    raise ValueError
            except ValueError:
                print("[!] Duração inválida. Digite um número maior ou igual a zero.")
                input("\nPressione [Enter] para continuar...")
                continue
                
            # Salva o valor original
            dur_anterior = projeto.grafo.nodes[t_escolhida]['duracao']
            
            # Calcula o estado antes da mudança
            dur_antes, crit_antes, _ = matematica.calcular_caminho_critico()
            
            # Aplica a alteração usando um grafo temporário para não corromper o estado em caso de erro
            G_simulado = projeto.grafo.copy()
            G_simulado.nodes[t_escolhida]['duracao'] = nova_dur
            alg_temp = AlgoritmosGrafos.__new__(AlgoritmosGrafos)
            alg_temp.G = G_simulado
            
            # Recalcula o estado com a nova duração no grafo temporário
            dur_depois, crit_depois, _ = alg_temp.calcular_caminho_critico()
            
            # Apresenta os resultados da simulação "E Se?"
            print("\n" + "="*65)
            print(" SIMULAÇÃO DE IMPACTO NO CRONOGRAMA (WHAT-IF) ".center(65))
            print("="*65)
            print(f"Tarefa analisada: {t_escolhida} ({projeto.grafo.nodes[t_escolhida]['nome']})")
            print(f"Alteração: Duração mudou de {dur_anterior}d para {nova_dur}d")
            print(f"Duração original do projeto: {dur_antes} dias")
            print(f"Duração simulada do projeto:  {dur_depois} dias")
            
            diferenca = dur_depois - dur_antes
            if diferenca > 0:
                print(f"[!] IMPACTO NEGATIVO: O projeto sofrerá um ATRASO de {diferenca} dia(s).")
            elif diferenca < 0:
                print(f"[+] IMPACTO POSITIVO: O projeto será ANTECIPADO em {abs(diferenca)} dia(s)!")
            else:
                print("[*] SEM IMPACTO: A alteração não afeta o prazo final do projeto (estava na folga da tarefa).")
                
            print(f"\n[*] Caminho Crítico Original: {' -> '.join(crit_antes)}")
            print(f"[*] Caminho Crítico Simulado: {' -> '.join(crit_depois)}")
            
            if set(crit_antes) != set(crit_depois):
                print("[!] Alerta: O caminho crítico do projeto MUDOU com esta alteração!")
            print("="*65 + "\n")
            
            exportar = input("Deseja exportar o grafo com essa simulação? (s/n): ").strip().lower()
            if exportar == 's':
                # Usa o grafo temporário simulado para plotagem
                nome_arquivo = os.path.join("imagens", f"grafo_simulado_{t_escolhida}.png")
                titulo_mutacao = f"DAG: Simulação de Sensibilidade (What-If)\nMutação Injetada na Tarefa {t_escolhida} (Nova Duração: {nova_dur}d)"
                Visualizador.plotar_grafo(G_simulado, crit_depois, nome_arquivo, titulo=titulo_mutacao)
            
            input("\nPressione [Enter] para voltar ao menu...")
            
        # =======================================================
        # OPÇÃO 5: EXPORTAÇÃO DO GRAFO (PNG)
        # Renderiza visualmente os vértices e dependências, pintando
        # a rota crítica com destaque em vermelho usando Matplotlib.
        # =======================================================
        elif opcao == "5":
            limpar_tela()
            print("\n" + "="*60)
            print(" EXPORTAR DIAGRAMA DE REDE ".center(60))
            print("="*60)
            _, crit, _ = matematica.calcular_caminho_critico()
            caminho_saida = os.path.join("imagens", "grafo_projeto.png")
            Visualizador.plotar_grafo(projeto.grafo, crit, caminho_saida)
            print(f"\n[*] Grafo atualizado exportado com sucesso para: '{caminho_saida}'")
            input("\nPressione [Enter] para voltar ao menu...")
            
        # =======================================================
        # OPÇÃO 6: EXPORTAR MATRIZES MATEMÁTICAS (ADJACÊNCIA/INCIDÊNCIA)
        # =======================================================
        elif opcao == "6":
            limpar_tela()
            print("\n" + "="*60)
            print(" GERANDO MATRIZES MATEMÁTICAS (GRAFOS) ".center(60))
            print("="*60)
            print("[*] Renderizando Matriz de Adjacência e de Incidência...")
            Visualizador.plotar_matrizes(projeto.grafo)
            input("\nPressione [Enter] para voltar ao menu...")
            
        elif opcao == "7":
            limpar_tela()
            print("\nObrigado por usar o Sistema de Escalonamento de Tarefas. Até mais!\n")
            break
        else:
            print("[!] Opção inválida. Digite um número de 1 a 7.")
            input("\nPressione [Enter] para voltar ao menu...")

if __name__ == "__main__":
    executar_sistema()
