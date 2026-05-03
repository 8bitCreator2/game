from __future__ import annotations

import random
from dataclasses import replace

from game import BattleGame, EncounterConfig


def simulate(config: EncounterConfig, battles: int = 1000, seed: int = 7) -> dict[str, float]:
    wins = 0
    turns_total = 0
    player_hp_total = 0

    for i in range(battles):
        rng = random.Random(seed + i)
        game = BattleGame(rng=rng, config=config)
        result = game.run_battle()
        if result["winner"] == "Hero":
            wins += 1
        turns_total += int(result["turns"])
        player_hp_total += int(result["player_hp"])

    return {
        "win_rate": wins / battles,
        "avg_turns": turns_total / battles,
        "avg_player_hp": player_hp_total / battles,
    }


def auto_balance(
    start: EncounterConfig | None = None,
    target_win_rate: float = 0.52,
    tolerance: float = 0.03,
    max_iters: int = 12,
) -> tuple[EncounterConfig, dict[str, float]]:
    config = start or EncounterConfig()

    for _ in range(max_iters):
        metrics = simulate(config)
        delta = metrics["win_rate"] - target_win_rate
        if abs(delta) <= tolerance:
            return config, metrics

        # If player wins too much, increase enemy power. Otherwise reduce it.
        if delta > 0:
            hp_shift = max(2, int(10 * delta))
            atk_shift = max(1, int(4 * delta))
            config = replace(
                config,
                enemy_hp=max(20, config.enemy_hp + hp_shift),
                enemy_attack=max(3, config.enemy_attack + atk_shift),
                enemy_defense=max(0, min(8, config.enemy_defense + 1)),
            )
        else:
            hp_shift = max(2, int(10 * abs(delta)))
            atk_shift = max(1, int(4 * abs(delta)))
            config = replace(
                config,
                enemy_hp=max(20, config.enemy_hp - hp_shift),
                enemy_attack=max(3, config.enemy_attack - atk_shift),
                enemy_defense=max(0, config.enemy_defense - 1 if config.enemy_defense > 0 else 0),
            )

    return config, simulate(config)


if __name__ == "__main__":
    balanced, metrics = auto_balance()
    print("Balanced EncounterConfig:", balanced)
    print("Metrics:", metrics)
