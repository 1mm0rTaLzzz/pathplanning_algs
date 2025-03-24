import math
import pygame
import sys
import random
import copy
from heapq import heappush, heappop

# Константы для отображения
GRID_SIZE = 40
CELL_SIZE = 15
WINDOW_SIZE = (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Dijkstra:
    def __init__(self, start, goal, obstacles):
        self.start = start
        self.goal = goal
        self.obstacles = obstacles
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.initialize_grid()
        self.current_path = [start]
        self.current_pos = start
        self.step_count = 0
        self.path_complete = False
        self.visited = set()
        self.distances = {start: 0}
        self.previous = {start: None}
        self.pq = [(0, start)]
        self.path_edges = []

    def initialize_grid(self):
        # Инициализация сетки: 0 - свободно, 1 - препятствие
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if (i, j) in self.obstacles:
                    self.grid[i][j] = 1

    def get_neighbors(self, current):
        x, y = current
        neighbors = []
        # Проверяем все 8 направлений
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < GRID_SIZE and 
                    0 <= new_y < GRID_SIZE and 
                    self.grid[new_x][new_y] == 0):
                    neighbors.append((new_x, new_y))
        return neighbors

    def step(self):
        if not self.pq or self.path_complete:
            return False

        current_distance, current = heappop(self.pq)
        
        if current == self.goal:
            self.path_complete = True
            return True
            
        if current in self.visited:
            return True
            
        self.visited.add(current)
        self.current_pos = current
        
        for neighbor in self.get_neighbors(current):
            # Стоимость перехода (1 для ортогональных, sqrt(2) для диагональных)
            dx = abs(neighbor[0] - current[0])
            dy = abs(neighbor[1] - current[1])
            cost = math.sqrt(2) if dx == 1 and dy == 1 else 1
            
            distance = current_distance + cost
            
            if neighbor not in self.distances or distance < self.distances[neighbor]:
                self.distances[neighbor] = distance
                self.previous[neighbor] = current
                heappush(self.pq, (distance, neighbor))
                # Добавляем ребро для отрисовки
                self.path_edges.append((current, neighbor))

        self.step_count += 1
        # Обновляем текущий путь для визуализации
        if current != self.start:
            prev = self.previous[current]
            if prev is not None:
                self.current_path.append(current)
        
        return True

    def get_path(self):
        path = []
        current = self.goal
        while current is not None:
            path.append(current)
            current = self.previous.get(current)
        return list(reversed(path))

def generate_maze_obstacles(grid_size, start, goal, wall_density=0.3):
    """Генерирует лабиринт из препятствий
    
    Args:
        grid_size: размер сетки
        start: начальная точка (x, y)
        goal: целевая точка (x, y)
        wall_density: плотность препятствий (0.0 - 1.0)
        
    Returns:
        list: список координат препятствий
    """
    obstacles = []
    
    # Создаем препятствия с заданной плотностью
    for i in range(grid_size):
        for j in range(grid_size):
            # Проверяем, что точка не является стартом или целью
            if (i, j) != start and (i, j) != goal:
                # Проверяем, что точка не слишком близко к старту или цели
                start_dist = math.sqrt((i - start[0])**2 + (j - start[1])**2)
                goal_dist = math.sqrt((i - goal[0])**2 + (j - goal[1])**2)
                
                if start_dist > 3 and goal_dist > 3 and random.random() < wall_density:
                    obstacles.append((i, j))
    
    # Добавляем внешние стены
    for i in range(grid_size):
        if (i, 0) != start and (i, 0) != goal:
            obstacles.append((i, 0))
        if (i, grid_size-1) != start and (i, grid_size-1) != goal:
            obstacles.append((i, grid_size-1))
    
    for j in range(grid_size):
        if (0, j) != start and (0, j) != goal:
            obstacles.append((0, j))
        if (grid_size-1, j) != start and (grid_size-1, j) != goal:
            obstacles.append((grid_size-1, j))
    
    return obstacles

def check_path_exists(dijkstra_instance):
    """Проверяет, существует ли путь от начала к концу"""
    # Создаем глубокую копию для безопасной проверки
    dijkstra_copy = copy.deepcopy(dijkstra_instance)
    
    # Запускаем алгоритм до завершения
    while dijkstra_copy.step():
        if dijkstra_copy.path_complete:
            return True
    
    return False

