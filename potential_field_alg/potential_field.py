import math
import pygame
import sys

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

class PotentialField:
    def __init__(self, start, goal, obstacles):
        self.start = start
        self.goal = goal
        self.obstacles = obstacles
        self.influence_range = 5.0
        self.repulsive_gain = 100.0
        self.attractive_gain = 0.5  # Коэффициент притяжения к цели
        self.grid = [[0.0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def attractive_potential(self, x, y):
        # Притягивающий потенциал к цели
        dist = math.sqrt((x - self.goal[0])**2 + (y - self.goal[1])**2)
        return self.attractive_gain * dist

    def repulsive_potential(self, x, y):
        min_dist = float('inf')
        closest_obs = None
        for obs in self.obstacles:
            dist = math.sqrt((x - obs[0])**2 + (y - obs[1])**2)
            if dist < min_dist:
                min_dist = dist
                closest_obs = obs
        
        if min_dist <= self.influence_range and min_dist > 0.001:
            # Добавляем направленный отталкивающий потенциал
            if closest_obs:
                dx = x - closest_obs[0]
                dy = y - closest_obs[1]
                # Проверяем на нулевые значения
                if abs(dx) < 0.001 and abs(dy) < 0.001:
                    return float('inf')
                angle = math.atan2(dy, dx)
                # Проверяем на NaN
                if math.isnan(angle):
                    return float('inf')
                # Усиливаем отталкивание в направлении от препятствия
                potential = 0.5 * self.repulsive_gain * (1/min_dist - 1/self.influence_range)**2 * (1 + math.cos(angle))
                return potential if not math.isnan(potential) else float('inf')
            return 0.5 * self.repulsive_gain * (1/min_dist - 1/self.influence_range)**2
        elif min_dist <= 0.001:
            return float('inf')
        return 0

    def calculate_potential_field(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                # Комбинируем притягивающий и отталкивающий потенциалы
                self.grid[i][j] = self.attractive_potential(j, i) + self.repulsive_potential(j, i)

def main():
    try:
        # Инициализация pygame
        pygame.init()
        print("Pygame успешно инициализирован")
        
        # Создание окна
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Метод потенциальных полей")
        print(f"Окно создано с размером {WINDOW_SIZE}")
        
        clock = pygame.time.Clock()
        
        # Определяем начальную точку, целевую точку и препятствия
        start = (5, 5)
        goal = (35, 35)
        obstacles = [(20, 20), (25, 25), (30, 30)]
        
        # Создаем объект потенциального поля
        pf = PotentialField(start, goal, obstacles)
        pf.calculate_potential_field()
        
        # Инициализация для анимации
        current_path = [start]
        current_pos = start
        step_count = 0
        max_steps = 3000
        path_complete = False
        stuck_counter = 0
        last_positions = []
        last_update_time = pygame.time.get_ticks()
        update_interval = 50  # миллисекунды между обновлениями
        
        print(f"Начальная точка: {start}")
        print(f"Целевая точка: {goal}")
        print(f"Количество препятствий: {len(obstacles)}")
        print("Нажмите ESC для выхода")
        
        running = True
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
            
            # Отрисовка текущего пути
            if len(current_path) > 1:
                for i in range(len(current_path)-1):
                    try:
                        x1 = max(0, min(GRID_SIZE-1, current_path[i][1]))
                        y1 = max(0, min(GRID_SIZE-1, current_path[i][0]))
                        x2 = max(0, min(GRID_SIZE-1, current_path[i+1][1]))
                        y2 = max(0, min(GRID_SIZE-1, current_path[i+1][0]))
                        
                        pygame.draw.line(screen, BLACK,
                                       (int(x1*CELL_SIZE + CELL_SIZE/2),
                                        int(y1*CELL_SIZE + CELL_SIZE/2)),
                                       (int(x2*CELL_SIZE + CELL_SIZE/2),
                                        int(y2*CELL_SIZE + CELL_SIZE/2)),
                                       2)
                    except (ValueError, TypeError):
                        continue
            
            # Построение пути с задержкой
            if not path_complete and step_count < max_steps and current_time - last_update_time >= update_interval:
                x, y = current_pos
                x_int = int(x)
                y_int = int(y)
                
                if x_int < 0 or x_int >= GRID_SIZE or y_int < 0 or y_int >= GRID_SIZE:
                    print(f"Выход за границы: x={x_int}, y={y_int}")
                    path_complete = True
                else:
                    dx = pf.grid[min(x_int+1, GRID_SIZE-1)][y_int] - pf.grid[max(x_int-1, 0)][y_int]
                    dy = pf.grid[x_int][min(y_int+1, GRID_SIZE-1)] - pf.grid[x_int][max(y_int-1, 0)]
                    
                    norm = math.sqrt(dx*dx + dy*dy)
                    if norm > 0:
                        dx = dx/norm
                        dy = dy/norm
                        
                        new_x = x - dx * 0.2
                        new_y = y - dy * 0.2
                        
                        if math.isnan(new_x) or math.isnan(new_y):
                            print("Обнаружен NaN в координатах")
                            path_complete = True
                        else:
                            current_pos = (new_x, new_y)
                            last_positions.append(current_pos)
                            if len(last_positions) > 10:
                                last_positions.pop(0)
                                if all(math.sqrt((p[0]-current_pos[0])**2 + (p[1]-current_pos[1])**2) < 0.1 for p in last_positions):
                                    stuck_counter += 1
                                    if stuck_counter > 5:
                                        print("Застряли в локальном минимуме")
                                        path_complete = True
                                else:
                                    stuck_counter = 0
                            
                            current_path.append(current_pos)
                            step_count += 1
                            last_update_time = current_time
                    else:
                        print("Нулевой градиент")
                        path_complete = True
            
            if math.sqrt((current_pos[0] - goal[0])**2 + (current_pos[1] - goal[1])**2) <= 0.5:
                path_complete = True
                print(f"Путь построен! Количество шагов: {step_count}")
                print(f"Длина пути: {len(current_path)}")
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 