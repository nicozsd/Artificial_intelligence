from typing import List, Tuple
import random
import math
import time

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
                    cidades[int(partes[0])] = (float(partes[1]), float(partes[2]))
    
    return cidades

def calcular_distancia(cidade1: Tuple[float, float], cidade2: Tuple[float, float]) -> float:
    """Calcula a distância euclidiana entre duas cidades"""
    dx = cidade1[0] - cidade2[0]
    dy = cidade1[1] - cidade2[1]
    return math.sqrt(dx * dx + dy * dy)

def calcular_custo_rota(rota: List[int], cidades: dict) -> float:
    """Calcula o custo total de uma rota (distância total percorrida)"""
    custo = 0
    for i in range(len(rota)):
        cidade_atual = cidades[rota[i]]
        cidade_proxima = cidades[rota[(i + 1) % len(rota)]]  
        custo += calcular_distancia(cidade_atual, cidade_proxima)
    return custo

def gerar_rota_inicial(cidades: dict) -> List[int]:
    """Gera uma rota inicial aleatória"""
    rota = list(cidades.keys())
    random.shuffle(rota)
    return rota

def two_opt(rota: List[int], i: int, k: int) -> List[int]:
    """Aplica a operação 2-opt: inverte o segmento entre i e k"""
    nova_rota = rota[:i] + rota[i:k+1][::-1] + rota[k+1:]
    return nova_rota

def simulated_annealing_2opt(rota_inicial, cidades, temp_inicial=10000, temp_final=0.1, alpha=0.995):
    """Simulated Annealing híbrido com 2-opt"""
    rota_atual = rota_inicial[:]
    custo_atual = calcular_custo_rota(rota_atual, cidades)
    
    melhor_rota = rota_atual[:]
    melhor_custo = custo_atual
    
    temperatura = temp_inicial
    n = len(rota_atual)
    
    while temperatura > temp_final:
        i = random.randint(1, n - 2)
        k = random.randint(i + 1, n - 1)
        
        nova_rota = rota_atual[:i] + rota_atual[i:k+1][::-1] + rota_atual[k+1:]
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

def main():
    tempo_inicio = time.time()
    
    arquivo_cidades = "aula/cidades.txt"
    
    print("=" * 60)
    print("PCV - BUSCA LOCAL (2-OPT)")
    print("=" * 60)
    
    cidades = ler_cidades_txt(arquivo_cidades)
    print(f"\nCidades: {len(cidades)}")
    
    num_tentativas = 10
    melhor_rota = None
    melhor_custo = float('inf')
    
    print(f"Executando {num_tentativas} tentativas...\n")
    
    for i in range(num_tentativas):
        rota_inicial = gerar_rota_inicial(cidades)
        rota_final, custo_final = simulated_annealing_2opt(rota_inicial, cidades)
        
        print(f"Tentativa {i+1}: {custo_final:.2f}")
        
        if custo_final < melhor_custo:
            melhor_rota = rota_final
            melhor_custo = custo_final
    
    tempo_fim = time.time()
    tempo_execucao = tempo_fim - tempo_inicio
    
    print("\n" + "=" * 60)
    print("MELHOR ROTA ENCONTRADA")
    print("=" * 60)
    print(f"Distância total: {melhor_custo:.2f}")
    print(f"Tempo de execução: {tempo_execucao:.4f} segundos")
    print("\nRota completa:")
    rota_completa = ' -> '.join(map(str, melhor_rota)) + f' -> {melhor_rota[0]}'
    print(rota_completa)
    print("=" * 60)

if __name__ == "__main__":
    random.seed(42)
    main()
