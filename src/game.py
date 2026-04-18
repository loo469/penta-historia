from __future__ import annotations

import pygame

from src.sim.climate import tick_climate
from src.sim.economy import tick_economy
from src.sim.intrigue import tick_intrigue
from src.sim.research import tick_research
from src.sim.war import tick_war
from src.ui.council import apply_suggestion, build_suggestions
from src.ui.hud import draw_hud
from src.ui.map_view import TILE, draw_map
from src.world.generator import generate_world


def advance_world(world) -> None:
    world.tick_count += 1
    tick_climate(world)
    tick_economy(world)
    tick_research(world)
    tick_intrigue(world)
    tick_war(world)
    world.suggestions = build_suggestions(world)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Penta Historia")
    font = pygame.font.SysFont("arial", 18)

    world = generate_world()
    world.suggestions = build_suggestions(world)
    screen = pygame.display.set_mode((world.width * TILE + 560, world.height * TILE))
    clock = pygame.time.Clock()
    accumulator = 0.0
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        accumulator += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    world = generate_world()
                    world.suggestions = build_suggestions(world)
                elif pygame.K_1 <= event.key <= pygame.K_5:
                    index = event.key - pygame.K_1
                    if index < len(world.suggestions):
                        apply_suggestion(world, world.suggestions[index].effect_key)

        if accumulator >= 1.2:
            advance_world(world)
            accumulator = 0.0

        screen.fill((18, 20, 28))
        draw_map(screen, world)
        draw_hud(screen, world, font)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
