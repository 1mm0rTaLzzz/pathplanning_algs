import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import pygame
import sys
import math
import random
from matplotlib.patches import Circle
import os

# Константы для симуляции
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class FuzzyLogicRobot:
    def __init__(self):
        # Определение входных лингвистических переменных
        self.distance_left = ctrl.Antecedent(np.arange(0, 101, 1), 'distance_left')
        self.distance_front = ctrl.Antecedent(np.arange(0, 101, 1), 'distance_front')
        self.distance_right = ctrl.Antecedent(np.arange(0, 101, 1), 'distance_right')
        self.direction_to_target = ctrl.Antecedent(np.arange(-180, 181, 1), 'direction_to_target')

        # Определение выходных лингвистических переменных
        self.steering_angle = ctrl.Consequent(np.arange(-90, 91, 1), 'steering_angle')
        self.speed = ctrl.Consequent(np.arange(0, 101, 1), 'speed')

        # Определение функций принадлежности для расстояний
        self.distance_left['close'] = fuzz.trimf(self.distance_left.universe, [0, 0, 30])
        self.distance_left['medium'] = fuzz.trimf(self.distance_left.universe, [20, 50, 80])
        self.distance_left['far'] = fuzz.trimf(self.distance_left.universe, [70, 100, 100])

        self.distance_front['close'] = fuzz.trimf(self.distance_front.universe, [0, 0, 30])
        self.distance_front['medium'] = fuzz.trimf(self.distance_front.universe, [20, 50, 80])
        self.distance_front['far'] = fuzz.trimf(self.distance_front.universe, [70, 100, 100])

        self.distance_right['close'] = fuzz.trimf(self.distance_right.universe, [0, 0, 30])
        self.distance_right['medium'] = fuzz.trimf(self.distance_right.universe, [20, 50, 80])
        self.distance_right['far'] = fuzz.trimf(self.distance_right.universe, [70, 100, 100])

        # Определение функций принадлежности для направления на цель
        self.direction_to_target['far_left'] = fuzz.trimf(self.direction_to_target.universe, [-180, -180, -90])
        self.direction_to_target['left'] = fuzz.trimf(self.direction_to_target.universe, [-135, -45, 0])
        self.direction_to_target['straight'] = fuzz.trimf(self.direction_to_target.universe, [-30, 0, 30])
        self.direction_to_target['right'] = fuzz.trimf(self.direction_to_target.universe, [0, 45, 135])
        self.direction_to_target['far_right'] = fuzz.trimf(self.direction_to_target.universe, [90, 180, 180])

        # Определение функций принадлежности для угла поворота
        self.steering_angle['hard_left'] = fuzz.trimf(self.steering_angle.universe, [-90, -90, -45])
        self.steering_angle['left'] = fuzz.trimf(self.steering_angle.universe, [-60, -30, 0])
        self.steering_angle['straight'] = fuzz.trimf(self.steering_angle.universe, [-15, 0, 15])
        self.steering_angle['right'] = fuzz.trimf(self.steering_angle.universe, [0, 30, 60])
        self.steering_angle['hard_right'] = fuzz.trimf(self.steering_angle.universe, [45, 90, 90])

        # Определение функций принадлежности для скорости
        self.speed['slow'] = fuzz.trimf(self.speed.universe, [0, 0, 40])
        self.speed['medium'] = fuzz.trimf(self.speed.universe, [30, 50, 70])
        self.speed['fast'] = fuzz.trimf(self.speed.universe, [60, 100, 100])

        # Определение правил нечеткой логики
        self.create_fuzzy_rules()

        # Создание системы управления
        self.control_system = ctrl.ControlSystem(self.rules)
        self.control_simulation = ctrl.ControlSystemSimulation(self.control_system)

    def create_fuzzy_rules(self):
        self.rules = []

        # Правила для избегания препятствий (высший приоритет)
        # Если препятствие близко спереди, поворачиваем в сторону с большим расстоянием
        rule1 = ctrl.Rule(self.distance_front['close'] & self.distance_left['far'], self.steering_angle['hard_left'])
        rule2 = ctrl.Rule(self.distance_front['close'] & self.distance_right['far'], self.steering_angle['hard_right'])
        rule3 = ctrl.Rule(self.distance_front['close'] & self.distance_left['medium'] & self.distance_right['medium'], 
                        self.steering_angle['hard_left'])  # По умолчанию резко влево, если оба расстояния средние
        rule3a = ctrl.Rule(self.distance_front['close'] & self.distance_left['close'] & self.distance_right['close'], 
                        self.steering_angle['hard_right'])  # Экстренный разворот, если всё близко

        # Если препятствие близко слева, поворачиваем резко вправо
        rule4 = ctrl.Rule(self.distance_left['close'], self.steering_angle['hard_right'])

        # Если препятствие близко справа, поворачиваем резко влево
        rule5 = ctrl.Rule(self.distance_right['close'], self.steering_angle['hard_left'])

        # Правила для движения к цели (средний приоритет)
        rule6 = ctrl.Rule(self.distance_front['far'] & self.direction_to_target['straight'], self.steering_angle['straight'])
        rule7 = ctrl.Rule(self.distance_front['far'] & self.direction_to_target['left'], self.steering_angle['left'])
        rule8 = ctrl.Rule(self.distance_front['far'] & self.direction_to_target['far_left'], self.steering_angle['hard_left'])
        rule9 = ctrl.Rule(self.distance_front['far'] & self.direction_to_target['right'], self.steering_angle['right'])
        rule10 = ctrl.Rule(self.distance_front['far'] & self.direction_to_target['far_right'], self.steering_angle['hard_right'])

        # Правила для средней дистанции до препятствий
        rule14 = ctrl.Rule(self.distance_front['medium'] & self.direction_to_target['straight'], self.steering_angle['straight'])
        rule15 = ctrl.Rule(self.distance_front['medium'] & self.direction_to_target['left'], self.steering_angle['left'])
        rule16 = ctrl.Rule(self.distance_front['medium'] & self.direction_to_target['far_left'], self.steering_angle['hard_left'])
        rule17 = ctrl.Rule(self.distance_front['medium'] & self.direction_to_target['right'], self.steering_angle['right'])
        rule18 = ctrl.Rule(self.distance_front['medium'] & self.direction_to_target['far_right'], self.steering_angle['hard_right'])

        # Правила по умолчанию (низший приоритет)
        rule19 = ctrl.Rule(self.direction_to_target['straight'], self.steering_angle['straight'])
        rule20 = ctrl.Rule(self.direction_to_target['left'], self.steering_angle['left'])
        rule21 = ctrl.Rule(self.direction_to_target['right'], self.steering_angle['right'])
        rule22 = ctrl.Rule(self.direction_to_target['far_left'], self.steering_angle['hard_left'])
        rule23 = ctrl.Rule(self.direction_to_target['far_right'], self.steering_angle['hard_right'])

        # Правила для скорости
        rule11 = ctrl.Rule(self.distance_front['close'], self.speed['slow'])
        rule12 = ctrl.Rule(self.distance_front['medium'], self.speed['medium'])
        rule13 = ctrl.Rule(self.distance_front['far'], self.speed['fast'])

        self.rules = [rule1, rule2, rule3, rule3a, rule4, rule5, rule6, rule7, rule8, rule9, rule10, 
                     rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, 
                     rule21, rule22, rule23]

    def compute_control(self, distance_left, distance_front, distance_right, direction_to_target):
        # Устанавливаем входные значения
        self.control_simulation.input['distance_left'] = distance_left
        self.control_simulation.input['distance_front'] = distance_front
        self.control_simulation.input['distance_right'] = distance_right
        self.control_simulation.input['direction_to_target'] = direction_to_target

        # Вычисляем результат
        try:
            self.control_simulation.compute()
            steering = self.control_simulation.output['steering_angle']
            velocity = self.control_simulation.output['speed']
            return steering, velocity
        except Exception as e:
            print(f"Ошибка при вычислении нечеткой логики: {e}")
            # Используем более интеллектуальное резервное значение на основе направления к цели
            if direction_to_target > 30:
                return 20, 2.0  # Поворот вправо с низкой скоростью
            elif direction_to_target < -30:
                return -20, 2.0  # Поворот влево с низкой скоростью
            else:
                return 0, 5.0  # Прямо со средней скоростью

