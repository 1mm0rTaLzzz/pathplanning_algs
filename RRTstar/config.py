from pygame import font


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)  # Добавлен фиолетовый цвет для RRT*

WIDTH = 800
HEIGHT = 600
font.init()
FONT = font.SysFont('Tahoma', 25, bold = True)

# Параметры алгоритма RRT*
RADIUS = 100  # Увеличенный радиус поиска соседей для rewiring (было 50)
MAX_ITERATIONS = 10000  # Увеличенное максимальное количество итераций (было 10000)
MIN_ITERATIONS_AFTER_SOLUTION = 2000  # Продолжать поиск после нахождения первого решения
GOAL_SAMPLE_RATE = 0.1  # Вероятность выбора цели в качестве случайного узла 