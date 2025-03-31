import numpy as np
import time
from typing import Tuple, List, Dict
from config import (
    X_MIN, X_MAX, Y_MIN, Y_MAX, POPULATION_SIZES, CROSSOVER_RATES,
    MAX_GENERATIONS, STAGNATION_GENERATIONS, ELITE_PERCENTAGE
)
from fitness import (
    calculate_population_fitness, calculate_diversity,
    calculate_population_accuracy, get_best_solution
)
from selection import tournament_selection, roulette_selection
from crossover import create_offspring
from mutation import mutate_population, calculate_mutation_rate

class GeneticAlgorithm:
    def __init__(
        self,
        population_size: int,
        crossover_rate: float,
        selection_method: str = 'tournament',
        crossover_method: str = 'arithmetic'
    ):
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.selection_method = selection_method
        self.crossover_method = crossover_method
        self.population = None
        self.fitness = None
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.best_accuracy_history = []
        self.generation = 0
        self.stagnation_counter = 0
        self.best_fitness = float('-inf')
        self.best_solution = None
        self.start_time = None
        self.end_time = None
        self.function_evaluations = 0

    def initialize_population(self):
        """Инициализация начальной популяции"""
        self.population = np.random.uniform(
            low=[X_MIN, Y_MIN],
            high=[X_MAX, Y_MAX],
            size=(self.population_size, 2)
        )
        self.fitness = calculate_population_fitness(self.population)
        self.function_evaluations += self.population_size
        self.update_history()

    def update_history(self):
        """Обновление истории лучших и средних значений"""
        self.best_fitness_history.append(np.max(self.fitness))
        self.avg_fitness_history.append(np.mean(self.fitness))
        self.best_accuracy_history.append(calculate_population_accuracy(self.population))

    def select_parents(self) -> np.ndarray:
        """Выбор родителей с использованием выбранного метода селекции"""
        num_parents = int(self.population_size * (1 - ELITE_PERCENTAGE))
        if self.selection_method == 'tournament':
            return tournament_selection(self.population, self.fitness, num_parents)
        else:
            return roulette_selection(self.population, self.fitness, num_parents)

    def create_next_generation(self):
        """Создание следующего поколения"""
        # Сохранение элитных особей
        elite_size = int(self.population_size * ELITE_PERCENTAGE)
        elite_indices = np.argsort(self.fitness)[-elite_size:]
        elite_population = self.population[elite_indices].copy()
        elite_fitness = self.fitness[elite_indices].copy()

        # Выбор родителей и создание потомков
        parents = self.select_parents()
        offspring = create_offspring(parents, self.crossover_method)
        
        # Мутация потомков
        mutation_rate = calculate_mutation_rate(self.generation, MAX_GENERATIONS)
        offspring = mutate_population(offspring, mutation_rate)
        
        # Оценка приспособленности потомков
        offspring_fitness = calculate_population_fitness(offspring)
        self.function_evaluations += len(offspring)

        # Объединение элитных особей и потомков
        self.population = np.vstack([elite_population, offspring])
        self.fitness = np.concatenate([elite_fitness, offspring_fitness])

    def check_stopping_criteria(self) -> bool:
        """Проверка критериев остановки"""
        current_best_fitness = np.max(self.fitness)
        
        # Обновление лучшего решения
        if current_best_fitness > self.best_fitness:
            self.best_fitness = current_best_fitness
            self.best_solution = self.population[np.argmax(self.fitness)]
            self.stagnation_counter = 0
        else:
            self.stagnation_counter += 1

        # Проверка критериев остановки
        if self.generation >= MAX_GENERATIONS:
            return True
        if self.stagnation_counter >= STAGNATION_GENERATIONS:
            return True
        return False

    def run(self) -> Dict:
        """Запуск генетического алгоритма"""
        self.start_time = time.time()
        self.initialize_population()

        while not self.check_stopping_criteria():
            self.create_next_generation()
            self.update_history()
            self.generation += 1

        self.end_time = time.time()
        
        # Получение финального лучшего решения
        final_best_point, final_best_fitness, final_best_accuracy = get_best_solution(
            self.population, self.fitness
        )

        return {
            'best_solution': final_best_point,
            'best_fitness': final_best_fitness,
            'best_accuracy': final_best_accuracy,
            'generations': self.generation,
            'time': self.end_time - self.start_time,
            'function_evaluations': self.function_evaluations,
            'fitness_history': {
                'best': self.best_fitness_history,
                'average': self.avg_fitness_history,
                'accuracy': self.best_accuracy_history
            }
        }

def run_experiments() -> List[Dict]:
    """Проведение экспериментов с разными параметрами"""
    results = []
    
    for pop_size in POPULATION_SIZES:
        for crossover_rate in CROSSOVER_RATES:
            for selection_method in ['tournament', 'roulette']:
                for crossover_method in ['arithmetic', 'blx_alpha']:
                    print(f"\nЗапуск эксперимента:")
                    print(f"Размер популяции: {pop_size}")
                    print(f"Вероятность кроссовера: {crossover_rate}")
                    print(f"Метод селекции: {selection_method}")
                    print(f"Метод кроссовера: {crossover_method}")
                    
                    ga = GeneticAlgorithm(
                        population_size=pop_size,
                        crossover_rate=crossover_rate,
                        selection_method=selection_method,
                        crossover_method=crossover_method
                    )
                    
                    result = ga.run()
                    results.append({
                        'parameters': {
                            'population_size': pop_size,
                            'crossover_rate': crossover_rate,
                            'selection_method': selection_method,
                            'crossover_method': crossover_method
                        },
                        'results': result
                    })
                    
                    print(f"Лучшее решение: {result['best_solution']}")
                    print(f"Значение функции: {result['best_fitness']}")
                    print(f"Точность: {result['best_accuracy']}")
                    print(f"Время выполнения: {result['time']:.2f} сек")
                    print(f"Количество вычислений функции: {result['function_evaluations']}")
    
    return results 