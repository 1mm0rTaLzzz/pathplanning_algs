import pygame
import random
import math
import time

import collision
import config as cfg
import utils

# Определение класса узла
class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.cost = 0  # Стоимость пути от начала до этого узла

# Определение класса RRT*
class RRTStar:
    def __init__(self, start, goal, obstacles):
        self.start = start
        self.goal = goal
        self.obstacles = obstacles
        self.nodes = [start]
        self.step_size = 20
        self.final_step = 50
        self.base_radius = cfg.RADIUS  # Базовый радиус для rewiring
        self.path_found = False
        self.best_goal_node = None
        self.best_cost = float('inf')
        self.solution_iter = 0  # Итерация, на которой найдено первое решение
    
    def calculate_dynamic_radius(self):
        """Вычисляет динамический радиус в зависимости от количества узлов"""
        # Формула из теории RRT*: gamma * (log(n)/n)^(1/d), где d - размерность пространства (2)
        n = max(1, len(self.nodes))
        gamma = 2.0 * math.sqrt((cfg.WIDTH * cfg.HEIGHT) / math.pi)
        radius = min(gamma * math.sqrt(math.log(n) / n), self.base_radius * 2)
        # Ограничение снизу
        return max(radius, self.base_radius / 2)
    
    def find_nearest(self, node):
        """Находит ближайший узел к заданному"""
        nearest = self.nodes[0]
        min_dist = float('inf')
        for n in self.nodes:
            dist = math.hypot(node.x - n.x, node.y - n.y)
            if dist < min_dist:
                min_dist = dist
                nearest = n
        return nearest

    def steer(self, from_node, to_node, step_size):
        """Создает новый узел в направлении целевого узла на расстоянии step_size"""
        dist = math.hypot(to_node.x - from_node.x, to_node.y - from_node.y)
        if dist < step_size:
            return to_node
        
        ratio = step_size / dist
        new_x = from_node.x + ratio * (to_node.x - from_node.x)
        new_y = from_node.y + ratio * (to_node.y - from_node.y)
        return Node(new_x, new_y)
    
    def find_near_nodes(self, new_node, radius):
        """Находит узлы рядом с новым узлом в заданном радиусе"""
        near_nodes = []
        for node in self.nodes:
            if math.hypot(node.x - new_node.x, node.y - new_node.y) <= radius:
                near_nodes.append(node)
        return near_nodes
    
    def choose_parent(self, new_node, near_nodes):
        """Выбирает родительский узел для нового узла из списка близких узлов"""
        if not near_nodes:
            return new_node
        
        # Находим узел с минимальной стоимостью пути
        min_cost = float('inf')
        best_parent = None
        
        for near_node in near_nodes:
            # Проверяем, можно ли соединить узлы без столкновений
            if not collision.collision(near_node, new_node, self.obstacles):
                # Вычисляем стоимость пути через этот узел
                cost = utils.cost(near_node) + math.hypot(near_node.x - new_node.x, near_node.y - new_node.y)
                if cost < min_cost:
                    min_cost = cost
                    best_parent = near_node
        
        if best_parent:
            new_node.parent = best_parent
            new_node.cost = min_cost
        
        return new_node
    
    def rewire(self, new_node, near_nodes):
        """Перестраивает дерево для оптимизации путей"""
        for near_node in near_nodes:
            # Проверяем не является ли near_node корнем или родителем нового узла
            if near_node == self.start or near_node == new_node.parent:
                continue
            
            # Проверяем, можно ли соединить узлы без столкновений
            if not collision.collision(new_node, near_node, self.obstacles):
                # Вычисляем новую стоимость пути через новый узел
                new_cost = new_node.cost + math.hypot(new_node.x - near_node.x, new_node.y - near_node.y)
                # Если новый путь короче, обновляем родителя
                if new_cost < utils.cost(near_node):
                    near_node.parent = new_node
    
    def check_goal(self, new_node):
        """Проверяет, достигнута ли цель и обновляет лучший путь"""
        dist_to_goal = math.hypot(new_node.x - self.goal.x, new_node.y - self.goal.y)
        
        if dist_to_goal < self.final_step:
            # Создаем узел цели
            final_node = Node(self.goal.x, self.goal.y)
            # Проверяем, можно ли соединить с целью без столкновений
            if not collision.collision(new_node, final_node, self.obstacles):
                # Устанавливаем родителя для финального узла
                final_node.parent = new_node
                # Вычисляем стоимость полного пути
                final_cost = new_node.cost + dist_to_goal
                
                # Если это первый путь к цели или он лучше предыдущего, обновляем
                if not self.path_found or final_cost < self.best_cost:
                    if not self.path_found:
                        self.path_found = True
                        self.solution_iter = len(self.nodes)
                        print(f"Первое решение найдено на итерации {self.solution_iter} с стоимостью {final_cost:.2f}")
                    else:
                        print(f"Найден лучший путь, стоимость улучшена с {self.best_cost:.2f} до {final_cost:.2f}")
                    
                    # Если у нас уже есть целевой узел в дереве, удаляем его
                    if self.best_goal_node in self.nodes:
                        self.nodes.remove(self.best_goal_node)
                    
                    self.best_goal_node = final_node
                    self.best_cost = final_cost
                    # Добавляем финальный узел в список узлов
                    self.nodes.append(final_node)
    
    def find_path(self):
        """Основной метод для поиска пути с помощью RRT*"""
        for i in range(cfg.MAX_ITERATIONS):
            # Вычисляем динамический радиус для этой итерации
            radius = self.calculate_dynamic_radius()
            
            # Генерируем случайный узел
            if random.random() < cfg.GOAL_SAMPLE_RATE:  # Увеличенная вероятность выбора цели
                rand_node = Node(self.goal.x, self.goal.y)
            else:
                rand_node = Node(random.randint(0, cfg.WIDTH), random.randint(0, cfg.HEIGHT))
            
            # Находим ближайший узел
            nearest_node = self.find_nearest(rand_node)
            
            # Создаем новый узел в направлении случайного узла
            new_node = self.steer(nearest_node, rand_node, self.step_size)
            
            # Проверяем на столкновения
            if not collision.collision(nearest_node, new_node, self.obstacles):
                # Находим близкие узлы
                near_nodes = self.find_near_nodes(new_node, radius)
                
                # Выбираем лучшего родителя для нового узла
                new_node = self.choose_parent(new_node, near_nodes)
                
                # Добавляем новый узел в список
                self.nodes.append(new_node)
                
                # Перестраиваем дерево (rewiring) только на каждой 5-й итерации или если число узлов < 1000
                # Это оптимизация для ускорения работы
                if len(self.nodes) < 1000 or i % 5 == 0:
                    self.rewire(new_node, near_nodes)
                
                # Проверяем, можно ли достичь цели из нового узла
                self.check_goal(new_node)
                
                # Отображаем прогресс
                if i % 1000 == 0:
                    print(f"Выполнено {i} итераций, количество узлов: {len(self.nodes)}")
                
                # Если найден путь и прошло достаточно дополнительных итераций для его улучшения
                if self.path_found and (len(self.nodes) - self.solution_iter) > cfg.MIN_ITERATIONS_AFTER_SOLUTION:
                    print(f"Путь найден и оптимизирован, остановка после {len(self.nodes)} итераций")
                    break
        
        # Если путь найден, возвращаем его
        if self.path_found:
            path = []
            current = self.best_goal_node
            while current is not None:
                path.append((current.x, current.y))
                current = current.parent
            print(f"Финальный путь состоит из {len(path)} точек с общей стоимостью {self.best_cost:.2f}")
            return path[::-1]  # Переворачиваем путь, чтобы он шел от старта к цели
        else:
            print("Путь не найден после всех итераций")
            return None
    
    def draw(self, screen):
        """Отрисовка дерева RRT*"""
        # Рисуем все узлы и ребра
        for node in self.nodes:
            pygame.draw.circle(screen, cfg.YELLOW, (int(node.x), int(node.y)), 3)
            if node.parent is not None:
                pygame.draw.line(screen, cfg.WHITE, (node.x, node.y), (node.parent.x, node.parent.y), 1)
        
        # Рисуем начальную и конечную точки
        pygame.draw.circle(screen, cfg.RED, (int(self.start.x), int(self.start.y)), 10)
        pygame.draw.circle(screen, cfg.GREEN, (int(self.goal.x), int(self.goal.y)), 10)
        
        # Если путь найден, рисуем его
        if self.path_found:
            path = []
            current = self.best_goal_node
            while current is not None:
                path.append((current.x, current.y))
                current = current.parent
            path = path[::-1]  # Переворачиваем путь
            if len(path) > 1:
                pygame.draw.lines(screen, cfg.PURPLE, False, path, 3)


