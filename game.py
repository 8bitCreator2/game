from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple


class Action(str, Enum):
    ATTACK = "attack"
    POWER_ATTACK = "power_attack"
    HEAL = "heal"
    GUARD = "guard"


@dataclass
class Stats:
    hp: int
    attack: int
    defense: int
    crit_chance: float = 0.1
    crit_multiplier: float = 1.5


@dataclass
class Combatant:
    name: str
    base: Stats
    max_hp: int = field(init=False)
    hp: int = field(init=False)
    level: int = 1
    xp: int = 0
    potions: int = 2

    def __post_init__(self) -> None:
        self.max_hp = self.base.hp
        self.hp = self.base.hp

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def gain_xp(self, amount: int) -> None:
        self.xp += amount
        while self.xp >= self.level * 20:
            self.xp -= self.level * 20
            self.level += 1
            self.max_hp += 8
            self.base.attack += 2
            self.base.defense += 1
            self.hp = self.max_hp


@dataclass
class EncounterConfig:
    enemy_hp: int = 38
    enemy_attack: int = 8
    enemy_defense: int = 2
    enemy_crit_chance: float = 0.08
    enemy_crit_multiplier: float = 1.4


@dataclass
class TurnLog:
    actor: str
    action: str
    amount: int
    detail: str


class BattleGame:
    """A compact RPG-style battle game with simulation-friendly APIs."""

    def __init__(self, rng: random.Random | None = None, config: EncounterConfig | None = None):
        self.rng = rng or random.Random()
        self.config = config or EncounterConfig()

    def create_player(self) -> Combatant:
        return Combatant("Hero", Stats(hp=54, attack=10, defense=3, crit_chance=0.14, crit_multiplier=1.7))

    def create_enemy(self) -> Combatant:
        c = self.config
        return Combatant(
            "Bandit Captain",
            Stats(
                hp=c.enemy_hp,
                attack=c.enemy_attack,
                defense=c.enemy_defense,
                crit_chance=c.enemy_crit_chance,
                crit_multiplier=c.enemy_crit_multiplier,
            ),
        )

    def _roll_damage(self, attacker: Combatant, defender: Combatant, power: float = 1.0, guarded: bool = False) -> Tuple[int, bool]:
        swing = self.rng.uniform(0.85, 1.15)
        raw = int((attacker.base.attack * power) * swing)
        damage = max(1, raw - defender.base.defense)
        crit = self.rng.random() < attacker.base.crit_chance
        if crit:
            damage = int(damage * attacker.base.crit_multiplier)
        if guarded:
            damage = int(damage * 0.5)
        return max(1, damage), crit

    def _enemy_choose(self, enemy: Combatant, player: Combatant) -> Action:
        if enemy.hp < int(enemy.max_hp * 0.35) and self.rng.random() < 0.25 and enemy.potions > 0:
            return Action.HEAL
        if player.hp > 16 and self.rng.random() < 0.25:
            return Action.POWER_ATTACK
        return Action.ATTACK

    def _apply_action(self, actor: Combatant, target: Combatant, action: Action, guarded: bool = False) -> TurnLog:
        if action == Action.HEAL:
            if actor.potions <= 0:
                return TurnLog(actor.name, action.value, 0, "no potion")
            heal_amount = min(16, actor.max_hp - actor.hp)
            actor.hp += heal_amount
            actor.potions -= 1
            return TurnLog(actor.name, action.value, heal_amount, "restored hp")

        if action == Action.GUARD:
            return TurnLog(actor.name, action.value, 0, "bracing for impact")

        power = 1.45 if action == Action.POWER_ATTACK else 1.0
        damage, crit = self._roll_damage(actor, target, power=power, guarded=guarded)
        target.hp = max(0, target.hp - damage)
        detail = "critical" if crit else "hit"
        return TurnLog(actor.name, action.value, damage, detail)

    def run_battle(self, scripted_player_actions: List[Action] | None = None) -> Dict[str, object]:
        player = self.create_player()
        enemy = self.create_enemy()
        logs: List[TurnLog] = []
        turn = 0

        while player.alive and enemy.alive and turn < 100:
            # Player turn
            if scripted_player_actions:
                action = scripted_player_actions[min(turn, len(scripted_player_actions) - 1)]
            else:
                action = self._player_ai(player, enemy)

            enemy_guarding = False
            if action == Action.GUARD:
                logs.append(self._apply_action(player, enemy, action))
                enemy_guarding = True
            else:
                logs.append(self._apply_action(player, enemy, action))

            if not enemy.alive:
                break

            # Enemy turn
            e_action = self._enemy_choose(enemy, player)
            guarded = action == Action.GUARD
            logs.append(self._apply_action(enemy, player, e_action, guarded=guarded))

            turn += 1

        winner = player.name if player.alive and not enemy.alive else enemy.name if enemy.alive and not player.alive else "draw"
        if winner == player.name:
            player.gain_xp(25)

        return {
            "winner": winner,
            "turns": turn + 1,
            "player_hp": player.hp,
            "enemy_hp": enemy.hp,
            "player_level": player.level,
            "logs": logs,
        }

    def _player_ai(self, player: Combatant, enemy: Combatant) -> Action:
        if player.hp < int(player.max_hp * 0.4) and player.potions > 0:
            return Action.HEAL
        if enemy.hp > 14 and self.rng.random() < 0.3:
            return Action.POWER_ATTACK
        if player.hp < 12 and self.rng.random() < 0.35:
            return Action.GUARD
        return Action.ATTACK


def play_cli() -> None:
    rng = random.Random()
    game = BattleGame(rng=rng)
    result = game.run_battle()
    print(f"Winner: {result['winner']}")
    print(f"Turns: {result['turns']} | Player HP: {result['player_hp']} | Enemy HP: {result['enemy_hp']}")
    for entry in result["logs"]:
        print(f"- {entry.actor} used {entry.action}: {entry.amount} ({entry.detail})")


if __name__ == "__main__":
    play_cli()
