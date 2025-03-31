from genetic_algo import run_experiments
from visualization import save_experiment_plots
import time

def main():
    print("Запуск генетического алгоритма для поиска глобальных экстремумов функции")
    print("f(x, y) = - (x² + y - 11)² - (x + y² - 7)²")
    print("\nПараметры алгоритма:")
    print("- Размеры популяции: 50, 100, 200")
    print("- Вероятности кроссовера: 0.7, 0.9")
    print("- Методы селекции: турнирная, рулетка")
    print("- Методы кроссовера: арифметический, BLX-α")
    print("- Адаптивная мутация: да")
    print("- Обработка границ: да")
    print("- Многопроцессорная оценка: нет")
    
    start_time = time.time()
    results = run_experiments()
    end_time = time.time()
    
    print(f"\nОбщее время выполнения всех экспериментов: {end_time - start_time:.2f} сек")
    
    # Сохранение результатов и графиков
    save_experiment_plots(results)
    print("\nРезультаты и графики сохранены в директории 'results'")
    
    # Анализ результатов
    print("\nАнализ результатов:")
    best_result = max(results, key=lambda x: x['results']['best_fitness'])
    print(f"\nЛучший результат:")
    print(f"Параметры:")
    print(f"- Размер популяции: {best_result['parameters']['population_size']}")
    print(f"- Вероятность кроссовера: {best_result['parameters']['crossover_rate']}")
    print(f"- Метод селекции: {best_result['parameters']['selection_method']}")
    print(f"- Метод кроссовера: {best_result['parameters']['crossover_method']}")
    print(f"\nРезультаты:")
    print(f"- Лучшее решение: {best_result['results']['best_solution']}")
    print(f"- Значение функции: {best_result['results']['best_fitness']}")
    print(f"- Точность решения: {best_result['results']['best_accuracy']}")
    print(f"- Время выполнения: {best_result['results']['time']:.2f} сек")
    print(f"- Количество вычислений функции: {best_result['results']['function_evaluations']}")

if __name__ == "__main__":
    main() 