def create_maze_with_pattern():
    """Создаёт лабиринт с более структурированным паттерном и гарантированным путём"""
    obstacles = []
    
    # Добавляем внешние стены
    for i in range(GRID_SIZE):
        obstacles.append((i, 0))
        obstacles.append((i, GRID_SIZE-1))
    
    for j in range(GRID_SIZE):
        obstacles.append((0, j))
        obstacles.append((GRID_SIZE-1, j))
    
    # Создаем горизонтальные стены с проходами
    for i in range(5, GRID_SIZE-5, 6):
        passage = random.randint(2, GRID_SIZE-3)
        for j in range(1, GRID_SIZE-1):
            if j != passage and j != passage+1:
                obstacles.append((i, j))
    
    # Создаем вертикальные стены с проходами
    for j in range(5, GRID_SIZE-5, 6):
        passage = random.randint(2, GRID_SIZE-3)
        for i in range(1, GRID_SIZE-1):
            if i != passage and i != passage+1:
                obstacles.append((i, j))
    
    # Добавляем случайные острова препятствий
    for _ in range(8):  # Уменьшаем количество островов для большей проходимости
        island_x = random.randint(5, GRID_SIZE-6)
        island_y = random.randint(5, GRID_SIZE-6)
        
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if random.random() < 0.6:  # Уменьшаем вероятность препятствия для большей проходимости
                    obstacles.append((island_x + dx, island_y + dy))
    
    # Определяем начальную и конечную точки
    start = (5, 5)
    goal = (GRID_SIZE-6, GRID_SIZE-6)
    
    # Убираем препятствия рядом с начальной и конечной точками
    filtered_obstacles = []
    for obs in obstacles:
        start_dist = math.sqrt((obs[0] - start[0])**2 + (obs[1] - start[1])**2)
        goal_dist = math.sqrt((obs[0] - goal[0])**2 + (obs[1] - goal[1])**2)
        
        if start_dist > 3 and goal_dist > 3:  # Увеличиваем зону без препятствий
            filtered_obstacles.append(obs)
    
    # Проверяем, существует ли путь от начала к концу
    temp_dijkstra = Dijkstra(start, goal, filtered_obstacles)
    path_exists = check_path_exists(temp_dijkstra)
    
    # Если путь не существует, пробуем удалить препятствия до тех пор,
    # пока путь не появится
    if not path_exists:
        # Создаем список препятствий, которые могут быть удалены
        # (не внешние стены)
        removable_obstacles = [obs for obs in filtered_obstacles 
                              if obs[0] != 0 and obs[0] != GRID_SIZE-1 
                              and obs[1] != 0 and obs[1] != GRID_SIZE-1]
        
        # Перемешиваем список для случайного порядка удаления
        random.shuffle(removable_obstacles)
        
        # Постепенно удаляем препятствия, пока не появится путь
        for obs in removable_obstacles:
            # Удаляем препятствие из списка
            filtered_obstacles.remove(obs)
            
            # Проверяем, существует ли теперь путь
            temp_dijkstra = Dijkstra(start, goal, filtered_obstacles)
            if check_path_exists(temp_dijkstra):
                break
    
    return filtered_obstacles, start, goal

def main():
    try:
        # Инициализация pygame
        pygame.init()
        print("Pygame успешно инициализирован")
        
        # Создание окна
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Алгоритм Дейкстры")
        print(f"Окно создано с размером {WINDOW_SIZE}")
        
        clock = pygame.time.Clock()
        
        # Используем функцию создания лабиринта с гарантией пути
        obstacles, start, goal = create_maze_with_pattern()
        
        # Создаем объект алгоритма Дейкстры
        dijkstra = Dijkstra(start, goal, obstacles)
        
        print(f"Начальная точка: {start}")
        print(f"Целевая точка: {goal}")
        print(f"Количество препятствий: {len(obstacles)}")
        print("Нажмите ESC для выхода")
        print("Нажмите R для перегенерации лабиринта")
        
        running = True
        last_update_time = pygame.time.get_ticks()
        update_interval = 5  # Еще быстрее, 5 мс между обновлениями
        
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        # Перегенерация лабиринта с гарантией пути
                        obstacles, start, goal = create_maze_with_pattern()
                        dijkstra = Dijkstra(start, goal, obstacles)
                        print(f"Лабиринт перегенерирован. Препятствий: {len(obstacles)}")
            
            screen.fill(WHITE)
            
            # Отрисовка сетки
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    pygame.draw.rect(screen, (200, 200, 200), 
                                   (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            
            # Отрисовка препятствий
            for obs in obstacles:
                pygame.draw.rect(screen, RED, 
                               (obs[1]*CELL_SIZE, obs[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
            # Отрисовка начальной точки
            pygame.draw.circle(screen, GREEN,
                             (int(start[1]*CELL_SIZE + CELL_SIZE/2),
                              int(start[0]*CELL_SIZE + CELL_SIZE/2)),
                             CELL_SIZE//2)
            
            # Отрисовка целевой точки
            pygame.draw.circle(screen, BLUE,
                             (int(goal[1]*CELL_SIZE + CELL_SIZE/2),
                              int(goal[0]*CELL_SIZE + CELL_SIZE/2)),
                             CELL_SIZE//2)
            
            # Отрисовка рёбер путей
            for edge in dijkstra.path_edges:
                src, dst = edge
                pygame.draw.line(screen, GREEN,
                               (int(src[1]*CELL_SIZE + CELL_SIZE/2),
                                int(src[0]*CELL_SIZE + CELL_SIZE/2)),
                               (int(dst[1]*CELL_SIZE + CELL_SIZE/2),
                                int(dst[0]*CELL_SIZE + CELL_SIZE/2)),
                               1)
                                
            # Отрисовка текущего пути только если путь уже найден
            if dijkstra.path_complete and len(dijkstra.current_path) > 1:
                for i in range(len(dijkstra.current_path)-1):
                    pygame.draw.line(screen, BLACK,
                                   (int(dijkstra.current_path[i][1]*CELL_SIZE + CELL_SIZE/2),
                                    int(dijkstra.current_path[i][0]*CELL_SIZE + CELL_SIZE/2)),
                                   (int(dijkstra.current_path[i+1][1]*CELL_SIZE + CELL_SIZE/2),
                                    int(dijkstra.current_path[i+1][0]*CELL_SIZE + CELL_SIZE/2)),
                                   2)
            
            # Обновление пути
            if not dijkstra.path_complete and current_time - last_update_time >= update_interval:
                if dijkstra.step():
                    last_update_time = current_time
                    if dijkstra.path_complete:
                        # Отображаем финальный путь
                        dijkstra.current_path = dijkstra.get_path()
                        print(f"Путь построен! Количество шагов: {dijkstra.step_count}")
                        print(f"Длина пути: {len(dijkstra.current_path)}")
                else:
                    print("Путь не найден - такого не должно быть при корректной генерации лабиринта")
                    dijkstra.path_complete = True
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 