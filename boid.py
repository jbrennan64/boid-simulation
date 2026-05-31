import pygame
import math
import random
from constants import *
import colorsys


def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


class Boid:
    def __init__(self, x, y, species="prey"):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.acceleration = pygame.Vector2(0, 0)
        self.species = species
        self.hue_offset = random.uniform(0, 1.0)
        self._density_tick = 0
        self.density_t = 0.0

        if species == "prey":
            self.max_speed = PREY_MAX_SPEED
            self.min_speed = PREY_MAX_SPEED * 0.6
            self.max_force = PREY_MAX_FORCE
            self.size = PREY_SIZE
            self.color = WHITE
            self.perception = PREY_PERCEPTION
        elif species == "predator":
            self.max_speed = PREDATOR_MAX_SPEED
            self.min_speed = PREDATOR_MAX_SPEED * 0.6
            self.max_force = PREDATOR_MAX_FORCE
            self.size = PREDATOR_SIZE
            self.color = RED
            self.perception = PREDATOR_PERCEPTION

    def get_color(self, mode, all_boids, color_settings):
        if mode == 0:
            solid = color_settings.get('solid_color')
            return solid if solid else self.color

        elif mode == 1:
            cycle_speed = color_settings.get('cycle_speed', 1.0)
            saturation  = color_settings.get('saturation', 1.0)
            brightness  = color_settings.get('brightness', 1.0)
            hue = (self.hue_offset + pygame.time.get_ticks() * 0.0005 * cycle_speed) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
            return (int(r * 255), int(g * 255), int(b * 255))

        elif mode == 2:
            speed_min = color_settings.get('speed_min', 0.0)
            speed_max = color_settings.get('speed_max', 1.0)
            speed_range = speed_max - speed_min
            t = (self.velocity.length() - speed_min) / speed_range if speed_range > 0 else 0.0
            sensitivity = color_settings.get('velocity_sensitivity', 1.0)
            t = max(0.0, min(1.0, t)) ** (1.0 / max(sensitivity, 0.01))
            c1 = color_settings.get('slow_color', (0, 0, 255))
            c2 = color_settings.get('fast_color', (255, 0, 0))
            return lerp_color(c1, c2, t)

        elif mode == 3:
            self._density_tick = (self._density_tick + 1) % 3
            if self._density_tick == 0:
                radius      = color_settings.get('density_radius', 80)
                sensitivity = color_settings.get('density_sensitivity', 4.0)
                count = sum(
                    1 for other in all_boids
                    if other is not self and self.position.distance_to(other.position) < radius
                )
                self.density_t = min(count / max(sensitivity, 0.01), 1.0)
            c1 = color_settings.get('low_color', (0, 0, 255))
            c2 = color_settings.get('high_color', (255, 100, 0))
            return lerp_color(c1, c2, self.density_t)

        return self.color

    def clamp_speed(self, vector, max_val):
        if vector.length() > max_val:
            vector = vector.normalize() * max_val
        return vector

    def update(self):
        self.velocity += self.acceleration
        self.velocity = self.clamp_speed(self.velocity, self.max_speed)
        if self.velocity.length() < self.min_speed:
            self.velocity = self.velocity.normalize() * self.min_speed
        self.position += self.velocity
        self.acceleration *= 0

    def edges(self, width, height):
        if self.position.x > width:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = width
        if self.position.y > height:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = height

    def draw(self, screen, shape=0, color=None):
        draw_color = color if color else self.color
        angle = math.atan2(self.velocity.y, self.velocity.x)

        if shape == 1:
            pygame.draw.circle(screen, draw_color, (int(self.position.x), int(self.position.y)), self.size)

        elif shape == 2:
            tip = pygame.Vector2(
                self.position.x + math.cos(angle) * self.size * 2,
                self.position.y + math.sin(angle) * self.size * 2
            )
            left = pygame.Vector2(
                self.position.x + math.cos(angle + 2.5) * self.size,
                self.position.y + math.sin(angle + 2.5) * self.size
            )
            right = pygame.Vector2(
                self.position.x + math.cos(angle - 2.5) * self.size,
                self.position.y + math.sin(angle - 2.5) * self.size
            )
            tail = pygame.Vector2(
                self.position.x - math.cos(angle) * self.size * 2,
                self.position.y - math.sin(angle) * self.size * 2
            )
            pygame.draw.polygon(screen, draw_color, [tip, left, right])
            pygame.draw.line(screen, draw_color, (int(self.position.x), int(self.position.y)), (int(tail.x), int(tail.y)), 1)

        else:
            tip = pygame.Vector2(
                self.position.x + math.cos(angle) * self.size * 2,
                self.position.y + math.sin(angle) * self.size * 2
            )
            left = pygame.Vector2(
                self.position.x + math.cos(angle + 2.5) * self.size,
                self.position.y + math.sin(angle + 2.5) * self.size
            )
            right = pygame.Vector2(
                self.position.x + math.cos(angle - 2.5) * self.size,
                self.position.y + math.sin(angle - 2.5) * self.size
            )
            pygame.draw.polygon(screen, draw_color, [tip, left, right])
