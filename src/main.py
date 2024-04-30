from typing import Literal

import pygame
import numpy as np

from config import (
    window_size,
    grid_size,
    border_size,
    grid_color,
    snake_color,
    food_color,
    snake_head_color,
)


class GameState:
    def __init__(self, p_grid_size: tuple[int, int]):
        self.grid_size = np.array(p_grid_size, dtype=np.int16)
        self.snake = np.array([[0, 0], [0, 1]], dtype=np.int16)
        self.food_location = np.array([0, 0], dtype=np.int16)
        self.direction: Literal["up", "down", "left", "right"] = "right"
        self.win_state: Literal["pending", "win", "loose"] = "pending"
        self.update_food()

    def update_food(self):
        check = np.all(self.snake == self.food_location, axis=1)
        if np.any(check):
            self.food_location = np.random.randint(self.grid_size, dtype=np.int16)

    @property
    def direction_vector(self):
        match self.direction:
            case "up":
                return -1, 0
            case "down":
                return 1, 0
            case "left":
                return 0, -1
            case "right":
                return 0, 1

    def update(self):
        if self.win_state != "pending":
            return

        dir = np.array(self.direction_vector)
        next_head_pos = (self.snake[-1] + dir + self.grid_size) % self.grid_size
        check = np.all(self.snake == next_head_pos, axis=1)
        if np.any(check):
            self.win_state = "loose"
            return

        self.snake = np.append(self.snake, [next_head_pos], axis=0)

        if not np.array_equal(self.snake[-1], self.food_location):
            self.snake = np.delete(self.snake, 0, axis=0)

        if len(self.snake) == self.grid_size[0] * self.grid_size[1]:
            self.win_state = "win"
            return

        self.update_food()


class Renderer:
    def __init__(self, state: GameState):
        self.state = state

        ratio = min(*(np.array(window_size) / state.grid_size))
        real_size = state.grid_size * ratio

        self.cell_size = (
            real_size - border_size * (state.grid_size + np.ones((2,)))
        ) / state.grid_size
        self.offset = (np.array(window_size) - real_size) / 2

    def _offset_for(self, x: int, y: int):
        return (
            self.offset
            + (np.ones((2,)) * border_size)
            + np.array([x, y]) * (self.cell_size + np.ones((2,)) * border_size)
        )

    def _draw_square(self, surface: pygame.Surface, x: int, y: int, color):
        pos = self._offset_for(x, y)
        rect = (pos[0], pos[1], self.cell_size[0], self.cell_size[1])
        pygame.draw.rect(surface, color, rect)

    def draw(self, surface: pygame.Surface):
        surface.fill(pygame.Color("black"))
        for y, x in np.ndindex(*self.state.grid_size):
            self._draw_square(surface, x, y, grid_color)

        self._draw_square(
            surface,
            int(self.state.food_location[1]),
            int(self.state.food_location[0]),
            food_color,
        )

        start_color = np.array(snake_color)
        end_color = np.array(snake_head_color)
        diff = (end_color - start_color) / (len(self.state.snake) - 1)
        for idx, (y, x) in enumerate(self.state.snake):
            self._draw_square(surface, x, y, start_color + diff * idx)

        pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption("Snake")
    window_surface = pygame.display.set_mode(window_size)

    state = GameState(grid_size)
    renderer = Renderer(state)

    clock = pygame.time.Clock()
    is_running = True
    while is_running:
        did_change_direction = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.KEYDOWN and not did_change_direction:
                if event.key == pygame.K_LEFT and state.direction != "right":
                    state.direction = "left"
                    did_change_direction = True
                elif event.key == pygame.K_RIGHT and state.direction != "left":
                    state.direction = "right"
                    did_change_direction = True
                elif event.key == pygame.K_UP and state.direction != "down":
                    state.direction = "up"
                    did_change_direction = True
                elif event.key == pygame.K_DOWN and state.direction != "up":
                    state.direction = "down"
                    did_change_direction = True

        state.update()
        renderer.draw(window_surface)

        clock.tick(10)

    pygame.quit()


if __name__ == "__main__":
    main()
