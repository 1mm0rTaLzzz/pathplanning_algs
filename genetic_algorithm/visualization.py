import numpy as np
import matplotlib.pyplot as plt
from config import X_MIN, X_MAX, Y_MIN, Y_MAX, PLOT_POINTS, CONTOUR_LEVELS, GLOBAL_MAXIMA
from fitness import objective_function

def plot_contour_function():
    """Построение контурного графика функции"""
    x = np.linspace(X_MIN, X_MAX, PLOT_POINTS)
    y = np.linspace(Y_MIN, Y_MAX, PLOT_POINTS)
    X, Y = np.meshgrid(x, y)
    
    # Вычисление значений функции
    Z = np.zeros_like(X)
    for i in range(PLOT_POINTS):
        for j in range(PLOT_POINTS):
            Z[i, j] = objective_function(X[i, j], Y[i, j])
    
    # Построение контурного графика
    plt.figure(figsize=(10, 8))
    plt.contour(X, Y, Z, levels=CONTOUR_LEVELS, cmap='viridis')
    plt.colorbar(label='f(x, y)')
    
    # Отображение глобальных максимумов
    for max_x, max_y in GLOBAL_MAXIMA:
        plt.plot(max_x, max_y, 'r*', markersize=15, label='Глобальные максимумы')
    
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Контурный график функции f(x, y)')
    plt.grid(True)
    plt.legend()
    return plt.gcf()

def plot_population(population: np.ndarray, title: str = "Популяция"):
    """Отображение популяции на контурном графике"""
    fig = plot_contour_function()
    plt.scatter(population[:, 0], population[:, 1], c='red', alpha=0.5, label='Особи')
    plt.title(title)
    plt.legend()
    return fig

def plot_fitness_history(fitness_history: dict, title: str = "История значений приспособленности"):
    """Построение графика изменения значений приспособленности"""
    plt.figure(figsize=(10, 6))
    generations = range(len(fitness_history['best']))
    
    plt.plot(generations, fitness_history['best'], 'b-', label='Лучшее значение')
    plt.plot(generations, fitness_history['average'], 'g-', label='Среднее значение')
    
    plt.xlabel('Поколение')
    plt.ylabel('Значение приспособленности')
    plt.title(title)
    plt.grid(True)
    plt.legend()
    return plt.gcf()

def plot_accuracy_history(accuracy_history: list, title: str = "История точности решения"):
    """Построение графика изменения точности решения"""
    plt.figure(figsize=(10, 6))
    generations = range(len(accuracy_history))
    
    plt.plot(generations, accuracy_history, 'r-')
    
    plt.xlabel('Поколение')
    plt.ylabel('Точность решения')
    plt.title(title)
    plt.grid(True)
    return plt.gcf()

def plot_experiment_results(results: list):
    """Визуализация результатов экспериментов"""
    # Создание подграфиков
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Результаты экспериментов', fontsize=16)
    
    # График времени выполнения
    times = [r['results']['time'] for r in results]
    labels = [f"Pop={r['parameters']['population_size']}, "
             f"Cr={r['parameters']['crossover_rate']}, "
             f"Sel={r['parameters']['selection_method']}, "
             f"Cross={r['parameters']['crossover_method']}" for r in results]
    
    axes[0, 0].bar(range(len(times)), times)
    axes[0, 0].set_title('Время выполнения')
    axes[0, 0].set_xticks(range(len(labels)))
    axes[0, 0].set_xticklabels(labels, rotation=45, ha='right')
    
    # График точности решения
    accuracies = [r['results']['best_accuracy'] for r in results]
    axes[0, 1].bar(range(len(accuracies)), accuracies)
    axes[0, 1].set_title('Точность решения')
    axes[0, 1].set_xticks(range(len(labels)))
    axes[0, 1].set_xticklabels(labels, rotation=45, ha='right')
    
    # График количества вычислений функции
    evaluations = [r['results']['function_evaluations'] for r in results]
    axes[1, 0].bar(range(len(evaluations)), evaluations)
    axes[1, 0].set_title('Количество вычислений функции')
    axes[1, 0].set_xticks(range(len(labels)))
    axes[1, 0].set_xticklabels(labels, rotation=45, ha='right')
    
    # График лучшего значения функции
    best_fitness = [r['results']['best_fitness'] for r in results]
    axes[1, 1].bar(range(len(best_fitness)), best_fitness)
    axes[1, 1].set_title('Лучшее значение функции')
    axes[1, 1].set_xticks(range(len(labels)))
    axes[1, 1].set_xticklabels(labels, rotation=45, ha='right')
    
    plt.tight_layout()
    return fig

def save_experiment_plots(results: list, output_dir: str = "results"):
    """Сохранение всех графиков эксперимента"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохранение графика контурной функции
    fig = plot_contour_function()
    fig.savefig(os.path.join(output_dir, 'contour_function.png'))
    
    # Сохранение графика результатов экспериментов
    fig = plot_experiment_results(results)
    fig.savefig(os.path.join(output_dir, 'experiment_results.png'))
    
    # Сохранение графиков для каждого эксперимента
    for i, result in enumerate(results):
        # График истории приспособленности
        fig = plot_fitness_history(result['results']['fitness_history'])
        fig.savefig(os.path.join(output_dir, f'fitness_history_{i}.png'))
        
        # График истории точности
        fig = plot_accuracy_history(result['results']['fitness_history']['accuracy'])
        fig.savefig(os.path.join(output_dir, f'accuracy_history_{i}.png')) 