class Robot:
    def __init__(self, x, y, angle=0, radius=15):
        self.x = x
        self.y = y
        self.angle = angle  # угол в градусах
        self.radius = radius
        self.speed = 0
        self.sensor_range = 100  # дальность датчиков
        self.path = [(x, y)]  # список координат для отрисовки пути
        self.fuzzy_controller = FuzzyLogicRobot()
        self.stuck_counter = 0  # счетчик для определения, когда робот застрял
        self.last_positions = []  # список последних позиций для определения застревания
        self.obstacle_memory = []  # память о недавних препятствиях

    def move(self, obstacles, target):
        # Сохраняем текущую позицию для определения застревания
        self.last_positions.append((self.x, self.y))
        if len(self.last_positions) > 10:
            self.last_positions.pop(0)
        
        # Проверяем, не застрял ли робот
        is_stuck = self.check_if_stuck()
        
        # Проверка, не находится ли робот внутри какого-либо препятствия
        is_inside_obstacle = self.check_if_inside_obstacle(obstacles)
        if is_inside_obstacle:
            # Выталкиваем робота из препятствия
            self.escape_from_obstacle(obstacles)
            return
        
        # Проверка столкновений с препятствиями
        collision, collision_obs = self.check_collision(obstacles)
        if collision:
            # Добавляем препятствие в память
            if collision_obs:
                self.obstacle_memory.append((collision_obs[0], collision_obs[1]))
            
            # Останавливаем робота и заставляем его повернуть в противоположную сторону
            self.speed = 0
            # Разворот от 120 до 240 градусов (отворачиваем от препятствия)
            random_angle = random.randint(120, 240)
            self.angle = (self.angle + random_angle) % 360
            return

        # Вычисляем показания датчиков
        distances = self.get_sensor_readings(obstacles)
        
        # Если хоть один датчик показывает очень близкое препятствие, снижаем скорость
        if min(distances.values()) < 5:
            self.speed = 0
            return
        
        # Вычисляем направление на цель
        dx = target[0] - self.x
        dy = target[1] - self.y
        direction = math.degrees(math.atan2(dy, dx)) - self.angle
        
        # Нормализуем угол до диапазона -180..180
        direction = (direction + 180) % 360 - 180
        
        # Если робот застрял, добавляем небольшое случайное отклонение к направлению
        if self.stuck_counter > 0:
            direction += random.uniform(-45, 45)  # Увеличиваем случайность при застревании
            self.stuck_counter -= 1
        
        # Применяем дополнительное отклонение, чтобы избежать препятствий из памяти
        direction_adjustment = self.avoid_memorized_obstacles(direction)
        direction += direction_adjustment
        
        # Получаем управляющие воздействия от нечеткого контроллера
        steering, speed = self.fuzzy_controller.compute_control(
            distances['left'], distances['front'], distances['right'], direction)
        
        # Ограничиваем максимальное изменение угла поворота для более плавного движения
        max_steering_change = 15  # максимальное изменение за один шаг
        steering = max(-max_steering_change, min(max_steering_change, steering))
        
        # Если спереди очень близко препятствие, сильно уменьшаем скорость
        if distances['front'] < 20:
            speed = min(speed, 10)
        
        # Обновляем состояние робота
        self.angle += steering
        self.angle %= 360  # Нормализуем угол до диапазона 0..360
        self.speed = speed / 10  # Масштабируем скорость
        
        # Если робот застрял, увеличиваем скорость для выхода из тупика
        if self.stuck_counter > 0:
            self.speed = max(self.speed, 4.0)  # Увеличиваем ускорение при застревании
        
        # Перемещаем робота в соответствии с его углом и скоростью
        rad_angle = math.radians(self.angle)
        new_x = self.x + self.speed * math.cos(rad_angle)
        new_y = self.y + self.speed * math.sin(rad_angle)
        
        # Проверяем, не приведет ли перемещение к столкновению
        original_x, original_y = self.x, self.y
        self.x, self.y = new_x, new_y
        
        # Повторная проверка столкновений после перемещения
        collision, _ = self.check_collision(obstacles)
        if collision:
            # Возвращаем робота на прежнюю позицию
            self.x, self.y = original_x, original_y
            self.speed = 0
            # Поворачиваем сильнее при столкновении
            self.angle = (self.angle + 30 * random.choice([-1, 1])) % 360
            # Увеличиваем счетчик застревания
            self.stuck_counter += 5
        else:
            # Защита от выхода за границы
            self.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.x))
            self.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.y))
        
        # Добавляем текущую позицию в путь (только если робот действительно переместился)
        if (self.x, self.y) != self.path[-1]:
            self.path.append((self.x, self.y))
        
        # Очищаем память о препятствиях по мере движения
        if len(self.obstacle_memory) > 10:
            self.obstacle_memory.pop(0)

    def check_if_stuck(self):
        """Проверяет, не застрял ли робот на одном месте"""
        if len(self.last_positions) < 10:
            return False
        
        # Рассчитываем, насколько далеко продвинулся робот за последние 10 шагов
        start_x, start_y = self.last_positions[0]
        total_distance = 0
        for i in range(1, len(self.last_positions)):
            x, y = self.last_positions[i]
            prev_x, prev_y = self.last_positions[i-1]
            total_distance += math.sqrt((x - prev_x)**2 + (y - prev_y)**2)
        
        # Более низкий порог для определения застревания
        if total_distance < self.radius * 1.5:
            self.stuck_counter = 10  # Уменьшаем счетчик "застревания"
            return True
        return False

    def avoid_memorized_obstacles(self, direction_to_target):
        """Корректирует направление для избежания запомненных препятствий"""
        if not self.obstacle_memory:
            return 0
        
        adjustment = 0
        for obs_x, obs_y in self.obstacle_memory:
            # Вектор от робота к препятствию
            dx = obs_x - self.x
            dy = obs_y - self.y
            
            # Расстояние до препятствия
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Угол к препятствию относительно текущего направления робота
            obstacle_angle = math.degrees(math.atan2(dy, dx)) - self.angle
            obstacle_angle = (obstacle_angle + 180) % 360 - 180
            
            # Если препятствие близко и впереди, отклоняемся от него
            if distance < 100 and abs(obstacle_angle) < 90:
                # Чем ближе препятствие, тем сильнее отклонение
                strength = 30 * (1 - distance / 100)
                if obstacle_angle > 0:
                    adjustment -= strength  # Отклоняемся влево
                else:
                    adjustment += strength  # Отклоняемся вправо
        
        return adjustment

    def get_sensor_readings(self, obstacles):
        # Датчики: слева (-45°), спереди (0°), справа (45°)
        angles = [-45, 0, 45]
        readings = {'left': self.sensor_range, 'front': self.sensor_range, 'right': self.sensor_range}
        
        # Для каждого датчика
        for i, angle_offset in enumerate(['left', 'front', 'right']):
            sensor_angle = (self.angle + angles[i]) % 360
            rad_angle = math.radians(sensor_angle)
            
            # Для каждого препятствия проверяем пересечение с лучом датчика
            for obstacle in obstacles:
                # Вектор от робота к центру препятствия
                dx = obstacle[0] - self.x
                dy = obstacle[1] - self.y
                
                # Угол до препятствия
                obstacle_angle = math.degrees(math.atan2(dy, dx)) % 360
                
                # Расстояние до препятствия
                distance = math.sqrt(dx*dx + dy*dy) - obstacle[2] - self.radius
                
                # Расширяем зону видимости датчика до ±25° для лучшего обнаружения препятствий
                angle_diff = abs((obstacle_angle - sensor_angle + 180) % 360 - 180)
                
                if angle_diff <= 25 and distance < readings[angle_offset]:
                    readings[angle_offset] = max(0, distance)
        
        # Масштабируем до диапазона 0-100
        for key in readings:
            readings[key] = min(100, readings[key])
            
        return readings

    def reached_target(self, target, threshold=20):
        # Проверяем, достиг ли робот цели с заданной погрешностью
        dist = math.sqrt((self.x - target[0])**2 + (self.y - target[1])**2)
        return dist < threshold

    def check_collision(self, obstacles):
        """Проверяет столкновение робота с препятствиями с дополнительным запасом безопасности"""
        safety_margin = 5  # Увеличиваем запас безопасности для лучшего обнаружения
        
        for obs in obstacles:
            # Расстояние от центра робота до центра препятствия
            dist = math.sqrt((self.x - obs[0])**2 + (self.y - obs[1])**2)
            # Если расстояние меньше суммы радиусов + запас, считаем, что есть столкновение
            if dist < (self.radius + obs[2] + safety_margin):
                return True, obs  # Возвращаем также препятствие, с которым произошло столкновение
        return False, None

    def check_if_inside_obstacle(self, obstacles):
        """Проверяет, не находится ли робот внутри какого-либо препятствия"""
        for obs in obstacles:
            # Расстояние от центра робота до центра препятствия
            dist = math.sqrt((self.x - obs[0])**2 + (self.y - obs[1])**2)
            # Если расстояние меньше радиуса препятствия минус радиус робота, то робот внутри
            if dist < abs(obs[2] - self.radius) - 2:  # Допуск 2 пикселя
                return True
        return False

    def escape_from_obstacle(self, obstacles):
        """Помогает роботу выбраться из препятствия, если он оказался внутри"""
        # Находим ближайшее препятствие
        min_dist = float('inf')
        closest_obs = None
        
        for obs in obstacles:
            dist = math.sqrt((self.x - obs[0])**2 + (self.y - obs[1])**2)
            if dist < min_dist:
                min_dist = dist
                closest_obs = obs
        
        if closest_obs:
            # Вычисляем направление от центра препятствия к роботу
            dx = self.x - closest_obs[0]
            dy = self.y - closest_obs[1]
            
            # Если расстояние очень маленькое, добавим небольшое смещение, чтобы избежать деления на ноль
            if abs(dx) < 0.001 and abs(dy) < 0.001:
                dx = random.uniform(-1, 1)
                dy = random.uniform(-1, 1)
            
            # Нормализуем вектор
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx /= length
                dy /= length
            
            # "Выпрыгиваем" из препятствия, перемещаясь на границу препятствия + запас
            escape_distance = closest_obs[2] + self.radius + 5  # Радиус препятствия + радиус робота + запас
            self.x = closest_obs[0] + dx * escape_distance
            self.y = closest_obs[1] + dy * escape_distance
            
            # Защита от выхода за границы
            self.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.x))
            self.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.y))
            
            # Разворот от препятствия
            self.angle = math.degrees(math.atan2(dy, dx))
            
            # Добавляем препятствие в память
            self.obstacle_memory.append((closest_obs[0], closest_obs[1]))
            
            # Увеличиваем счетчик застревания
            self.stuck_counter = 15

