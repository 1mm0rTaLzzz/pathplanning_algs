import math
from typing import Tuple, Union
import numpy as np
import matplotlib.pyplot as plt

# Константы
L1 = 1.0  # Длина первого сегмента
L2 = 0.5  # Длина второго сегмента

def inverse_kinematics(x: float, y: float, output_degrees: bool = False) -> Tuple[float, float]:
    """
    Вычисляет углы суставов для достижения заданной точки (x, y).
    
    Args:
        x (float): X-координата целевой точки
        y (float): Y-координата целевой точки
        output_degrees (bool): Если True, возвращает углы в градусах
        
    Returns:
        Tuple[float, float]: Углы суставов (theta1, theta2)
        
    Raises:
        ValueError: Если точка недостижима или введены некорректные значения
    """
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ValueError("Координаты должны быть числовыми значениями")
    
    # Вычисление расстояния до цели
    D = math.sqrt(x**2 + y**2)
    
    # Проверка на достижимость
    if D > (L1 + L2):
        raise ValueError(f"Точка ({x}, {y}) находится за пределами максимальной досягаемости")
    if D < abs(L1 - L2):
        raise ValueError(f"Точка ({x}, {y}) находится ближе, чем минимальная досягаемость")
    
    # Вычисление углов суставов
    try:
        # Вычисление theta2
        cos_theta2 = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
        if abs(cos_theta2) > 1:
            raise ValueError("Невозможно достичь заданной точки")
        theta2 = math.acos(cos_theta2)
        
        # Вычисление theta1
        theta1 = math.atan2(y, x) - math.atan2(
            L2 * math.sin(theta2),
            L1 + L2 * math.cos(theta2)
        )
        
        # Приведение углов к диапазону [0, 2π)
        theta1 = theta1 % (2 * math.pi)
        theta2 = theta2 % (2 * math.pi)
        
        if output_degrees:
            theta1 = math.degrees(theta1)
            theta2 = math.degrees(theta2)
            
        return theta1, theta2
        
    except Exception as e:
        raise ValueError(f"Ошибка при вычислении углов: {str(e)}")

def test_inverse_kinematics():
    """Тестирование функции inverse_kinematics"""
    test_cases = [
        # Корректные случаи
        ((0.5, 0.5), True),
        ((1.0, 0.0), True),
        ((0.0, 1.0), True),
        
        # Граничные случаи
        ((1.5, 0.0), True),  # Максимальная досягаемость по X
        ((0.0, 1.5), True),  # Максимальная досягаемость по Y
        
        # Некорректные случаи
        ((2.0, 0.0), False),  # За пределами досягаемости
        ((0.0, 0.0), False),  # Внутри минимальной досягаемости
        (("a", 0.5), False),  # Некорректный тип данных
    ]
    
    for (x, y), should_succeed in test_cases:
        try:
            theta1, theta2 = inverse_kinematics(x, y)
            if should_succeed:
                print(f"Успех: точка ({x}, {y}) -> углы: {theta1:.2f}, {theta2:.2f}")
            else:
                print(f"Ошибка: тест должен был завершиться с ошибкой для точки ({x}, {y})")
        except ValueError as e:
            if should_succeed:
                print(f"Ошибка: тест должен был пройти успешно для точки ({x}, {y})")
            else:
                print(f"Успех: получена ожидаемая ошибка для точки ({x}, {y}): {str(e)}")

def visualize_manipulator(theta1: float, theta2: float, target_x: float, target_y: float):
    """
    Визуализирует манипулятор и целевую точку.
    
    Args:
        theta1 (float): Угол первого сустава в радианах
        theta2 (float): Угол второго сустава в радианах
        target_x (float): X-координата целевой точки
        target_y (float): Y-координата целевой точки
    """
    joint1_x = L1 * math.cos(theta1)
    joint1_y = L1 * math.sin(theta1)
    
    joint2_x = joint1_x + L2 * math.cos(theta1 + theta2)
    joint2_y = joint1_y + L2 * math.sin(theta1 + theta2)
    
    plt.figure(figsize=(7, 7))

    plt.plot([0, joint1_x], [0, joint1_y], 'b-', linewidth=2, label='Сегмент 1')
    plt.plot([joint1_x, joint2_x], [joint1_y, joint2_y], 'r-', linewidth=2, label='Сегмент 2')
    
    plt.plot(0, 0, 'ko')
    plt.plot(joint1_x, joint1_y, 'ko')
    plt.plot(joint2_x, joint2_y, 'ko')
    
    plt.plot(target_x, target_y, 'g*', markersize=15, label='Целевая точка')
    
    plt.grid(True)
    plt.axis('equal')
    plt.title('Визуализация манипулятора')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    
    # Установка пределов осей
    max_range = L1 + L2 + 0.2
    plt.xlim(-max_range, max_range)
    plt.ylim(-max_range, max_range)
    
    plt.show()

if __name__ == "__main__":
    try:
        x_target, y_target = 2, 0
        theta1, theta2 = inverse_kinematics(x_target, y_target, output_degrees=True)
        print(f"Для точки ({x_target}, {y_target}):")
        print(f"Углы суставов: θ1 = {theta1:.2f}°, θ2 = {theta2:.2f}°")
        
        # Визуализация
        visualize_manipulator(
            math.radians(theta1),
            math.radians(theta2),
            x_target,
            y_target
        )
        
        # Запуск тестов
        print("\nЗапуск тестов:")
        test_inverse_kinematics()
        
    except ValueError as e:
        print(f"Ошибка: {str(e)}") 