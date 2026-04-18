from __future__ import annotations

import pygame

from src.adapters.council.default_council import DefaultCouncilAdapter
from src.adapters.generation.random_world_generator import RandomWorldGeneratorAdapter
from src.adapters.simulation.default_rules import DefaultSimulationRulesAdapter
from src.application.use_cases import GameSessionService
from src.ui.hud import draw_hud
from src.ui.map_view import TILE, draw_map


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Penta Historia")
    font = pygame.font.SysFont("arial", 18)
    game_session = GameSessionService(
        world_generator=RandomWorldGeneratorAdapter(),
        simulation_rules=DefaultSimulationRulesAdapter(),
        council=DefaultCouncilAdapter(),
    )

    world = game_session.create_world()
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
                    world = game_session.regenerate_world(world)
                elif pygame.K_1 <= event.key <= pygame.K_5:
                    index = event.key - pygame.K_1
                    game_session.apply_player_choice(world, index)

        if accumulator >= 1.2:
            game_session.advance_world(world)
            accumulator = 0.0

        screen.fill((18, 20, 28))
        draw_map(screen, world)
        draw_hud(screen, world, font)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