class MovingObstacle:
    def __init__(self, x, y, radius, speed=None):
        self.x = x
        self.y = y
        self.radius = radius
        # Если скорость не задана, генерируем случайную скорость
        if speed is None:
            # Скорость от 0.5 до 2.0
            speed_value = random.uniform(0.5, 2.0)
            # Случайное направление в радианах
            angle = random.uniform(0, 2 * math.pi)
            self.vx = speed_value * math.cos(angle)
            self.vy = speed_value * math.sin(angle)
        else:
            self.vx, self.vy = speed
    
    def move(self, obstacles):
        # Сохраняем текущую позицию
        old_x, old_y = self.x, self.y
        
        # Обновляем позицию
        self.x += self.vx
        self.y += self.vy
        
        # Проверяем столкновение со стенами
        if self.x - self.radius < 0:  # Левая стена
            self.x = self.radius
            self.vx = -self.vx
        elif self.x + self.radius > WINDOW_WIDTH:  # Правая стена
            self.x = WINDOW_WIDTH - self.radius
            self.vx = -self.vx
        
        if self.y - self.radius < 0:  # Верхняя стена
            self.y = self.radius
            self.vy = -self.vy
        elif self.y + self.radius > WINDOW_HEIGHT:  # Нижняя стена
            self.y = WINDOW_HEIGHT - self.radius
            self.vy = -self.vy
        
        # Проверяем столкновения с другими препятствиями
        for obs in obstacles:
            if obs != self:  # Не проверяем столкновение с самим собой
                # Извлекаем координаты и радиус другого препятствия
                if isinstance(obs, MovingObstacle):
                    other_x, other_y, other_radius = obs.x, obs.y, obs.radius
                else:  # Если это кортеж (статическое препятствие)
                    other_x, other_y, other_radius = obs
                
                # Расстояние между препятствиями
                dx = self.x - other_x
                dy = self.y - other_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Если есть столкновение
                if distance < self.radius + other_radius:
                    # Возвращаемся на предыдущую позицию
                    self.x, self.y = old_x, old_y
                    
                    # Отражаем скорость (упрощенная модель)
                    if dx != 0 or dy != 0:  # Избегаем деления на ноль
                        # Нормализуем вектор направления отражения
                        norm = math.sqrt(dx*dx + dy*dy)
                        dx /= norm
                        dy /= norm
                        
                        # Проекция скорости на направление отражения
                        dot_product = self.vx * dx + self.vy * dy
                        
                        # Меняем составляющую скорости в направлении столкновения
                        self.vx -= 2 * dot_product * dx
                        self.vy -= 2 * dot_product * dy
                    else:
                        # Если вектор нулевой, просто инвертируем скорость
                        self.vx = -self.vx
                        self.vy = -self.vy
                    
                    # Добавляем немного случайности, чтобы избежать зацикливания
                    self.vx += random.uniform(-0.1, 0.1)
                    self.vy += random.uniform(-0.1, 0.1)
                    break
    
    def to_tuple(self):
        """Возвращает кортеж (x, y, radius) для совместимости"""
        return (self.x, self.y, self.radius)

