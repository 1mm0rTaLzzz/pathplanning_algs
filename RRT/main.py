import pygame
import random
import math
import time

import collision
import config as cfg



# Define Node class
class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None


# Define RRT class
class RRT:
    def __init__(self, start, goal, obstacles):
        self.start = start
        self.goal = goal
        self.obstacles = obstacles
        self.nodes = [start]
        self.step_size = 20
        self.final_step = 50

    def find_path(self):
        for i in range(10000):
            rand_node = Node(random.randint(0, cfg.WIDTH), random.randint(0, cfg.HEIGHT))
            nearest_node = self.nodes[0]
            for node in self.nodes:
                if math.sqrt((rand_node.x - node.x) ** 2 + (rand_node.y - node.y) ** 2) < math.sqrt(
                        (rand_node.x - nearest_node.x) ** 2 + (rand_node.y - nearest_node.y) ** 2):
                    nearest_node = node

            new_node = Node(nearest_node.x + self.step_size * (rand_node.x - nearest_node.x) / math.sqrt(
                (rand_node.x - nearest_node.x) ** 2 + (rand_node.y - nearest_node.y) ** 2),
                            nearest_node.y + self.step_size * (rand_node.y - nearest_node.y) / math.sqrt(
                                (rand_node.x - nearest_node.x) ** 2 + (rand_node.y - nearest_node.y) ** 2))
            if not collision.collision(nearest_node, new_node, self.obstacles):
                new_node.parent = nearest_node
                self.nodes.append(new_node)
                print(f"Random node position: ({rand_node.x}, {rand_node.y})")
                print(f"Nearest node position: ({nearest_node.x}, {nearest_node.y})")
                print(f"New node position: ({new_node.x}, {new_node.y})")
            final_node = Node(self.goal.x, self.goal.y)
            if math.sqrt((new_node.x - self.goal.x) ** 2 + (
                    new_node.y - self.goal.y) ** 2) < self.final_step and not collision.collision(new_node, final_node,
                                                                                             self.obstacles):
                    final_node.parent = new_node
                    self.nodes.append(final_node)
                    path = [final_node]
                    while path[-1].parent is not None:
                        path.append(path[-1].parent)
                    return [(node.x, node.y) for node in path[::-1]]
        return None

    def draw(self, screen):
        for node in self.nodes:
            pygame.draw.circle(screen, cfg.YELLOW, (node.x, node.y), 3)
            if node.parent is not None:
                pygame.draw.line(screen, cfg.WHITE, (node.x, node.y), (node.parent.x, node.parent.y), 2)
        pygame.draw.circle(screen, cfg.RED, (self.start.x, self.start.y), 10)
        pygame.draw.circle(screen, cfg.GREEN, (self.goal.x, self.goal.y), 10)




# Define function to create obstacles
def create_obstacles():
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


# Define function to get the start and end points from user
def get_start_end_points():
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


pygame.init()

screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
pygame.display.set_caption("Rapidly-exploring Random Tree")

infoSurface = pygame.Surface((cfg.WIDTH, cfg.HEIGHT))
infoSurface.set_colorkey((0, 0, 0))
start, goal = get_start_end_points()
obstacles = create_obstacles()
rrt = RRT(start, goal, obstacles)
startTime = time.perf_counter()
path = rrt.find_path()
elapsed = time.perf_counter() - startTime
elapsed = format(elapsed, '.4f')
temp = cfg.FONT.render(f'Nodes: {len(rrt.nodes)} Time:{elapsed}s', 0, (0, 255, 0), (0, 0, 1))

running = True
while running:
    screen.blit(infoSurface, (0, 0))
    infoSurface.blit(temp, (cfg.WIDTH - temp.get_width(), cfg.FONT.get_height()))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:

                rrt.draw(screen)

                if path is not None:
                    pygame.draw.lines(screen, cfg.BLUE, False, path, 3)

                temp = cfg.FONT.render(f'{len(rrt.nodes)}', 0, (255, 255, 0), (0, 0, 1))

                pygame.display.update()

pygame.quit()
