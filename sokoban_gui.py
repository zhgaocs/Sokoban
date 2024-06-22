import pygame
import sys
import os


class Sokoban:
    def __init__(self, level):
        self.initial_level = [list(row) for row in level]
        self.reset()

    def reset(self):
        self.level = [row[:] for row in self.initial_level]
        self.rows = len(self.level)
        self.cols = len(self.level[0])
        self.player_pos = self.find_player()
        self.targets = self.find_targets()
        self.total_boxes = self.count_initial_boxes()
        self.tile_size = 50

    def find_player(self):
        for r, row in enumerate(self.level):
            for c, cell in enumerate(row):
                if cell == "P":
                    return (r, c)
        return None

    def find_targets(self):
        targets = []
        for r, row in enumerate(self.level):
            for c, cell in enumerate(row):
                if cell == "O" or cell == "X":
                    targets.append((r, c))
        return targets

    def count_initial_boxes(self):
        count = 0
        for row in self.level:
            count += row.count("#") + row.count("X")
        return count

    def is_game_won(self):
        current_x_count = sum(row.count("X") for row in self.level)
        return current_x_count == self.total_boxes

    def move(self, direction):
        dr, dc = 0, 0
        if direction == "W":
            dr = -1
        elif direction == "S":
            dr = 1
        elif direction == "A":
            dc = -1
        elif direction == "D":
            dc = 1
        else:
            return

        r, c = self.player_pos
        new_r, new_c = r + dr, c + dc
        beyond_r, beyond_c = new_r + dr, new_c + dc

        # player moves to empty space or goal
        if self.level[new_r][new_c] in (".", "O"):
            self.level[r][c] = "."  # leave the old position
            self.level[new_r][new_c] = "P"
            self.player_pos = (new_r, new_c)
        # player pushes box
        elif self.level[new_r][new_c] in ("#", "X"):
            if self.level[beyond_r][beyond_c] in (".", "O"):
                self.level[r][c] = "."  # leave the old position
                self.level[new_r][new_c] = "P"
                self.level[beyond_r][beyond_c] = "#"
                self.player_pos = (new_r, new_c)

        # Update target positions
        for tr, tc in self.targets:
            if self.level[tr][tc] == ".":
                self.level[tr][tc] = "O"
            elif self.level[tr][tc] == "#":
                self.level[tr][tc] = "X"

    def draw(self, screen):
        colors = {
            "*": (156, 102, 31),  # Wall
            ".": (192, 192, 192),  # Floor
            "O": (255, 255, 0),  # Target
            "P": (3, 168, 158),  # Player
            "#": (199, 97, 20),  # Box
            "X": (0, 255, 0),  # Box on Target
        }

        for r, row in enumerate(self.level):
            for c, cell in enumerate(row):
                color = colors.get(cell, (0, 0, 0))
                rect = pygame.Rect(
                    c * self.tile_size,
                    r * self.tile_size,
                    self.tile_size,
                    self.tile_size,
                )

                # Draw the base tile
                pygame.draw.rect(screen, colors["."], rect)

                if cell == "*":
                    # Draw wall
                    pygame.draw.rect(screen, color, rect)
                elif cell in ["#", "X"]:
                    # Draw box
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 6)  # Add border for box
                elif cell == "O":
                    # Draw target
                    pygame.draw.circle(screen, color, rect.center, self.tile_size // 4)
                elif cell == "P":
                    # Draw player
                    pygame.draw.circle(screen, color, rect.center, self.tile_size // 2)
                elif cell == "X":
                    # Draw box on target
                    pygame.draw.rect(screen, colors["#"], rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 3)  # Add border for box
                    pygame.draw.circle(
                        screen, colors["O"], rect.center, self.tile_size // 4
                    )


def load_level(filename):
    with open(filename, "r") as file:
        level = file.read().splitlines()
    return level


def draw_button(
    screen, text, rect, font, base_color=(255, 255, 255), hover_color=(100, 100, 100)
):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    color = hover_color if is_hovered else base_color
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    return is_hovered


def main_menu():
    pygame.init()
    levels_path = "levels"
    level_files = [f for f in os.listdir(levels_path) if f.endswith(".txt")]
    levels = [os.path.join(levels_path, f) for f in level_files]
    num_levels = len(levels)

    menu_width = 400
    menu_height = max(300, 100 + num_levels * 60)
    screen = pygame.display.set_mode((menu_width, menu_height))
    pygame.display.set_caption("Sokoban - Select Level")
    font = pygame.font.Font(None, 36)

    buttons = [pygame.Rect(150, 100 + i * 60, 100, 40) for i in range(num_levels)]

    while True:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    for i, button in enumerate(buttons):
                        if button.collidepoint(event.pos):
                            game_loop(levels[i])

        for i, level in enumerate(levels):
            draw_button(screen, f"Level {i + 1}", buttons[i], font)

        pygame.display.flip()


def game_loop(level_file):
    level = load_level(level_file)
    game = Sokoban(level)
    screen = pygame.display.set_mode(
        (game.cols * game.tile_size, game.rows * game.tile_size + 100)
    )
    pygame.display.set_caption("Sokoban")

    font = pygame.font.Font(None, 36)

    buttons = {
        "reset": pygame.Rect(50, game.rows * game.tile_size + 30, 100, 40),
        "menu": pygame.Rect(200, game.rows * game.tile_size + 30, 100, 40),
    }

    clock = pygame.time.Clock()

    while True:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if buttons["reset"].collidepoint(event.pos):
                        game.reset()
                    elif buttons["menu"].collidepoint(event.pos):
                        return

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    game.move("W")
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    game.move("S")
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    game.move("A")
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    game.move("D")

        game.draw(screen)

        for text, rect in buttons.items():
            draw_button(screen, text.capitalize(), rect, font)

        pygame.display.flip()

        if game.is_game_won():
            return

        clock.tick(60)


if __name__ == "__main__":
    main_menu()