def generate_obstacles(num_obstacles, min_radius=20, max_radius=40, moving_ratio=0.5):
    """Генерирует список препятствий, часть из которых движется"""
    obstacles = []
    
    # Определяем, сколько препятствий будут движущимися
    num_moving = int(num_obstacles * moving_ratio)
    
    for i in range(num_obstacles):
        valid = False
        while not valid:
            radius = random.randint(min_radius, max_radius)
            x = random.randint(radius, WINDOW_WIDTH - radius)
            y = random.randint(radius, WINDOW_HEIGHT - radius)
            
            # Проверяем, не перекрывается ли с существующими препятствиями
            valid = True
            for obs in obstacles:
                if isinstance(obs, MovingObstacle):
                    other_x, other_y, other_radius = obs.x, obs.y, obs.radius
                else:
                    other_x, other_y, other_radius = obs
                
                dist = math.sqrt((x - other_x)**2 + (y - other_y)**2)
                if dist < (radius + other_radius + 10):  # 10 - минимальное расстояние между препятствиями
                    valid = False
                    break
            
            # Также проверяем, не перекрывается ли со стартовой и целевой позицией
            start_pos = (50, 50)
            goal_pos = (WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50)
            
            start_dist = math.sqrt((x - start_pos[0])**2 + (y - start_pos[1])**2)
            goal_dist = math.sqrt((x - goal_pos[0])**2 + (y - goal_pos[1])**2)
            
            if start_dist < (radius + 30) or goal_dist < (radius + 30):
                valid = False
        
        # Создаем препятствие (движущееся или статическое)
        if i < num_moving:
            obstacles.append(MovingObstacle(x, y, radius))
        else:
            obstacles.append((x, y, radius))
    
    return obstacles

