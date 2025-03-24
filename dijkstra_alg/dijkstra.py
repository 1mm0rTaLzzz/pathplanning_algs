import math
import pygame
import sys
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
        
        # Определяем начальную точку, целевую точку и препятствия
        start = (5, 5)
        goal = (35, 35)
        obstacles = [(20, 20), (25, 25), (30, 30)]
        
        # Создаем объект алгоритма Дейкстры
        dijkstra = Dijkstra(start, goal, obstacles)
        
        print(f"Начальная точка: {start}")
        print(f"Целевая точка: {goal}")
        print(f"Количество препятствий: {len(obstacles)}")
        print("Нажмите ESC для выхода")
        
        running = True
        last_update_time = pygame.time.get_ticks()
        update_interval = 50  # миллисекунды между обновлениями
        
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            screen.fill(WHITE)
            
            # Отрисовка сетки
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    pygame.draw.rect(screen, (200, 200, 200), 
                                   (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            
            # Отрисовка препятствий
            for obs in obstacles:
                pygame.draw.circle(screen, RED, 
                                 (int(obs[1]*CELL_SIZE + CELL_SIZE/2),
                                  int(obs[0]*CELL_SIZE + CELL_SIZE/2)),
                                 CELL_SIZE//2)
                pygame.draw.circle(screen, (139, 0, 0),
                                 (int(obs[1]*CELL_SIZE + CELL_SIZE/2),
                                  int(obs[0]*CELL_SIZE + CELL_SIZE/2)),
                                 CELL_SIZE//2, 2)
            
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
                    print("Путь не найден")
                    dijkstra.path_complete = True
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 