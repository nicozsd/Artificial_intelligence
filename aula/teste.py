from typing import List, Tuple, Set, Dict
import random
import math
import time
from copy import deepcopy
from itertools import combinations

def ler_cidades_txt(arquivo: str) -> dict:
    """
    Lê as coordenadas das cidades de um arquivo txt
    """
    cidades = {}
    
    with open(arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith('cidade'):
                partes = linha.split()
                if len(partes) >= 3:
                    x, y = float(partes[1]), float(partes[2])
                    # Multiplica por 100 para escala adequada
                    if x < 100 and y < 100:
                        x, y = x * 100, y * 100
                    cidades[int(partes[0])] = (x, y)
    
    return cidades

def calcular_distancia(cidade1: Tuple[float, float], cidade2: Tuple[float, float]) -> float:
    """Calcula a distância euclidiana entre duas cidades (arredondada)"""
    dx = cidade1[0] - cidade2[0]
    dy = cidade1[1] - cidade2[1]
    return round(math.sqrt(dx * dx + dy * dy))

def calcular_custo_rota(rota: List[int], cidades: dict) -> float:
    """Calcula o custo total de uma rota (distância total percorrida)"""
    custo = 0
    for i in range(len(rota)):
        cidade_atual = cidades[rota[i]]
        cidade_proxima = cidades[rota[(i + 1) % len(rota)]]  
        custo += calcular_distancia(cidade_atual, cidade_proxima)
    return custo

def dijkstra(cidades: dict, origem: int, destino: int) -> Tuple[List[int], float]:
    """
    Algoritmo de Dijkstra - Encontra o caminho mais curto entre origem e destino
    
    Retorna: (caminho, distancia_total)
    """
    import heapq
    
    # Inicialização
    distancias = {cidade: float('inf') for cidade in cidades.keys()}
    distancias[origem] = 0
    predecessores = {cidade: None for cidade in cidades.keys()}
    
    # Fila de prioridade: (distancia, cidade)
    fila = [(0, origem)]
    visitados = set()
    
    while fila:
        dist_atual, cidade_atual = heapq.heappop(fila)
        
        if cidade_atual in visitados:
            continue
            
        visitados.add(cidade_atual)
        
        # Se chegou no destino, pode parar
        if cidade_atual == destino:
            break
        
        # Verifica todos os vizinhos (todas as outras cidades no grafo completo)
        for vizinho in cidades.keys():
            if vizinho not in visitados:
                # Calcula distância até o vizinho
                dist_vizinho = calcular_distancia(cidades[cidade_atual], cidades[vizinho])
                nova_distancia = dist_atual + dist_vizinho
                
                # Se encontrou caminho melhor, atualiza
                if nova_distancia < distancias[vizinho]:
                    distancias[vizinho] = nova_distancia
                    predecessores[vizinho] = cidade_atual
                    heapq.heappush(fila, (nova_distancia, vizinho))
    
    # Reconstrói o caminho
    caminho = []
    cidade = destino
    while cidade is not None:
        caminho.append(cidade)
        cidade = predecessores[cidade]
    
    caminho.reverse()
    
    return caminho, distancias[destino]

def bellman_ford(cidades: dict, origem: int) -> Tuple[Dict[int, float], Dict[int, int]]:
    """
    Algoritmo de Bellman-Ford - Encontra caminhos mais curtos de origem para todos os vértices
    Funciona mesmo com arestas de peso negativo (diferente do Dijkstra)
    
    Retorna: (distancias, predecessores)
    """
    # Inicialização
    distancias = {cidade: float('inf') for cidade in cidades.keys()}
    distancias[origem] = 0
    predecessores = {cidade: None for cidade in cidades.keys()}
    
    cidades_lista = list(cidades.keys())
    n = len(cidades_lista)
    
    # Relaxamento de arestas (n-1 vezes)
    for _ in range(n - 1):
        melhorou = False
        
        # Para cada aresta (u, v) no grafo completo
        for u in cidades_lista:
            for v in cidades_lista:
                if u != v:
                    peso = calcular_distancia(cidades[u], cidades[v])
                    
                    # Relaxamento
                    if distancias[u] != float('inf') and distancias[u] + peso < distancias[v]:
                        distancias[v] = distancias[u] + peso
                        predecessores[v] = u
                        melhorou = True
        
        # Se não houve melhoria, pode parar cedo
        if not melhorou:
            break
    
    # Verifica se há ciclos negativos
    for u in cidades_lista:
        for v in cidades_lista:
            if u != v:
                peso = calcular_distancia(cidades[u], cidades[v])
                if distancias[u] != float('inf') and distancias[u] + peso < distancias[v]:
                    raise ValueError("Grafo contém ciclo de peso negativo!")
    
    return distancias, predecessores

def reconstruir_caminho_bellman(predecessores: Dict[int, int], origem: int, destino: int) -> List[int]:
    """Reconstrói o caminho a partir dos predecessores do Bellman-Ford"""
    caminho = []
    atual = destino
    
    while atual is not None:
        caminho.append(atual)
        atual = predecessores[atual]
    
    caminho.reverse()
    
    # Verifica se há caminho válido
    if caminho[0] != origem:
        return []
    
    return caminho

def gerar_rota_inicial(cidades: dict) -> List[int]:
    """Gera uma rota inicial aleatória"""
    rota = list(cidades.keys())
    random.shuffle(rota)
    return rota

def gerar_rota_nearest_neighbor(cidades: dict) -> List[int]:
    """Gera rota inicial usando Nearest Neighbor (vizinho mais próximo)"""
    nao_visitadas = set(cidades.keys())
    atual = random.choice(list(nao_visitadas))
    rota = [atual]
    nao_visitadas.remove(atual)
    
    while nao_visitadas:
        mais_proxima = min(nao_visitadas, 
                          key=lambda c: calcular_distancia(cidades[atual], cidades[c]))
        rota.append(mais_proxima)
        atual = mais_proxima
        nao_visitadas.remove(atual)
    
    return rota

def gerar_rota_dijkstra_greedy(cidades: dict) -> List[int]:
    """
    Usa Dijkstra de forma gulosa para construir rota TSP.
    Em cada passo, usa Dijkstra para encontrar a cidade não visitada mais próxima.
    Nota: Isso é similar a Nearest Neighbor, mas demonstra o uso de Dijkstra.
    """
    nao_visitadas = set(cidades.keys())
    atual = random.choice(list(nao_visitadas))
    rota = [atual]
    nao_visitadas.remove(atual)
    
    while nao_visitadas:
        # Usa Dijkstra para encontrar distâncias de 'atual' para todas as cidades
        melhor_destino = None
        melhor_distancia = float('inf')
        
        for destino in nao_visitadas:
            caminho, distancia = dijkstra(cidades, atual, destino)
            if distancia < melhor_distancia:
                melhor_distancia = distancia
                melhor_destino = destino
        
        rota.append(melhor_destino)
        atual = melhor_destino
        nao_visitadas.remove(atual)
    
    return rota

def gerar_rota_bellman_ford_greedy(cidades: dict) -> List[int]:
    """
    Usa Bellman-Ford de forma gulosa para construir rota TSP.
    Em cada passo, usa Bellman-Ford para encontrar distâncias e escolhe a cidade não visitada mais próxima.
    """
    nao_visitadas = set(cidades.keys())
    atual = random.choice(list(nao_visitadas))
    rota = [atual]
    nao_visitadas.remove(atual)
    
    while nao_visitadas:
        # Usa Bellman-Ford para encontrar distâncias de 'atual' para todas as cidades
        distancias, predecessores = bellman_ford(cidades, atual)
        
        # Escolhe a cidade não visitada mais próxima
        melhor_destino = None
        melhor_distancia = float('inf')
        
        for destino in nao_visitadas:
            if distancias[destino] < melhor_distancia:
                melhor_distancia = distancias[destino]
                melhor_destino = destino
        
        rota.append(melhor_destino)
        atual = melhor_destino
        nao_visitadas.remove(atual)
    
    return rota

def two_opt(rota: List[int], i: int, k: int) -> List[int]:
    """Aplica a operação 2-opt: inverte o segmento entre i e k"""
    nova_rota = rota[:i] + rota[i:k+1][::-1] + rota[k+1:]
    return nova_rota

def three_opt_swap(rota: List[int], i: int, j: int, k: int) -> List[int]:
    """Aplica uma das recombinações possíveis do 3-opt"""
    # Existem 8 formas de reconectar 3 segmentos, aqui usamos algumas das melhores
    A, B, C, D = rota[:i], rota[i:j], rota[j:k], rota[k:]
    
    # Teste diferentes recombinações
    opcoes = [
        A + B[::-1] + C + D,      # inverte B
        A + B + C[::-1] + D,      # inverte C
        A + B[::-1] + C[::-1] + D, # inverte B e C
        A + C + B + D,             # troca B e C
        A + C[::-1] + B[::-1] + D, # troca e inverte
    ]
    
    return random.choice(opcoes)

def or_opt(rota: List[int], i: int, length: int, j: int) -> List[int]:
    """Or-opt: remove uma cadeia de tamanho 'length' da posição i e insere em j"""
    if i + length > len(rota) or i < 0 or j < 0 or j > len(rota):
        return rota
    
    # Remove a cadeia
    cadeia = rota[i:i+length]
    rota_temp = rota[:i] + rota[i+length:]
    
    # Insere na nova posição
    if j > i:
        j = j - length
    nova_rota = rota_temp[:j] + cadeia + rota_temp[j:]
    
    return nova_rota

def busca_local_2opt(rota: List[int], cidades: dict) -> Tuple[List[int], float]:
    """Busca local completa com 2-opt até não haver melhoria"""
    melhorou = True
    melhor_rota = rota[:]
    melhor_custo = calcular_custo_rota(melhor_rota, cidades)
    
    while melhorou:
        melhorou = False
        for i in range(len(rota) - 1):
            for k in range(i + 2, len(rota)):
                nova_rota = two_opt(melhor_rota, i, k)
                novo_custo = calcular_custo_rota(nova_rota, cidades)
                
                if novo_custo < melhor_custo:
                    melhor_rota = nova_rota
                    melhor_custo = novo_custo
                    melhorou = True
                    break
            if melhorou:
                break
    
    return melhor_rota, melhor_custo

def busca_local_completa(rota: List[int], cidades: dict) -> Tuple[List[int], float]:
    """Busca local usando 2-opt, 3-opt e Or-opt"""
    melhorou = True
    melhor_rota = rota[:]
    melhor_custo = calcular_custo_rota(melhor_rota, cidades)
    n = len(rota)
    
    iteracoes = 0
    max_iter = 200
    
    while melhorou and iteracoes < max_iter:
        melhorou = False
        iteracoes += 1
        
        # 2-opt completo
        for i in range(n - 1):
            for k in range(i + 2, n):
                nova_rota = two_opt(melhor_rota, i, k)
                novo_custo = calcular_custo_rota(nova_rota, cidades)
                
                if novo_custo < melhor_custo:
                    melhor_rota = nova_rota
                    melhor_custo = novo_custo
                    melhorou = True
                    break
            if melhorou:
                break
        
        if not melhorou:
            # Or-opt com cadeias de tamanho 1, 2, 3
            for length in [1, 2, 3]:
                for i in range(n - length):
                    for j in range(n):
                        if j < i or j > i + length:
                            nova_rota = or_opt(melhor_rota, i, length, j)
                            novo_custo = calcular_custo_rota(nova_rota, cidades)
                            
                            if novo_custo < melhor_custo:
                                melhor_rota = nova_rota
                                melhor_custo = novo_custo
                                melhorou = True
                                break
                    if melhorou:
                        break
                if melhorou:
                    break
        
        # 3-opt se ainda não melhorou
        if not melhorou and n >= 6:
            for i in range(n - 5):
                for j in range(i + 2, min(n - 3, i + 8)):
                    for k in range(j + 2, min(n - 1, j + 8)):
                        nova_rota = three_opt_swap(melhor_rota, i, j, k)
                        novo_custo = calcular_custo_rota(nova_rota, cidades)
                        
                        if novo_custo < melhor_custo:
                            melhor_rota = nova_rota
                            melhor_custo = novo_custo
                            melhorou = True
                            break
                    if melhorou:
                        break
                if melhorou:
                    break
    
    return melhor_rota, melhor_custo

def perturbar_rota(rota: List[int], intensidade: int = 4) -> List[int]:
    """Perturba a rota aplicando múltiplas trocas aleatórias"""
    nova_rota = rota[:]
    n = len(rota)
    
    for _ in range(intensidade):
        i, j = random.randint(0, n-1), random.randint(0, n-1)
        nova_rota[i], nova_rota[j] = nova_rota[j], nova_rota[i]
    
    return nova_rota

def iterated_local_search(rota_inicial: List[int], cidades: dict, max_iter: int = 50) -> Tuple[List[int], float]:
    """Iterated Local Search (ILS) - Busca local iterada com perturbações"""
    melhor_rota = rota_inicial[:]
    melhor_custo = calcular_custo_rota(melhor_rota, cidades)
    
    # Busca local inicial
    melhor_rota, melhor_custo = busca_local_completa(melhor_rota, cidades)
    
    rota_atual = melhor_rota[:]
    custo_atual = melhor_custo
    
    sem_melhoria = 0
    
    for i in range(max_iter):
        # Perturba a solução
        intensidade = 3 + (sem_melhoria // 10)  # Aumenta perturbação se estagnado
        rota_perturbada = perturbar_rota(rota_atual, intensidade)
        
        # Aplica busca local
        rota_nova, custo_novo = busca_local_completa(rota_perturbada, cidades)
        
        # Critério de aceitação (aceita se melhor ou ocasionalmente pior)
        if custo_novo < custo_atual or (sem_melhoria > 20 and random.random() < 0.1):
            rota_atual = rota_nova
            custo_atual = custo_novo
            sem_melhoria = 0
            
            if custo_novo < melhor_custo:
                melhor_rota = rota_nova
                melhor_custo = custo_novo
        else:
            sem_melhoria += 1
    
    return melhor_rota, melhor_custo

def simulated_annealing_advanced(rota_inicial, cidades, temp_inicial=100000, temp_final=0.0001, alpha=0.9998):
    """Simulated Annealing avançado com múltiplos operadores"""
    rota_atual = rota_inicial[:]
    custo_atual = calcular_custo_rota(rota_atual, cidades)
    
    melhor_rota = rota_atual[:]
    melhor_custo = custo_atual
    
    temperatura = temp_inicial
    n = len(rota_atual)
    
    iteracoes = 0
    
    while temperatura > temp_final and iteracoes < 500000:
        iteracoes += 1
        
        # Escolhe operador aleatoriamente
        operador = random.random()
        
        if operador < 0.7:  # 70% 2-opt
            i = random.randint(1, n - 2)
            k = random.randint(i + 1, n - 1)
            nova_rota = two_opt(rota_atual, i, k)
            
        elif operador < 0.85:  # 15% Or-opt
            i = random.randint(0, n - 3)
            length = random.randint(1, min(3, n - i))
            j = random.randint(0, n - 1)
            nova_rota = or_opt(rota_atual, i, length, j)
            
        else:  # 15% 3-opt
            pontos = sorted(random.sample(range(1, n), 3))
            i, j, k = pontos[0], pontos[1], pontos[2]
            nova_rota = three_opt_swap(rota_atual, i, j, k)
        
        novo_custo = calcular_custo_rota(nova_rota, cidades)
        delta = novo_custo - custo_atual
        
        if delta < 0 or random.random() < math.exp(-delta / temperatura):
            rota_atual = nova_rota
            custo_atual = novo_custo
            
            if custo_atual < melhor_custo:
                melhor_rota = rota_atual[:]
                melhor_custo = custo_atual
        
        temperatura *= alpha
    
    return melhor_rota, melhor_custo

def held_karp_tsp(cidades: dict) -> Tuple[List[int], float]:
    """
    Algoritmo de Held-Karp (programação dinâmica) - SOLUÇÃO ÓTIMA EXATA
    Complexidade: O(n² * 2^n) - funciona bem para até ~20 cidades
    """
    n = len(cidades)
    cidades_lista = list(cidades.keys())
    
    # Matriz de distâncias
    dist = {}
    for c1 in cidades_lista:
        for c2 in cidades_lista:
            if c1 != c2:
                dist[(c1, c2)] = calcular_distancia(cidades[c1], cidades[c2])
    
    # DP: memo[conjunto_visitado][ultima_cidade] = (custo_minimo, caminho)
    memo = {}
    
    # Cidade inicial (usamos a primeira da lista)
    inicio = cidades_lista[0]
    
    # Base: partindo do início para cada cidade
    for cidade in cidades_lista[1:]:
        conjunto = frozenset([inicio, cidade])
        memo[(conjunto, cidade)] = (dist[(inicio, cidade)], [inicio, cidade])
    
    # Preenche a DP para subconjuntos crescentes
    for tamanho in range(3, n + 1):
        for subset in combinations(cidades_lista[1:], tamanho - 1):
            conjunto = frozenset([inicio] + list(subset))
            
            for ultima in subset:
                # Calcula o custo mínimo para chegar em 'ultima'
                conjunto_anterior = conjunto - {ultima}
                melhor_custo = float('inf')
                melhor_caminho = []
                
                for penultima in conjunto_anterior - {inicio}:
                    if (conjunto_anterior, penultima) in memo:
                        custo_anterior, caminho_anterior = memo[(conjunto_anterior, penultima)]
                        custo_total = custo_anterior + dist[(penultima, ultima)]
                        
                        if custo_total < melhor_custo:
                            melhor_custo = custo_total
                            melhor_caminho = caminho_anterior + [ultima]
                
                if melhor_caminho:
                    memo[(conjunto, ultima)] = (melhor_custo, melhor_caminho)
    
    # Encontra o melhor caminho completo (voltando ao início)
    conjunto_completo = frozenset(cidades_lista)
    melhor_custo_final = float('inf')
    melhor_rota_final = []
    
    for ultima in cidades_lista[1:]:
        if (conjunto_completo, ultima) in memo:
            custo, caminho = memo[(conjunto_completo, ultima)]
            custo_total = custo + dist[(ultima, inicio)]
            
            if custo_total < melhor_custo_final:
                melhor_custo_final = custo_total
                melhor_rota_final = caminho
    
    return melhor_rota_final, melhor_custo_final

def main():
    tempo_inicio = time.time()        
    
    print("=" * 60)
    print("PCV - BUSCA LOCAL EUCLIDIANA")
    print("=" * 60)

    #calibração
    arquivo_cidades = f"aula/teste01.txt"

    cidades = ler_cidades_txt(arquivo_cidades)
    print(f"Cidades: {len(cidades)}")
    
    melhor_rota_global = None
    melhor_custo_global = float('inf')
    
    # FASE 1: Múltiplas inicializações com Nearest Neighbor + 2-opt completo
    print("\n[NN + 2-opt]", end=" ")
    for i in range(50):
        rota = gerar_rota_nearest_neighbor(cidades)
        rota, custo = busca_local_2opt(rota, cidades)
        
        if custo < melhor_custo_global:
            melhor_rota_global = rota
            melhor_custo_global = custo
            print(f"\n  Nova melhor: {round(melhor_custo_global)} - Rota: {melhor_rota_global}")
    print(f"Melhor: {melhor_custo_global:.0f}")
    
    # FASE 2: Busca Local Completa (2-opt + Or-opt + 3-opt)
    print("[Busca Local Completa]", end=" ")
    for i in range(20):
        rota = gerar_rota_nearest_neighbor(cidades)
        rota, custo = busca_local_completa(rota, cidades)
        
        if custo < melhor_custo_global:
            melhor_rota_global = rota
            melhor_custo_global = custo
            print(f"\n  Nova melhor: {round(melhor_custo_global)} - Rota: {melhor_rota_global}")
    print(f"Melhor: {melhor_custo_global:.0f}")
    
    # FASE 3: Inicializações aleatórias + Busca Local Completa
    print("[Aleatório + Busca Local]", end=" ")
    for i in range(20):
        rota = gerar_rota_inicial(cidades)
        rota, custo = busca_local_completa(rota, cidades)
        
        if custo < melhor_custo_global:
            melhor_rota_global = rota
            melhor_custo_global = custo
            print(f"\n  Nova melhor: {round(melhor_custo_global)} - Rota: {melhor_rota_global}")
    print(f"Melhor: {melhor_custo_global:.0f}")
    
    # FASE 4: Iterated Local Search (Busca Local Iterada)
    print("[ILS - DESATIVADO]")
    
    # FASE 5: Simulated Annealing (Recozimento Simulado)
    print("[SA - DESATIVADO]")
    
    # FASE FINAL: Refinamento intensivo com busca local completa
    print("[Refinamento Final]", end=" ")
    melhor_rota_global, melhor_custo_global = busca_local_completa(melhor_rota_global, cidades)
    print(f"Final: {melhor_custo_global:.0f}")
    
    tempo_fim = time.time()
    tempo_execucao = tempo_fim - tempo_inicio
    
    print("\n" + "=" * 60)
    print(f"RESULTADO FINAL: {round(melhor_custo_global)} | Tempo: {tempo_execucao:.2f}s")    
    print(f"Rota: {melhor_rota_global}")
    print("=" * 60)
        
if __name__ == "__main__":
    random.seed(42)
    main()
