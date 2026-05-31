import pygame
import math
import colorsys
from constants import *

# UI colors
UI_BG = (15, 15, 15, 200)
UI_SECTION_BG = (30, 30, 30, 255)
UI_ACCENT = (100, 160, 255)
UI_TEXT = (220, 220, 220)
UI_MUTED = (120, 120, 120)
UI_TOGGLE_ON = (80, 200, 120)
UI_TOGGLE_OFF = (80, 80, 80)
UI_TAB_ACTIVE = (100, 160, 255)
UI_TAB_INACTIVE = (50, 50, 50)
PANEL_WIDTH = 260
TAB_HEIGHT = 36
SECTION_HEADER_HEIGHT = 32
ITEM_HEIGHT = 50
PADDING = 16


class Slider:
    def __init__(self, label, default, min_val, max_val, step=0.1):
        self.label = label
        self.value = default
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.dragging = False
        self.height = 4
        self.handle_radius = 6

    def handle_event(self, event, x, y, width, panel_x):
        mx, my = pygame.mouse.get_pos()
        lx = mx - panel_x
        handle_x = x + int((self.value - self.min_val) / (self.max_val - self.min_val) * width)
        handle_rect = pygame.Rect(handle_x - self.handle_radius, y - self.handle_radius,
                                  self.handle_radius * 2, self.handle_radius * 2)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handle_rect.collidepoint(lx, my):
                self.dragging = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        if event.type == pygame.MOUSEMOTION and self.dragging:
            ratio = max(0, min(1, (lx - x) / width))
            raw = self.min_val + ratio * (self.max_val - self.min_val)
            self.value = round(round(raw / self.step) * self.step, 2)

    def draw(self, surface, font, x, y, width):
        val_str = str(int(self.value)) if self.step >= 1 else str(self.value)
        surface.blit(font.render(f"{self.label}: {val_str}", True, UI_TEXT), (x, y - 18))
        pygame.draw.rect(surface, (60, 60, 60), (x, y - self.height // 2, width, self.height), border_radius=2)
        handle_x = x + int((self.value - self.min_val) / (self.max_val - self.min_val) * width)
        if handle_x > x:
            pygame.draw.rect(surface, UI_ACCENT, (x, y - self.height // 2, handle_x - x, self.height), border_radius=2)
        pygame.draw.circle(surface, UI_ACCENT, (handle_x, y), self.handle_radius)
        pygame.draw.circle(surface, UI_TEXT, (handle_x, y), self.handle_radius, 1)


class Toggle:
    def __init__(self, label, default=True):
        self.label = label
        self.value = default
        self.width = 36
        self.height = 18

    def handle_event(self, event, x, y, panel_x):
        mx, my = pygame.mouse.get_pos()
        lx = mx - panel_x
        # Full row is clickable, not just the toggle graphic
        rect = pygame.Rect(0, y - 15, PANEL_WIDTH - PADDING, 30)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(lx, my):
                self.value = not self.value

    def draw(self, surface, font, x, y):
        surface.blit(font.render(self.label, True, UI_TEXT), (x, y - 7))
        toggle_x = PANEL_WIDTH - PADDING * 2 - self.width
        color = UI_TOGGLE_ON if self.value else UI_TOGGLE_OFF
        rect = pygame.Rect(toggle_x, y - self.height // 2, self.width, self.height)
        pygame.draw.rect(surface, color, rect, border_radius=9)
        circle_x = toggle_x + self.width - 11 if self.value else toggle_x + 11
        pygame.draw.circle(surface, UI_TEXT, (circle_x, y), 7)


class Selector:
    def __init__(self, label, options, default=0):
        self.label = label
        self.options = options
        self.selected = default

    def handle_event(self, event, x, y, btn_width, panel_x):
        mx, my = pygame.mouse.get_pos()
        lx = mx - panel_x
        for i, option in enumerate(self.options):
            btn_rect = pygame.Rect(x + i * (btn_width + 4), y - 12, btn_width, 24)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(lx, my):
                    self.selected = i

    def draw(self, surface, font, x, y, btn_width):
        surface.blit(font.render(self.label, True, UI_TEXT), (x, y - 30))
        for i, option in enumerate(self.options):
            btn_rect = pygame.Rect(x + i * (btn_width + 4), y - 12, btn_width, 24)
            color = UI_TAB_ACTIVE if i == self.selected else UI_TAB_INACTIVE
            pygame.draw.rect(surface, color, btn_rect, border_radius=4)
            text_color = (255, 255, 255) if i == self.selected else UI_MUTED
            text_surf = font.render(option, True, text_color)
            surface.blit(text_surf, (
                btn_rect.x + (btn_width - text_surf.get_width()) // 2,
                btn_rect.y + (24 - text_surf.get_height()) // 2,
            ))


class ColorSwatch:
    """Small colored square in the panel. Click to open the HueWheelPopup."""
    HEIGHT_UNITS = 1
    SWATCH_SIZE = 24

    def __init__(self, label, default=(255, 255, 255)):
        self.label = label
        self._color = list(default)
        self.clicked = False  # UI reads and clears this to open the popup

    def get_color(self):
        return tuple(self._color)

    def set_color(self, color):
        self._color = list(color)

    def handle_event(self, event, x, y, panel_x):
        mx, my = pygame.mouse.get_pos()
        lx = mx - panel_x
        swatch_x = PANEL_WIDTH - PADDING * 2 - self.SWATCH_SIZE
        rect = pygame.Rect(swatch_x, y - self.SWATCH_SIZE // 2, self.SWATCH_SIZE, self.SWATCH_SIZE)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(lx, my):
                self.clicked = True

    def draw(self, surface, font, x, y):
        surface.blit(font.render(self.label, True, UI_TEXT), (x, y - 7))
        swatch_x = PANEL_WIDTH - PADDING * 2 - self.SWATCH_SIZE
        rect = pygame.Rect(swatch_x, y - self.SWATCH_SIZE // 2, self.SWATCH_SIZE, self.SWATCH_SIZE)
        pygame.draw.rect(surface, self.get_color(), rect, border_radius=3)
        pygame.draw.rect(surface, (180, 180, 180), rect, 1, border_radius=3)


class HueWheelPopup:
    """Full-screen overlay with a hue ring + saturation/value square."""
    WHEEL_RADIUS = 100
    RING_WIDTH   = 20
    SQ_SIZE      = 100   # fits inside inner ring radius=80 (corner dist ≈70.7)
    POPUP_W      = 260
    POPUP_H      = 316

    def __init__(self, initial_color, swatch):
        self.swatch = swatch
        r, g, b = (c / 255.0 for c in initial_color)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        self.hue        = h
        self.saturation = s
        self.value      = v
        self.confirmed  = False
        self._dragging  = None
        self._sv_dirty  = True
        self._sv_surf   = None
        self._wheel_surf = None
        self._build_wheel()

    # ------------------------------------------------------------------
    def _build_wheel(self):
        d = self.WHEEL_RADIUS * 2 + 4
        self._wheel_surf = pygame.Surface((d, d), pygame.SRCALPHA)
        self._wheel_surf.fill((0, 0, 0, 0))
        cx = cy = self.WHEEL_RADIUS + 2
        inner_r = self.WHEEL_RADIUS - self.RING_WIDTH
        for i in range(360):
            hue = i / 360.0
            rc, gc, bc = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = (int(rc * 255), int(gc * 255), int(bc * 255))
            a1 = math.radians(i)
            a2 = math.radians(i + 1.5)   # small overlap removes seams
            pts = [
                (cx + inner_r * math.cos(a1), cy + inner_r * math.sin(a1)),
                (cx + self.WHEEL_RADIUS * math.cos(a1), cy + self.WHEEL_RADIUS * math.sin(a1)),
                (cx + self.WHEEL_RADIUS * math.cos(a2), cy + self.WHEEL_RADIUS * math.sin(a2)),
                (cx + inner_r * math.cos(a2), cy + inner_r * math.sin(a2)),
            ]
            pygame.draw.polygon(self._wheel_surf, color, pts)

    def _build_sv_square(self):
        sq = self.SQ_SIZE
        self._sv_surf = pygame.Surface((sq, sq))
        for yi in range(sq):
            v = 1.0 - yi / sq
            for xi in range(sq):
                s = xi / sq
                rc, gc, bc = colorsys.hsv_to_rgb(self.hue, s, v)
                self._sv_surf.set_at((xi, yi), (int(rc * 255), int(gc * 255), int(bc * 255)))
        self._sv_dirty = False

    # ------------------------------------------------------------------
    def _layout(self, sw, sh):
        """Returns (popup_x, popup_y, ring_cx, ring_cy)."""
        px = (sw - self.POPUP_W) // 2
        py = (sh - self.POPUP_H) // 2
        cx = px + self.POPUP_W // 2
        cy = py + 16 + self.WHEEL_RADIUS
        return px, py, cx, cy

    def get_color(self):
        rc, gc, bc = colorsys.hsv_to_rgb(self.hue, self.saturation, self.value)
        return (int(rc * 255), int(gc * 255), int(bc * 255))

    # ------------------------------------------------------------------
    def handle_event(self, event, sw, sh):
        px, py, cx, cy = self._layout(sw, sh)
        mx, my = pygame.mouse.get_pos()
        inner_r = self.WHEEL_RADIUS - self.RING_WIDTH
        sq_x    = cx - self.SQ_SIZE // 2
        sq_y    = cy - self.SQ_SIZE // 2
        sq_rect = pygame.Rect(sq_x, sq_y, self.SQ_SIZE, self.SQ_SIZE)
        btn_rect = pygame.Rect(px + (self.POPUP_W - 100) // 2, py + self.POPUP_H - 52, 100, 36)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # confirm button
            if btn_rect.collidepoint(mx, my):
                self.swatch.set_color(self.get_color())
                self.confirmed = True
                return
            # click outside popup → dismiss and save
            if not pygame.Rect(px, py, self.POPUP_W, self.POPUP_H).collidepoint(mx, my):
                self.swatch.set_color(self.get_color())
                self.confirmed = True
                return
            # hue ring
            dx, dy = mx - cx, my - cy
            dist = math.hypot(dx, dy)
            if inner_r <= dist <= self.WHEEL_RADIUS:
                self.hue = math.atan2(dy, dx) / (2 * math.pi) % 1.0
                self._sv_dirty = True
                self._dragging = 'ring'
                self.swatch.set_color(self.get_color())
            # SV square
            elif sq_rect.collidepoint(mx, my):
                self.saturation = max(0.0, min(1.0, (mx - sq_x) / self.SQ_SIZE))
                self.value      = max(0.0, min(1.0, 1.0 - (my - sq_y) / self.SQ_SIZE))
                self._dragging  = 'sq'
                self.swatch.set_color(self.get_color())

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = None

        elif event.type == pygame.MOUSEMOTION:
            if self._dragging == 'ring':
                dx, dy = mx - cx, my - cy
                self.hue = math.atan2(dy, dx) / (2 * math.pi) % 1.0
                self._sv_dirty = True
                self.swatch.set_color(self.get_color())
            elif self._dragging == 'sq':
                self.saturation = max(0.0, min(1.0, (mx - sq_x) / self.SQ_SIZE))
                self.value      = max(0.0, min(1.0, 1.0 - (my - sq_y) / self.SQ_SIZE))
                self.swatch.set_color(self.get_color())

    def draw(self, screen, sw, sh, font):
        px, py, cx, cy = self._layout(sw, sh)

        # dim background
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # popup panel
        popup_rect = pygame.Rect(px, py, self.POPUP_W, self.POPUP_H)
        pygame.draw.rect(screen, (22, 22, 32), popup_rect, border_radius=10)
        pygame.draw.rect(screen, (70, 70, 100), popup_rect, 1, border_radius=10)

        # SV square (rebuild when hue changes)
        if self._sv_dirty:
            self._build_sv_square()
        sq_x = cx - self.SQ_SIZE // 2
        sq_y = cy - self.SQ_SIZE // 2
        screen.blit(self._sv_surf, (sq_x, sq_y))
        pygame.draw.rect(screen, (80, 80, 80), pygame.Rect(sq_x, sq_y, self.SQ_SIZE, self.SQ_SIZE), 1)

        # SV cursor
        cur_x = sq_x + int(self.saturation * self.SQ_SIZE)
        cur_y = sq_y + int((1.0 - self.value) * self.SQ_SIZE)
        pygame.draw.circle(screen, (0, 0, 0), (cur_x, cur_y), 6, 2)
        pygame.draw.circle(screen, (255, 255, 255), (cur_x, cur_y), 5, 1)

        # hue ring (transparent center reveals SV square)
        screen.blit(self._wheel_surf, (cx - self.WHEEL_RADIUS - 2, cy - self.WHEEL_RADIUS - 2))

        # hue cursor
        inner_r = self.WHEEL_RADIUS - self.RING_WIDTH
        mid_r   = (self.WHEEL_RADIUS + inner_r) // 2
        angle   = self.hue * 2 * math.pi
        hx = cx + int(math.cos(angle) * mid_r)
        hy = cy + int(math.sin(angle) * mid_r)
        pygame.draw.circle(screen, (0, 0, 0), (hx, hy), 8, 2)
        pygame.draw.circle(screen, (255, 255, 255), (hx, hy), 7, 1)

        # color preview strip
        preview_y = cy + self.WHEEL_RADIUS + 12
        preview_rect = pygame.Rect(px + 16, preview_y, self.POPUP_W - 32, 20)
        pygame.draw.rect(screen, self.get_color(), preview_rect, border_radius=3)
        pygame.draw.rect(screen, UI_MUTED, preview_rect, 1, border_radius=3)

        # confirm button
        btn_rect = pygame.Rect(px + (self.POPUP_W - 100) // 2, py + self.POPUP_H - 52, 100, 36)
        pygame.draw.rect(screen, (40, 100, 60), btn_rect, border_radius=6)
        pygame.draw.rect(screen, (80, 180, 110), btn_rect, 1, border_radius=6)
        btn_txt = font.render("Confirm", True, (220, 220, 220))
        screen.blit(btn_txt, (
            btn_rect.x + (btn_rect.w - btn_txt.get_width()) // 2,
            btn_rect.y + (btn_rect.h - btn_txt.get_height()) // 2,
        ))


class Section:
    def __init__(self, title, items):
        self.title = title
        self.items = items
        self.collapsed = False

    def toggle(self):
        self.collapsed = not self.collapsed

    def get_height(self):
        if self.collapsed:
            return SECTION_HEADER_HEIGHT
        units = sum(getattr(item, 'HEIGHT_UNITS', 1)
                    for item in self.items if getattr(item, 'visible', True))
        return SECTION_HEADER_HEIGHT + units * ITEM_HEIGHT + PADDING


class UI:
    def __init__(self, screen_width, screen_height):
        self.panel_width      = PANEL_WIDTH
        self.collapsed        = False
        self.active_tab       = 0
        self.collapse_btn_size = 20
        self.scroll_y         = 0
        self.active_popup     = None   # HueWheelPopup or None

        self.font_title = pygame.font.SysFont("segoeui", 12, bold=True)
        self.font_label = pygame.font.SysFont("segoeui", 11)

        # --- Simulation tab ---
        self.boid_count = Slider("Boid count", DEFAULT_BOID_COUNT, 5, 300, 1)
        self.speed      = Slider("Speed",      DEFAULT_SPEED,      0.5, 15, 0.1)
        self.boid_size  = Slider("Size",       DEFAULT_SIZE,       1, 30, 1)
        self.shape      = Selector("Shape", ["Triangle", "Dot", "Arrow"])
        self.mode_3d    = Toggle("3D mode (soon)", False)

        self.sep_strength = Slider("Separation", 1.0, 0.0, 3.0, 0.1)
        self.ali_strength = Slider("Alignment",  1.0, 0.0, 3.0, 0.1)
        self.coh_strength = Slider("Cohesion",   1.0, 0.0, 3.0, 0.1)
        self.perception   = Slider("Perception", 60,  10,  200, 1)

        # --- Visual tab: color mode ---
        self.color_mode = Selector("Color mode", ["Solid", "Rainbow", "Velocity", "Density"])

        # Solid
        self.solid_color_picker = ColorSwatch("Boid color", (255, 255, 255))
        self.solid_color_picker.visible = True

        # Rainbow
        self.rainbow_speed      = Slider("Cycle speed",  1.0, 0.1, 5.0,  0.1)
        self.rainbow_saturation = Slider("Saturation",   1.0, 0.0, 1.0,  0.05)
        self.rainbow_brightness = Slider("Brightness",   1.0, 0.0, 1.0,  0.05)
        self.rainbow_speed.visible = self.rainbow_saturation.visible = self.rainbow_brightness.visible = False

        # Velocity
        self.velocity_slow_picker = ColorSwatch("Slow color", (0,   80,  255))
        self.velocity_fast_picker = ColorSwatch("Fast color", (220, 60,  60))
        self.velocity_sensitivity = Slider("Sensitivity", 1.0, 0.1, 3.0, 0.1)
        self.velocity_slow_picker.visible = self.velocity_fast_picker.visible = self.velocity_sensitivity.visible = False

        # Density
        self.density_low_picker  = ColorSwatch("Low density",  (0,   80, 255))
        self.density_high_picker = ColorSwatch("High density", (255, 120,  0))
        self.density_sensitivity = Slider("Sensitivity", 4.0, 1.0, 10.0, 0.5)
        self.density_radius      = Slider("Radius",      80,  20,  200,  1)
        self.density_low_picker.visible = self.density_high_picker.visible = False
        self.density_sensitivity.visible = self.density_radius.visible = False

        # --- Background ---
        self.bg_color_picker = ColorSwatch("Background color", (0, 0, 0))

        # --- Trails ---
        self.trails_on    = Toggle("Trails", True)
        self.trail_width  = Slider("Trail width",  DEFAULT_TRAIL_WIDTH,  1, 6,   1)
        self.trail_length = Slider("Trail length", DEFAULT_TRAIL_LENGTH, 5, 100, 1)

        # --- Glow ---
        self.glow_on        = Toggle("Glow", False)
        self.glow_intensity = Slider("Glow layers", 3, 1, 10, 1)
        self.glow_radius    = Slider("Glow spread", 8, 2, 30, 1)

        self.sim_sections = [
            Section("Boids",    [self.boid_count, self.speed, self.boid_size, self.shape, self.mode_3d]),
            Section("Behavior", [self.sep_strength, self.ali_strength, self.coh_strength, self.perception]),
        ]
        self.vis_sections = [
            Section("Color", [
                self.color_mode,
                self.solid_color_picker,
                self.rainbow_speed, self.rainbow_saturation, self.rainbow_brightness,
                self.velocity_slow_picker, self.velocity_fast_picker, self.velocity_sensitivity,
                self.density_low_picker, self.density_high_picker,
                self.density_sensitivity, self.density_radius,
            ]),
            Section("Background", [self.bg_color_picker]),
            Section("Trails",     [self.trails_on, self.trail_width, self.trail_length]),
            Section("Glow",       [self.glow_on, self.glow_intensity, self.glow_radius]),
        ]

    # ------------------------------------------------------------------
    def _update_visibility(self):
        mode = self.color_mode.selected
        self.solid_color_picker.visible    = (mode == 0)
        self.rainbow_speed.visible         = (mode == 1)
        self.rainbow_saturation.visible    = (mode == 1)
        self.rainbow_brightness.visible    = (mode == 1)
        self.velocity_slow_picker.visible  = (mode == 2)
        self.velocity_fast_picker.visible  = (mode == 2)
        self.velocity_sensitivity.visible  = (mode == 2)
        self.density_low_picker.visible    = (mode == 3)
        self.density_high_picker.visible   = (mode == 3)
        self.density_sensitivity.visible   = (mode == 3)
        self.density_radius.visible        = (mode == 3)

    def get_sections(self):
        return self.sim_sections if self.active_tab == 0 else self.vis_sections

    # ------------------------------------------------------------------
    def handle_event(self, event, screen_width, screen_height):
        # Popup captures all events while open
        if self.active_popup is not None:
            self.active_popup.handle_event(event, screen_width, screen_height)
            if self.active_popup.confirmed:
                self.active_popup = None
            return

        self._update_visibility()
        mx, my = pygame.mouse.get_pos()
        panel_x = screen_width - self.panel_width

        btn_x = (panel_x - self.collapse_btn_size - 4
                 if not self.collapsed else screen_width - self.collapse_btn_size - 8)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(btn_x, 10, self.collapse_btn_size, self.collapse_btn_size).collidepoint(mx, my):
                self.collapsed = not self.collapsed
                return

        if self.collapsed:
            return

        lx = mx - panel_x
        ly = my

        # tab clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if 0 <= ly <= TAB_HEIGHT:
                if 0 <= lx <= self.panel_width // 2:
                    self.active_tab = 0
                elif self.panel_width // 2 <= lx <= self.panel_width:
                    self.active_tab = 1

        # scroll
        if event.type == pygame.MOUSEWHEEL:
            if panel_x <= mx <= screen_width:
                self.scroll_y = max(0, self.scroll_y - event.y * 20)

        # sections
        y = TAB_HEIGHT - self.scroll_y
        for section in self.get_sections():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(0, y, self.panel_width, SECTION_HEADER_HEIGHT).collidepoint(lx, ly):
                    section.toggle()
                    return

            y += SECTION_HEADER_HEIGHT
            if not section.collapsed:
                item_y = y + PADDING
                item_x = PADDING
                item_width = self.panel_width - PADDING * 2
                for item in section.items:
                    if not getattr(item, 'visible', True):
                        continue
                    if isinstance(item, ColorSwatch):
                        item.handle_event(event, item_x, item_y + 20, panel_x)
                        if item.clicked:
                            item.clicked = False
                            self.active_popup = HueWheelPopup(item.get_color(), item)
                    elif isinstance(item, Slider):
                        item.handle_event(event, item_x, item_y + 28, item_width, panel_x)
                    elif isinstance(item, Toggle):
                        item.handle_event(event, item_x, item_y + 9, panel_x)
                    elif isinstance(item, Selector):
                        btn_w = max(40, item_width // len(item.options) - 4)
                        item.handle_event(event, item_x, item_y + 30, btn_w, panel_x)
                    item_y += ITEM_HEIGHT * getattr(item, 'HEIGHT_UNITS', 1)
                y += sum(ITEM_HEIGHT * getattr(item, 'HEIGHT_UNITS', 1)
                         for item in section.items if getattr(item, 'visible', True)) + PADDING

    # ------------------------------------------------------------------
    def draw(self, screen, screen_width, screen_height):
        self._update_visibility()
        if self.collapsed:
            self._draw_collapse_btn(screen, screen_width - self.collapse_btn_size - 8, 10, ">")
            # Still draw popup if open (e.g. collapsed while popup was open)
            if self.active_popup is not None:
                self.active_popup.draw(screen, screen_width, screen_height, self.font_label)
            return

        panel_x = screen_width - self.panel_width
        surface = pygame.Surface((self.panel_width, screen_height), pygame.SRCALPHA)
        surface.fill(UI_BG)

        # tabs
        tab_w = self.panel_width // 2
        for i, name in enumerate(["Simulation", "Visual"]):
            color = UI_TAB_ACTIVE if i == self.active_tab else UI_TAB_INACTIVE
            pygame.draw.rect(surface, color, (i * tab_w, 0, tab_w, TAB_HEIGHT))
            txt = self.font_title.render(name, True, UI_TEXT)
            surface.blit(txt, (i * tab_w + (tab_w - txt.get_width()) // 2,
                                (TAB_HEIGHT - txt.get_height()) // 2))

        # sections
        y = TAB_HEIGHT - self.scroll_y
        for section in self.get_sections():
            pygame.draw.rect(surface, UI_SECTION_BG, (0, y, self.panel_width, SECTION_HEADER_HEIGHT))
            arrow = "▾" if not section.collapsed else "▸"
            surface.blit(
                self.font_title.render(f"{arrow}  {section.title.upper()}", True, UI_ACCENT),
                (PADDING, y + 8),
            )
            y += SECTION_HEADER_HEIGHT

            if not section.collapsed:
                item_y = y + PADDING
                item_x = PADDING
                item_width = self.panel_width - PADDING * 2
                for item in section.items:
                    if not getattr(item, 'visible', True):
                        continue
                    if isinstance(item, ColorSwatch):
                        item.draw(surface, self.font_label, item_x, item_y + 20)
                    elif isinstance(item, Slider):
                        item.draw(surface, self.font_label, item_x, item_y + 28, item_width)
                    elif isinstance(item, Toggle):
                        item.draw(surface, self.font_label, item_x, item_y + 9)
                    elif isinstance(item, Selector):
                        btn_w = max(40, item_width // len(item.options) - 4)
                        item.draw(surface, self.font_label, item_x, item_y + 30, btn_w)
                    item_y += ITEM_HEIGHT * getattr(item, 'HEIGHT_UNITS', 1)
                y += sum(ITEM_HEIGHT * getattr(item, 'HEIGHT_UNITS', 1)
                         for item in section.items if getattr(item, 'visible', True)) + PADDING

        screen.blit(surface, (panel_x, 0))
        self._draw_collapse_btn(screen, panel_x - self.collapse_btn_size - 4, 10, "<")

        # Popup drawn on top of everything
        if self.active_popup is not None:
            self.active_popup.draw(screen, screen_width, screen_height, self.font_label)

    def _draw_collapse_btn(self, screen, x, y, symbol):
        rect = pygame.Rect(x, y, self.collapse_btn_size, self.collapse_btn_size)
        pygame.draw.rect(screen, (40, 40, 40), rect, border_radius=4)
        pygame.draw.rect(screen, (100, 100, 100), rect, 1, border_radius=4)
        font = pygame.font.SysFont("segoeui", 12)
        label = font.render(symbol, True, UI_TEXT)
        screen.blit(label, (x + 5, y + 3))