def main():
    # Инициализация pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Система планирования пути на основе нечеткой логики")
    clock = pygame.time.Clock()
    
    # Генерация препятствий (половина движущихся, половина статических)
    obstacles = generate_obstacles(10, moving_ratio=0.5)
    
    # Создание робота в начальной позиции
    robot = Robot(50, 50)
    
    # Целевая точка
    target = (WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50)
    
    # Цикл симуляции
    running = True
    simulation_done = False
    
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:  # Сброс симуляции
                    robot = Robot(50, 50)
                    obstacles = generate_obstacles(10, moving_ratio=0.5)
                    simulation_done = False
        
        # Обновление движущихся препятствий
        for i, obs in enumerate(obstacles):
            if isinstance(obs, MovingObstacle):
                obs.move([o for o in obstacles if o != obs])
        
        # Очистка экрана
        screen.fill(WHITE)
        
        # Отрисовка препятствий
        for obs in obstacles:
            if isinstance(obs, MovingObstacle):
                # Движущиеся препятствия рисуем другим цветом (оранжевым)
                pygame.draw.circle(screen, (255, 165, 0), (int(obs.x), int(obs.y)), obs.radius)
                # Добавляем линию направления движения
                end_x = obs.x + obs.radius * obs.vx
                end_y = obs.y + obs.radius * obs.vy
                pygame.draw.line(screen, BLACK, (int(obs.x), int(obs.y)), (int(end_x), int(end_y)), 2)
            else:
                # Статические препятствия - красные
                pygame.draw.circle(screen, RED, (int(obs[0]), int(obs[1])), obs[2])
        
        # Отрисовка цели
        pygame.draw.circle(screen, BLUE, (int(target[0]), int(target[1])), 10)
        
        # Отрисовка пути робота
        if len(robot.path) > 1:
            pygame.draw.lines(screen, GREEN, False, robot.path, 2)
        
        # Отрисовка датчиков робота
        angles = [-45, 0, 45]
        # Конвертируем препятствия в кортежи для сенсоров
        sensor_obstacles = [obs.to_tuple() if isinstance(obs, MovingObstacle) else obs for obs in obstacles]
        sensor_readings = robot.get_sensor_readings(sensor_obstacles)
        for i, angle_offset in enumerate(['left', 'front', 'right']):
            sensor_angle = (robot.angle + angles[i]) % 360
            rad_angle = math.radians(sensor_angle)
            end_x = robot.x + sensor_readings[angle_offset] * math.cos(rad_angle)
            end_y = robot.y + sensor_readings[angle_offset] * math.sin(rad_angle)
            pygame.draw.line(screen, YELLOW, (int(robot.x), int(robot.y)), (int(end_x), int(end_y)), 1)
        
        # Отрисовка робота
        pygame.draw.circle(screen, BLACK, (int(robot.x), int(robot.y)), robot.radius)
        # Линия-указатель направления
        end_x = robot.x + robot.radius * 1.5 * math.cos(math.radians(robot.angle))
        end_y = robot.y + robot.radius * 1.5 * math.sin(math.radians(robot.angle))
        pygame.draw.line(screen, BLACK, (int(robot.x), int(robot.y)), (int(end_x), int(end_y)), 3)
        
        # Движение робота, если симуляция не завершена
        if not simulation_done:
            # Конвертируем препятствия в кортежи для проверки столкновений
            move_obstacles = [obs.to_tuple() if isinstance(obs, MovingObstacle) else obs for obs in obstacles]
            robot.move(move_obstacles, target)
            if robot.reached_target(target):
                simulation_done = True
                print("Цель достигнута!")
        
        # Обновление экрана
        pygame.display.flip()
        clock.tick(FPS)
    
    # Визуализация нечеткой системы
    visualize_fuzzy_system(robot.fuzzy_controller)
    
    pygame.quit()
    sys.exit()

