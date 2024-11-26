import pygame
import math
from typing import List, Tuple

pygame.init()

WIDTH, HEIGHT = 1200, 800
CELL_SIZE = 20

GRID_COLOR = (200, 200, 200)
AXIS_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)
POINT_COLOR_START = (255, 255, 0)
POINT_COLOR_END = (255, 255, 0)
LINE_COLOR = (0, 0, 255)
BACKGROUND = (245, 245, 245)

ALGORITHM_COLORS = {
    'dda': (0, 0, 255),
    'bresenham': (255, 0, 0),
    'circle': (0, 255, 0),
    'castle_pitway': (255, 105, 180),
    'wu': (0, 0, 0),
    'step': (255,255,0)
}


def lighten_color(color, factor=0.4):
        r, g, b = color
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        return (r, g, b)


class LineDrawerApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Алгоритмы растеризации")
        self.font = pygame.font.Font(None, 18)
        self.offset_x, self.offset_y = WIDTH // 2, HEIGHT // 2
        self.start_point = None
        self.end_point = None
        self.current_algorithm = "dda"
        self.buttons = [
            {'text': 'DDA', 'rect': pygame.Rect(10, 10, 100, 30), 'algorithm': 'dda'},
            {'text': 'Bresenham', 'rect': pygame.Rect(120, 10, 100, 30), 'algorithm': 'bresenham'},
            {'text': 'Circle', 'rect': pygame.Rect(230, 10, 100, 30), 'algorithm': 'circle'},
            {'text': 'Castle Pitway', 'rect': pygame.Rect(340, 10, 100, 30), 'algorithm': 'castle_pitway'},
            {'text': 'Wu', 'rect': pygame.Rect(450, 10, 100, 30), 'algorithm': 'wu'},
            {'text': 'Step', 'rect': pygame.Rect(560, 10, 100, 30), 'algorithm': 'step'},
            {'text': 'Clear', 'rect': pygame.Rect(670, 10, 100, 30), 'algorithm': 'clear'}
        ]
        self.lines = []

    def grid_to_screen(self, x: int, y: int) -> Tuple[int, int]:
        return x * CELL_SIZE + self.offset_x, self.offset_y - y * CELL_SIZE

    def screen_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        return (x - self.offset_x) // CELL_SIZE, (self.offset_y - y) // CELL_SIZE

    def draw_grid(self):
        self.screen.fill(BACKGROUND)

        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WIDTH, y))


        pygame.draw.line(self.screen, AXIS_COLOR, (self.offset_x, 0), (self.offset_x, HEIGHT), 2)
        pygame.draw.line(self.screen, AXIS_COLOR, (0, self.offset_y), (WIDTH, self.offset_y), 2)

        for i in range(-WIDTH // (2 * CELL_SIZE), WIDTH // (2 * CELL_SIZE) + 1):
            x = self.offset_x + i * CELL_SIZE
            if i != 0:
                text = self.font.render(str(i), True, TEXT_COLOR)
                self.screen.blit(text, (x - text.get_width() // 2, self.offset_y + 5))

        for i in range(-HEIGHT // (2 * CELL_SIZE), HEIGHT // (2 * CELL_SIZE) + 1):
            y = self.offset_y - i * CELL_SIZE
            if i != 0:
                text = self.font.render(str(i), True, TEXT_COLOR)
                self.screen.blit(text, (self.offset_x + 5, y - text.get_height() // 2))

    def draw_buttons(self):
        for button in self.buttons:
            button_color = ALGORITHM_COLORS.get(button['algorithm'], (200, 200, 200))

            if self.current_algorithm == button['algorithm']:
                color = button_color
            else:
                color = lighten_color(button_color, factor=0.6)

            pygame.draw.rect(self.screen, color, button['rect'])
            
            if button['algorithm'] == 'wu':
                text_color = (255, 255, 255)
            else:
                text_color = TEXT_COLOR
            
            text = self.font.render(button['text'], True, text_color)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)

    def draw_points(self):
        if self.start_point:
            x, y = self.grid_to_screen(*self.start_point)
            pygame.draw.rect(self.screen, POINT_COLOR_START, (x, y, CELL_SIZE, CELL_SIZE))
        if self.end_point:
            x, y = self.grid_to_screen(*self.end_point)
            pygame.draw.rect(self.screen, POINT_COLOR_END, (x, y, CELL_SIZE, CELL_SIZE))

    def draw_lines(self):
        for line in self.lines:
            algorithm = line['algorithm']
            line_color = ALGORITHM_COLORS.get(algorithm, LINE_COLOR)

            if algorithm == 'circle':
                x0, y0 = line['start']
                x1, y1 = line['end']
                points = self.bresenham_circle(x0, y0, x1, y1)
            elif algorithm == 'dda':
                points = self.dda_algorithm(*line['start'], *line['end'])
            elif algorithm == 'bresenham':
                points = self.bresenham_algorithm(*line['start'], *line['end'])
            elif algorithm == 'castle_pitway':
                points = self.castle_pitway_algorithm(*line['start'], *line['end'])
            elif algorithm == 'step':
                # Добавлен вызов step_algorithm
                points = self.step_algorithm(*line['start'], *line['end'])
            elif algorithm == 'wu':
                raw_points = self.wu_algorithm(*line['start'], *line['end'])
                for x, y, intensity in raw_points:
                    # Генерируем цвет: чем выше интенсивность, тем темнее
                    intensity_value = max(0, min(255, int(255 * (1 - intensity))))
                    color = (intensity_value, intensity_value, intensity_value)
                    screen_x, screen_y = self.grid_to_screen(x, y)
                    pygame.draw.rect(self.screen, color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
                continue

            # Обработка для всех остальных алгоритмов
            for x, y in points:
                screen_x, screen_y = self.grid_to_screen(x, y)
                pygame.draw.rect(self.screen, line_color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))

    

    def step_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        points = []
        
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy))
        
        x_inc, y_inc = dx / steps, dy / steps
        x, y = x0, y0

        for _ in range(steps + 1):
            points.append((round(x), round(y)))

            x += x_inc
            y += y_inc

        return points

    def dda_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        points = []
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy))
        x_inc, y_inc = dx / steps, dy / steps
        x, y = x0, y0

        for _ in range(steps + 1):
            points.append((round(x), round(y)))
            x += x_inc
            y += y_inc
        return points

    def bresenham_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        points = []
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx - dy

        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return points
    
    def bresenham_circle(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        r = int(math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2))
        
        points = []
        x, y = 0, r
        d = 3 - 2 * r
        while x <= y:
            points.extend([
                (x0 + x, y0 + y), (x0 - x, y0 + y), (x0 + x, y0 - y), (x0 - x, y0 - y),
                (x0 + y, y0 + x), (x0 - y, y0 + x), (x0 + y, y0 - x), (x0 - y, y0 - x)
            ])
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1
        return points

    def castle_pitway_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        derror = abs(dy / dx) if dx != 0 else 0
        error = 0
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                points.append((y, x))
            else:
                points.append((x, y))

            error += derror
            if error >= 0.5:
                y += 1 if y1 > y0 else -1
                error -= 1

        return points

    def wu_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        def ipart(x: float) -> int:
            return int(x)

        def fpart(x: float) -> float:
            return x - int(x)

        def rfpart(x: float) -> float:
            return 1 - fpart(x)

        points = []

        steep = abs(y1 - y0) > abs(x1 - x0)
        
        # Если линия крутая, меняем местами координаты
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        gradient = dy / dx if dx != 0 else 1

        # Фаза начальной точки
        x_end = round(x0)
        y_end = y0 + gradient * (x_end - x0)
        x_pixel_start = x_end
        y_pixel_start = ipart(y_end)

        intensity1 = rfpart(y_end)
        intensity2 = fpart(y_end)
        if intensity1 > 0:
            points.append((x_pixel_start, y_pixel_start, intensity1))
        if intensity2 > 0:
            points.append((x_pixel_start, y_pixel_start + 1, intensity2))

        intery = y_end + gradient

        for x in range(x_pixel_start + 1, round(x1) + 1):
            intensity1 = rfpart(intery)
            intensity2 = fpart(intery)
            if intensity1 > 0:
                points.append((x, ipart(intery), intensity1))
            if intensity2 > 0:
                points.append((x, ipart(intery) + 1, intensity2))
            intery += gradient

        x_end = round(x1)
        y_end = y1 + gradient * (x_end - x1)
        intensity1 = rfpart(y_end)
        intensity2 = fpart(y_end)
        if intensity1 > 0:
            points.append((x_end, ipart(y_end), intensity1))
        if intensity2 > 0:
            points.append((x_end, ipart(y_end) + 1, intensity2))

        # Если линия была крутой, меняем обратно местами координаты
        if steep:
            points = [(y, x, intensity) for (x, y, intensity) in points]

        return points

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for button in self.buttons:
                        if button['rect'].collidepoint(x, y):
                            if button['algorithm'] == 'clear':
                                self.start_point, self.end_point, self.lines = None, None, []
                            else:
                                self.current_algorithm = button['algorithm']
                            break
                    else:
                        grid_point = self.screen_to_grid(x, y)
                        if not self.start_point:
                            self.start_point = grid_point
                        elif not self.end_point:
                            self.end_point = grid_point
                            self.lines.append({'start': self.start_point, 'end': self.end_point, 'algorithm': self.current_algorithm})
                            self.start_point, self.end_point = None, None

            self.draw_grid()
            self.draw_buttons()
            self.draw_points()
            self.draw_lines()
            pygame.display.flip()

if __name__ == "__main__":
    LineDrawerApp().run()
