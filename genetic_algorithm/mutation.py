import numpy as np
from config import (
    MUTATION_SIGMA, MUTATION_MEAN, X_MIN, X_MAX, Y_MIN, Y_MAX,
    DIVERSITY_THRESHOLD, MAX_MUTATION_SIGMA
)

def gaussian_mutation(x: float, y: float, sigma: float = MUTATION_SIGMA) -> tuple[float, float]:
    """
    Гауссова мутация
    """
    # Генерация случайных отклонений с нормальным распределением
    dx = np.random.normal(MUTATION_MEAN, sigma)
    dy = np.random.normal(MUTATION_MEAN, sigma)
    
    # Применение мутации
    new_x = x + dx
    new_y = y + dy
    
    # Ограничение значений в допустимом диапазоне
    new_x = np.clip(new_x, X_MIN, X_MAX)
    new_y = np.clip(new_y, Y_MIN, Y_MAX)
    
    return new_x, new_y

def adaptive_mutation(population: np.ndarray, diversity: float) -> float:
    """
    Адаптивная мутация: корректировка σ в зависимости от разнообразия популяции
    """
    if diversity < DIVERSITY_THRESHOLD:
        # Увеличение σ при низком разнообразии
        return min(MUTATION_SIGMA * 2, MAX_MUTATION_SIGMA)
    return MUTATION_SIGMA

def mutate_population(
    population: np.ndarray,
    mutation_rate: float,
    diversity: float = None
) -> np.ndarray:
    """
    Мутация популяции с адаптивным σ
    """
    n = len(population)
    mutated_population = population.copy()
    
    # Определение σ для текущего поколения
    current_sigma = adaptive_mutation(population, diversity) if diversity is not None else MUTATION_SIGMA
    
    # Применение мутации к каждой особи с вероятностью mutation_rate
    for i in range(n):
        if np.random.random() < mutation_rate:
            mutated_population[i] = gaussian_mutation(
                population[i][0],
                population[i][1],
                current_sigma
            )
    
    return mutated_population

def calculate_mutation_rate(generation: int, max_generations: int) -> float:
    """
    Линейное уменьшение вероятности мутации от начального до конечного значения
    """
    from config import INITIAL_MUTATION_RATE, FINAL_MUTATION_RATE
    
    return INITIAL_MUTATION_RATE - (INITIAL_MUTATION_RATE - FINAL_MUTATION_RATE) * (generation / max_generations) 