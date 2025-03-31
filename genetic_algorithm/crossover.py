import numpy as np
from config import ALPHA_MIN, ALPHA_MAX, BLX_ALPHA

def arithmetic_crossover(parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
    """
    Арифметический кроссовер
    child = α * parent1 + (1-α) * parent2, где α ∈ [0.2, 0.8]
    """
    alpha = np.random.uniform(ALPHA_MIN, ALPHA_MAX)
    return alpha * parent1 + (1 - alpha) * parent2

def blx_alpha_crossover(parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
    """
    BLX-α кроссовер
    child = [min(p1, p2) - αΔ, max(p1, p2) + αΔ], где Δ = |p1 - p2|
    """
    min_coords = np.minimum(parent1, parent2)
    max_coords = np.maximum(parent1, parent2)
    delta = max_coords - min_coords
    
    # Генерация случайного значения в расширенном диапазоне
    child = np.random.uniform(
        min_coords - BLX_ALPHA * delta,
        max_coords + BLX_ALPHA * delta
    )
    
    return child

def create_offspring(parents: np.ndarray, crossover_method: str) -> np.ndarray:
    """
    Создание потомков с использованием выбранного метода кроссовера
    """
    n = len(parents)
    offspring = np.zeros((n, 2))
    
    for i in range(0, n, 2):
        if i + 1 < n:
            if crossover_method == 'arithmetic':
                offspring[i] = arithmetic_crossover(parents[i], parents[i+1])
                offspring[i+1] = arithmetic_crossover(parents[i+1], parents[i])
            else:  # blx_alpha
                offspring[i] = blx_alpha_crossover(parents[i], parents[i+1])
                offspring[i+1] = blx_alpha_crossover(parents[i+1], parents[i])
    
    return offspring 