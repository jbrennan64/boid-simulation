import pygame
import sys
import random
from constants import *
from boid import Boid
from ui import UI


def make_trail_surface(width, height, bg_color):
    surface = pygame.Surface((width, height))
    surface.fill(bg_color)
    return surface


def main():
    global WIDTH, HEIGHT
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Boid Simulation")
    clock = pygame.time.Clock()
    fullscreen = False

    ui = UI(WIDTH, HEIGHT)
    boids = [Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(DEFAULT_BOID_COUNT)]
    bg_color = ui.bg_color_picker.get_color()
    trail_surface = make_trail_surface(WIDTH, HEIGHT, bg_color)
    glow_surface  = pygame.Surface((WIDTH, HEIGHT))

    while True:
        bg_color = ui.bg_color_picker.get_color()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                trail_surface = make_trail_surface(WIDTH, HEIGHT, bg_color)
                glow_surface  = pygame.Surface((WIDTH, HEIGHT))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                WIDTH, HEIGHT = screen.get_size()
                trail_surface = make_trail_surface(WIDTH, HEIGHT, bg_color)
                glow_surface  = pygame.Surface((WIDTH, HEIGHT))
            ui.handle_event(event, WIDTH, HEIGHT)

        # sync boid properties from UI
        for boid in boids:
            boid.size      = ui.boid_size.value
            boid.max_speed = ui.speed.value
            boid.min_speed = ui.speed.value * ui.min_speed_mult.value
            boid.max_force = ui.max_force.value

        while len(boids) < int(ui.boid_count.value):
            boids.append(Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        while len(boids) > int(ui.boid_count.value):
            boids.pop()

        # --- trail surface: fade or clear, then blit as background ---
        if ui.trails_on.value:
            fade_alpha = max(4, int(210 - ui.trail_length.value * 2.0))
            fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade.fill((*bg_color, fade_alpha))
            trail_surface.blit(fade, (0, 0))
        else:
            trail_surface.fill(bg_color)
        screen.blit(trail_surface, (0, 0))

        # --- per-frame color settings ---
        speeds    = [b.velocity.length() for b in boids]
        speed_min = min(speeds) if speeds else 0.0
        speed_max = max(speeds) if speeds else 1.0

        color_settings = {
            'solid_color':          ui.solid_color_picker.get_color(),
            'slow_color':           ui.velocity_slow_picker.get_color(),
            'fast_color':           ui.velocity_fast_picker.get_color(),
            'low_color':            ui.density_low_picker.get_color(),
            'high_color':           ui.density_high_picker.get_color(),
            'cycle_speed':          ui.rainbow_speed.value,
            'saturation':           ui.rainbow_saturation.value,
            'brightness':           ui.rainbow_brightness.value,
            'speed_min':            speed_min,
            'speed_max':            speed_max,
            'velocity_sensitivity': ui.velocity_sensitivity.value,
            'density_sensitivity':  ui.density_sensitivity.value,
            'density_radius':       ui.density_radius.value,
        }

        # --- pass 1: update boids, compute colors, stamp trail dots ---
        boid_colors = []
        for boid in boids:
            boid.update(
                boids,
                ui.sep_perception.value,
                ui.ali_perception.value,
                ui.coh_perception.value,
                ui.sep_strength.value,
                ui.ali_strength.value,
                ui.coh_strength.value
            )
            boid.edges(WIDTH, HEIGHT)
            color = boid.get_color(ui.color_mode.selected, boids, color_settings)
            boid_colors.append(color)
            if ui.trails_on.value:
                pygame.draw.circle(
                    trail_surface, color,
                    (int(boid.position.x), int(boid.position.y)),
                    int(ui.trail_width.value)
                )

        # --- pass 2: glow with additive blending ---
        if ui.glow_on.value:
            glow_surface.fill((0, 0, 0))
            layers = int(ui.glow_intensity.value)
            spread = int(ui.glow_radius.value)
            for boid, color in zip(boids, boid_colors):
                px, py = int(boid.position.x), int(boid.position.y)
                r, g, b = color
                for i in range(layers, 0, -1):
                    glow_r = max(1, boid.size + spread * i // max(layers, 1))
                    # brightness increases toward center (i=1 is innermost)
                    intensity = 40 * (layers - i + 1) // max(layers, 1)
                    sc = (min(255, r * intensity // 255),
                          min(255, g * intensity // 255),
                          min(255, b * intensity // 255))
                    pygame.draw.circle(glow_surface, sc, (px, py), glow_r)
            screen.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # --- pass 3: solid boids ---
        for boid, color in zip(boids, boid_colors):
            boid.draw(screen, ui.shape.selected, color)

        ui.draw(screen, WIDTH, HEIGHT)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