def visualize_fuzzy_system(fuzzy_controller):
    # Создаем директорию для сохранения графика, если она не существует
    if not os.path.exists('fuzzy_logic_pathplanning'):
        os.makedirs('fuzzy_logic_pathplanning')
    
    # Визуализация функций принадлежности
    plt.figure(figsize=(12, 8))
    
    # Используем fig, ax для избежания предупреждений о перекрывающихся осях
    fig, axes = plt.subplots(3, 2, figsize=(12, 8))
    
    # Первый график: расстояние спереди
    fuzzy_controller.distance_front.view(ax=axes[0, 0])
    axes[0, 0].set_title('Расстояние спереди')
    
    # Второй график: направление на цель
    fuzzy_controller.direction_to_target.view(ax=axes[0, 1])
    axes[0, 1].set_title('Направление на цель')
    
    # Третий график: расстояние слева
    fuzzy_controller.distance_left.view(ax=axes[1, 0])
    axes[1, 0].set_title('Расстояние слева')
    
    # Четвертый график: расстояние справа
    fuzzy_controller.distance_right.view(ax=axes[1, 1])
    axes[1, 1].set_title('Расстояние справа')
    
    # Пятый график: угол поворота
    fuzzy_controller.steering_angle.view(ax=axes[2, 0])
    axes[2, 0].set_title('Угол поворота')
    
    # Шестой график: скорость
    fuzzy_controller.speed.view(ax=axes[2, 1])
    axes[2, 1].set_title('Скорость')
    
    plt.tight_layout()
    
    # Сохраняем график с полным путем
    save_path = os.path.join('fuzzy_logic_pathplanning', 'membership_functions.png')
    plt.savefig(save_path)
    print(f"График сохранен в {save_path}")
    
    plt.show()

if __name__ == "__main__":
    main() 