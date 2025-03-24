import math
import pygame
import sys
import random
import copy

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
        self.influence_range = 7.0
        self.repulsive_gain = 150.0
        self.attractive_gain = 0.5
        self.grid = [[0.0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.collision_distance = 0.4  # Уменьшаем дистанцию обнаружения столкновений
        # Добавляем счетчик неудачных попыток
        self.failed_attempts = 0
        # Запоминаем неудачные направления
        self.failed_directions = []

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
                # Добавляем линейное увеличение потенциала вместо экспоненциального
                potential = 0.5 * self.repulsive_gain * (1/min_dist - 1/self.influence_range)**2 * (1 + math.cos(angle)) * (1 + (self.influence_range - min_dist))
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

    def is_collision(self, point):
        """Проверяет столкновение с препятствием"""
        x, y = point
        # Проверяем границы поля
        if x < 1 or x > GRID_SIZE-2 or y < 1 or y > GRID_SIZE-2:
            return True
            
        for obs in self.obstacles:
            dist = math.sqrt((x - obs[0])**2 + (y - obs[1])**2)
            if dist < self.collision_distance:  # Используем поле класса
                return True
        return False
        
    def check_path_collision(self, start_point, end_point, steps=5):
        """Проверяет столкновения на пути между двумя точками с промежуточными проверками"""
        for i in range(1, steps+1):
            # Проверяем несколько точек на пути
            t = i / steps
            x = start_point[0] + t * (end_point[0] - start_point[0])
            y = start_point[1] + t * (end_point[1] - start_point[1])
            
            if self.is_collision((x, y)):
                return True
                
        return False

def create_simple_walls():
    """Создаёт минимальное количество препятствий в левой части поля"""
    obstacles = []
    
    # Всего несколько препятствий в левой части поля
    obstacles.append((8, 15))   # Верхнее препятствие
    obstacles.append((15, 20))  # Центральное препятствие
    obstacles.append((10, 25))  # Нижнее препятствие
    obstacles.append((20, 10))  # Дополнительное препятствие
    
    # Начальная и конечная точки
    start = (5, 5)
    goal = (35, 35)
    
    # Убеждаемся, что в начальной и конечной точке нет препятствий
    filtered_obstacles = []
    for obs in obstacles:
        start_dist = math.sqrt((obs[0] - start[0])**2 + (obs[1] - start[1])**2)
        goal_dist = math.sqrt((obs[0] - goal[0])**2 + (obs[1] - goal[1])**2)
        
        if start_dist > 2 and goal_dist > 2:
            filtered_obstacles.append(obs)
    
    return filtered_obstacles, start, goal

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
        
        # Используем функцию создания простых стенок вместо лабиринта
        obstacles, start, goal = create_simple_walls()
        
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
        local_minimum_detected = False
        last_positions = []
        last_update_time = pygame.time.get_ticks()
        update_interval = 30  # миллисекунды между обновлениями (сделаем быстрее)
        
        # Добавляем параметр для отображения потенциального поля
        show_potential_field = False
        
        print(f"Начальная точка: {start}")
        print(f"Целевая точка: {goal}")
        print(f"Количество препятствий: {len(obstacles)}")
        print("Нажмите ESC для выхода")
        print("Нажмите R для перегенерации стенок")
        print("Нажмите P для отображения/скрытия потенциального поля")
        
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        # Перегенерация стенок
                        obstacles, start, goal = create_simple_walls()
                        pf = PotentialField(start, goal, obstacles)
                        pf.calculate_potential_field()
                        current_path = [start]
                        current_pos = start
                        step_count = 0
                        path_complete = False
                        stuck_counter = 0
                        local_minimum_detected = False
                        last_positions = []
                        print(f"Стенки перегенерированы. Препятствий: {len(obstacles)}")
                    elif event.key == pygame.K_p:
                        # Переключаем отображение потенциального поля
                        show_potential_field = not show_potential_field
                        print(f"Отображение потенциального поля: {'включено' if show_potential_field else 'выключено'}")
            
            screen.fill(WHITE)
            
            # Отображение потенциального поля, если включено
            if show_potential_field:
                max_potential = 0
                # Находим максимальное значение потенциала для нормализации
                for i in range(GRID_SIZE):
                    for j in range(GRID_SIZE):
                        if pf.grid[i][j] < float('inf'):
                            max_potential = max(max_potential, pf.grid[i][j])
                
                # Отображаем потенциальное поле как градиент цветов
                for i in range(GRID_SIZE):
                    for j in range(GRID_SIZE):
                        if pf.grid[i][j] < float('inf'):
                            # Нормализуем значение от 0 до 1
                            norm_value = min(pf.grid[i][j] / max_potential, 1.0) if max_potential > 0 else 0
                            # Преобразуем в цвет от синего (низкий потенциал) до красного (высокий потенциал)
                            color = (int(255 * norm_value), 0, int(255 * (1 - norm_value)))
                            pygame.draw.rect(screen, color, 
                                           (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)
            
            # Отрисовка сетки
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    pygame.draw.rect(screen, (200, 200, 200), 
                                   (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            
            # Отрисовка препятствий - делаем их меньше
            for obs in obstacles:
                pygame.draw.circle(screen, RED, 
                                 (int(obs[1]*CELL_SIZE + CELL_SIZE/2),
                                  int(obs[0]*CELL_SIZE + CELL_SIZE/2)),
                                 CELL_SIZE//3)  # Уменьшаем размер до 1/3
                pygame.draw.circle(screen, (139, 0, 0),
                                 (int(obs[1]*CELL_SIZE + CELL_SIZE/2),
                                  int(obs[0]*CELL_SIZE + CELL_SIZE/2)),
                                 CELL_SIZE//3, 1)  # Тонкая обводка
            
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
                
                # Проверка на выход за границы и коррекция позиции если необходимо
                if x_int < 1:
                    x = 1.0
                    current_pos = (x, y)
                elif x_int >= GRID_SIZE-2:
                    x = GRID_SIZE-2.0
                    current_pos = (x, y)
                
                if y_int < 1:
                    y = 1.0
                    current_pos = (x, y)
                elif y_int >= GRID_SIZE-2:
                    y = GRID_SIZE-2.0
                    current_pos = (x, y)
                
                if x_int < 0 or x_int >= GRID_SIZE or y_int < 0 or y_int >= GRID_SIZE:
                    print(f"Выход за границы: x={x_int}, y={y_int}")
                    path_complete = True
                else:
                    # Если обнаружен локальный минимум, добавляем случайное возмущение
                    if local_minimum_detected:
                        # Добавление случайного возмущения в направлении цели
                        goal_dir_x = goal[0] - x
                        goal_dir_y = goal[1] - y
                        norm = math.sqrt(goal_dir_x**2 + goal_dir_y**2)
                        if norm > 0:
                            goal_dir_x /= norm
                            goal_dir_y /= norm
                            
                            # Увеличиваем область поиска с ростом числа неудачных попыток
                            noise_amplitude = min(0.8 + pf.failed_attempts * 0.1, 2.0)
                            step_size = min(0.5 + pf.failed_attempts * 0.1, 1.5)
                            
                            # Пробуем несколько возмущений, пока не найдем безопасное
                            found_safe_path = False
                            for attempt in range(20):  # Увеличиваем число попыток
                                # Случайное возмущение с уклоном в сторону цели
                                # Чем больше неудачных попыток, тем более случайным делаем направление
                                if pf.failed_attempts > 5:
                                    # Более случайное направление, когда много неудач
                                    random_perturb_x = random.uniform(-1.0, 1.0)
                                    random_perturb_y = random.uniform(-1.0, 1.0)
                                else:
                                    # Направление с уклоном к цели для первых попыток
                                    random_perturb_x = goal_dir_x + random.uniform(-noise_amplitude, noise_amplitude)
                                    random_perturb_y = goal_dir_y + random.uniform(-noise_amplitude, noise_amplitude)
                                
                                # Нормализуем вектор возмущения
                                perturb_norm = math.sqrt(random_perturb_x**2 + random_perturb_y**2)
                                if perturb_norm > 0:
                                    random_perturb_x /= perturb_norm
                                    random_perturb_y /= perturb_norm
                                
                                # Проверяем, не пробовали ли мы уже это направление
                                too_similar = False
                                for dir_x, dir_y in pf.failed_directions:
                                    similarity = dir_x * random_perturb_x + dir_y * random_perturb_y
                                    if similarity > 0.9:  # Если направления очень похожи
                                        too_similar = True
                                        break
                                
                                if too_similar and len(pf.failed_directions) < 20:
                                    continue  # Пропускаем похожие направления
                                    
                                new_x = x + random_perturb_x * step_size
                                new_y = y + random_perturb_y * step_size
                                
                                # Проверяем, что новая позиция в пределах поля
                                if 1 <= new_x <= GRID_SIZE-2 and 1 <= new_y <= GRID_SIZE-2:
                                    # Проверка на столкновение
                                    new_point = (new_x, new_y)
                                    if not pf.is_collision(new_point):
                                        current_pos = new_point
                                        current_path.append(current_pos)
                                        local_minimum_detected = False
                                        stuck_counter = 0
                                        last_positions = []
                                        pf.failed_attempts = 0  # Сбрасываем счетчик неудач
                                        pf.failed_directions = []  # Очищаем историю неудачных направлений
                                        print("Выход из локального минимума с помощью случайного возмущения")
                                        found_safe_path = True
                                        break
                                    else:
                                        # Запоминаем неудачное направление
                                        if len(pf.failed_directions) > 20:
                                            pf.failed_directions.pop(0)  # Удаляем самое старое
                                        pf.failed_directions.append((random_perturb_x, random_perturb_y))
                            
                            # Если не смогли найти безопасный путь, пробуем отступить назад
                            if not found_safe_path:
                                pf.failed_attempts += 1  # Увеличиваем счетчик неудач
                                
                                # Если много неудач, делаем большой прыжок в случайном направлении
                                if pf.failed_attempts > 10:
                                    for _ in range(20):  # Пробуем до 20 направлений
                                        random_dir_x = random.uniform(-1.0, 1.0)
                                        random_dir_y = random.uniform(-1.0, 1.0)
                                        dir_norm = math.sqrt(random_dir_x**2 + random_dir_y**2)
                                        if dir_norm > 0:
                                            random_dir_x /= dir_norm
                                            random_dir_y /= dir_norm
                                        
                                        jump_x = x + random_dir_x * 2.0  # Большой прыжок
                                        jump_y = y + random_dir_y * 2.0
                                        
                                        if 1 <= jump_x <= GRID_SIZE-2 and 1 <= jump_y <= GRID_SIZE-2:
                                            if not pf.is_collision((jump_x, jump_y)):
                                                current_pos = (jump_x, jump_y)
                                                current_path.append(current_pos)
                                                local_minimum_detected = False
                                                stuck_counter = 0
                                                last_positions = []
                                                pf.failed_attempts = 0
                                                pf.failed_directions = []
                                                print("Делаем большой прыжок для выхода из тупика")
                                                found_safe_path = True
                                                break
                                
                                # Если все еще не удалось, отступаем от препятствия
                                if not found_safe_path:
                                    back_step = 0.7 + pf.failed_attempts * 0.1  # Увеличиваем шаг отступления
                                    back_x = x - goal_dir_x * back_step
                                    back_y = y - goal_dir_y * back_step
                                    
                                    if 1 <= back_x <= GRID_SIZE-2 and 1 <= back_y <= GRID_SIZE-2:
                                        if not pf.is_collision((back_x, back_y)):
                                            current_pos = (back_x, back_y)
                                            current_path.append(current_pos)
                                            local_minimum_detected = False
                                            stuck_counter = 0
                                            last_positions = []
                                            print("Отступаем от препятствия в обратном направлении")
                                
                                # Если количество неудач больше 20, обнуляем путь и начинаем сначала
                                if not found_safe_path and pf.failed_attempts > 20:
                                    print("Слишком много неудачных попыток - возвращаемся к началу")
                                    current_path = [start]
                                    current_pos = start
                                    local_minimum_detected = False
                                    stuck_counter = 0
                                    last_positions = []
                                    pf.failed_attempts = 0
                                    pf.failed_directions = []
                    else:
                        # Обычное движение по градиенту потенциального поля
                        dx = pf.grid[min(x_int+1, GRID_SIZE-1)][y_int] - pf.grid[max(x_int-1, 0)][y_int]
                        dy = pf.grid[x_int][min(y_int+1, GRID_SIZE-1)] - pf.grid[x_int][max(y_int-1, 0)]
                        
                        norm = math.sqrt(dx*dx + dy*dy)
                        if norm > 0:
                            dx = dx/norm
                            dy = dy/norm
                            
                            # Стандартный шаг движения
                            step_size = 0.2
                            new_x = x - dx * step_size
                            new_y = y - dy * step_size
                            
                            if math.isnan(new_x) or math.isnan(new_y):
                                print("Обнаружен NaN в координатах")
                                path_complete = True
                            else:
                                # Проверка на столкновение без сложных проверок пути
                                new_point = (new_x, new_y)
                                if not pf.is_collision(new_point):
                                    current_pos = new_point
                                    last_positions.append(current_pos)
                                    if len(last_positions) > 10:
                                        last_positions.pop(0)
                                        avg_movement = 0
                                        for p in last_positions:
                                            avg_movement += math.sqrt((p[0]-current_pos[0])**2 + (p[1]-current_pos[1])**2)
                                        avg_movement /= len(last_positions)
                                        
                                        if avg_movement < 0.1:  # Мало движения - застряли
                                            stuck_counter += 1
                                            if stuck_counter > 5:
                                                print("Застряли в локальном минимуме - применяем случайное возмущение")
                                                local_minimum_detected = True
                                        else:
                                            stuck_counter = 0
                                    
                                    current_path.append(current_pos)
                                    step_count += 1
                                    last_update_time = current_time
                                else:
                                    print("Обнаружено столкновение, ищем другой путь")
                                    local_minimum_detected = True
                        else:
                            print("Нулевой градиент - активируем случайное возмущение")
                            local_minimum_detected = True
                    
                    # Проверка достижения цели
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