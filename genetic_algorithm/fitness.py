import numpy as np
from config import X_MIN, X_MAX, Y_MIN, Y_MAX, GLOBAL_MAXIMA

def objective_function(x: float, y: float) -> float:
    """
    Целевая функция для оптимизации
    f(x, y) = - (x² + y - 11)² - (x + y² - 7)²
    """
    return -(x**2 + y - 11)**2 - (x + y**2 - 7)**2

def calculate_fitness(x: float, y: float) -> float:
    """
    Вычисление значения приспособленности для точки (x, y)
    """
    # Проверка границ
    if x < X_MIN or x > X_MAX or y < Y_MIN or y > Y_MAX:
        # Если точка выходит за границы, возвращаем штрафованное значение
        return objective_function(x, y) * 0.9  # Штраф 10%
    
    return objective_function(x, y)

def calculate_population_fitness(population: np.ndarray) -> np.ndarray:
    """
    Вычисление значений приспособленности для всей популяции
    """
    return np.array([calculate_fitness(x, y) for x, y in population])

def calculate_diversity(population: np.ndarray) -> float:
    """
    Вычисление разнообразия популяции как среднее расстояние между особями
    """
    n = len(population)
    if n < 2:
        return 0.0
    
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((population[i] - population[j])**2))
            distances.append(dist)
    
    return np.mean(distances)

def find_nearest_global_maximum(x: float, y: float) -> tuple[float, float]:
    """
    Поиск ближайшего глобального максимума к точке (x, y)
    """
    min_dist = float('inf')
    nearest_max = None
    
    for max_x, max_y in GLOBAL_MAXIMA:
        dist = np.sqrt((x - max_x)**2 + (y - max_y)**2)
        if dist < min_dist:
            min_dist = dist
            nearest_max = (max_x, max_y)
    
    return nearest_max

def calculate_solution_accuracy(x: float, y: float) -> float:
    """
    Вычисление точности решения (расстояние до ближайшего глобального максимума)
    """
    nearest_max = find_nearest_global_maximum(x, y)
    return np.sqrt((x - nearest_max[0])**2 + (y - nearest_max[1])**2)

def is_solution_acceptable(x: float, y: float, tolerance: float = 0.01) -> bool:
    """
    Проверка, является ли решение приемлемым (находится ли в пределах допустимой погрешности)
    """
    return calculate_solution_accuracy(x, y) <= tolerance

def calculate_population_accuracy(population: np.ndarray) -> float:
    """
    Вычисление средней точности решения для всей популяции
    """
    accuracies = [calculate_solution_accuracy(x, y) for x, y in population]
    return np.mean(accuracies)

def get_best_solution(population: np.ndarray, fitness: np.ndarray) -> tuple[np.ndarray, float, float]:
    """
    Получение лучшего решения из популяции
    Возвращает: (лучшая точка, значение функции, точность решения)
    """
    best_idx = np.argmax(fitness)
    best_point = population[best_idx]
    best_fitness = fitness[best_idx]
    best_accuracy = calculate_solution_accuracy(best_point[0], best_point[1])
    
    return best_point, best_fitness, best_accuracy 