# Определение функций для создания препятствий и получения начальной и конечной точек
def create_obstacles():
    """Создает препятствия, позволяя пользователю рисовать их мышью"""
    done = False
    flStartDraw = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                flStartDraw = True
            elif event.type == pygame.MOUSEMOTION:
                if flStartDraw:
                    pos = event.pos
                    pygame.draw.circle(screen, (0, 255, 255), pos, 10)
                    pygame.display.update()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                flStartDraw = False
    pygame.image.save(screen, 'map.png')
    obstaclesSurface = pygame.image.load('map.png')
    return obstaclesSurface


def get_start_end_points():
    """Получает от пользователя начальную и конечную точки"""
    screen.fill(cfg.BLACK)
    start = None
    end = None
    selecting_start = True
    selecting_end = False
    while selecting_start or selecting_end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if selecting_start:
                    start = Node(*pos)
                    pygame.draw.circle(screen, cfg.RED, pos, 10)
                    pygame.display.update()
                    selecting_start = False
                    selecting_end = True
                elif selecting_end:
                    end = Node(*pos)
                    pygame.draw.circle(screen, cfg.GREEN, pos, 10)
                    selecting_end = False

        pygame.display.update()
    return start, end


def main():
    """Основная функция для запуска алгоритма RRT*"""
    global screen
    
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("RRT* Algorithm (Optimized RRT)")
    
    infoSurface = pygame.Surface((cfg.WIDTH, cfg.HEIGHT))
    infoSurface.set_colorkey((0, 0, 0))
    
    # Получаем начальную и конечную точки
    start, goal = get_start_end_points()
    
    # Создаем препятствия
    obstacles = create_obstacles()
    
    # Создаем экземпляр RRT*
    rrtstar = RRTStar(start, goal, obstacles)
    
    # Запускаем поиск пути и замеряем время
    startTime = time.perf_counter()
    path = rrtstar.find_path()
    elapsed = time.perf_counter() - startTime
    elapsed = format(elapsed, '.4f')
    
    # Отображаем информацию о найденном пути
    info_text = f'Nodes: {len(rrtstar.nodes)} Time: {elapsed}s'
    if rrtstar.path_found:
        info_text += f' Path cost: {format(rrtstar.best_cost, ".2f")}'
    temp = cfg.FONT.render(info_text, 0, (0, 255, 0), (0, 0, 1))
    
    # Основной цикл отображения
    running = True
    show_tree = False
    show_detailed_info = False
    
    while running:
        screen.blit(infoSurface, (0, 0))
        infoSurface.blit(temp, (cfg.WIDTH - temp.get_width(), cfg.FONT.get_height()))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    show_tree = not show_tree
                elif event.key == pygame.K_i:
                    # Переключаем отображение подробной информации
                    show_detailed_info = not show_detailed_info
                elif event.key == pygame.K_r:
                    # Перезапуск с новыми препятствиями
                    screen.fill(cfg.BLACK)
                    start, goal = get_start_end_points()
                    obstacles = create_obstacles()
                    rrtstar = RRTStar(start, goal, obstacles)
                    startTime = time.perf_counter()
                    path = rrtstar.find_path()
                    elapsed = time.perf_counter() - startTime
                    elapsed = format(elapsed, '.4f')
                    info_text = f'Nodes: {len(rrtstar.nodes)} Time: {elapsed}s'
                    if rrtstar.path_found:
                        info_text += f' Path cost: {format(rrtstar.best_cost, ".2f")}'
                    temp = cfg.FONT.render(info_text, 0, (0, 255, 0), (0, 0, 1))
        
        # Отображаем обнаруженные препятствия
        screen.blit(obstacles, (0, 0))
        
        # Если нажата клавиша TAB, показываем дерево
        if show_tree:
            rrtstar.draw(screen)
        else:
            # Иначе только начальную и конечную точки и найденный путь
            pygame.draw.circle(screen, cfg.RED, (int(start.x), int(start.y)), 10)
            pygame.draw.circle(screen, cfg.GREEN, (int(goal.x), int(goal.y)), 10)
            
            if path:
                # Оптимизированная отрисовка пути - более толстые линии для лучшей видимости
                pygame.draw.lines(screen, cfg.PURPLE, False, path, 4)
                
                # Добавляем маркеры в каждой точке пути
                for point in path:
                    pygame.draw.circle(screen, cfg.PURPLE, (int(point[0]), int(point[1])), 3)
        
        # Отображаем подробную информацию, если включено
        if show_detailed_info and rrtstar.path_found:
            info_lines = [
                f"Всего узлов: {len(rrtstar.nodes)}",
                f"Длина пути: {len(path)} точек",
                f"Стоимость пути: {rrtstar.best_cost:.2f}",
                f"Первое решение на итерации: {rrtstar.solution_iter}",
                f"Улучшение: {(1 - rrtstar.best_cost / (rrtstar.solution_iter * 0.01)):.2f}%",
                f"Нажмите TAB для просмотра дерева",
                f"Нажмите R для перезапуска"
            ]
            
            y_offset = 50
            for line in info_lines:
                info_surf = cfg.FONT.render(line, 0, (255, 255, 0), (0, 0, 128))
                screen.blit(info_surf, (20, y_offset))
                y_offset += 30
        
        pygame.display.update()
    
    pygame.quit()


if __name__ == "__main__":
    main() 