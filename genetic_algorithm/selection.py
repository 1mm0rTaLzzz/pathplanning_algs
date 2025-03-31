import numpy as np
from config import TOURNAMENT_SIZE

def tournament_selection(population: np.ndarray, fitness: np.ndarray, num_parents: int) -> np.ndarray:
    """
    Турнирная селекция
    """
    n = len(population)
    parents = np.zeros((num_parents, 2))
    
    for i in range(num_parents):
        # Выбор случайных индексов для турнира
        tournament_idx = np.random.choice(n, TOURNAMENT_SIZE, replace=False)
        tournament_fitness = fitness[tournament_idx]
        
        # Выбор победителя турнира (индекс лучшей особи)
        winner_idx = tournament_idx[np.argmax(tournament_fitness)]
        parents[i] = population[winner_idx]
    
    return parents

def roulette_selection(population: np.ndarray, fitness: np.ndarray, num_parents: int) -> np.ndarray:
    """
    Селекция методом рулетки
    """
    # Преобразование fitness в вероятности
    # Добавляем небольшое положительное число для избежания деления на ноль
    probabilities = (fitness - np.min(fitness) + 1e-10) / (np.sum(fitness - np.min(fitness) + 1e-10))
    
    # Выбор родителей с учетом вероятностей
    parent_indices = np.random.choice(len(population), num_parents, p=probabilities)
    return population[parent_indices] 