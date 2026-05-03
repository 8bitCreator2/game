import random

from balance import auto_balance, simulate
from game import BattleGame, EncounterConfig


def test_battle_runs_and_has_winner_or_draw():
    game = BattleGame(rng=random.Random(1))
    result = game.run_battle()
    assert result["winner"] in {"Hero", "Bandit Captain", "draw"}
    assert result["turns"] > 0


def test_simulate_outputs_expected_metrics_shape():
    metrics = simulate(EncounterConfig(), battles=100)
    assert 0.0 <= metrics["win_rate"] <= 1.0
    assert metrics["avg_turns"] > 0


def test_auto_balance_moves_toward_target_window():
    config, metrics = auto_balance(target_win_rate=0.50, tolerance=0.08, max_iters=10)
    assert isinstance(config.enemy_hp, int)
    assert abs(metrics["win_rate"] - 0.50) <= 0.15
