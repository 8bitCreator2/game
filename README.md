# Simulation-Balanced Battle Game

This repository now includes an expandable battle game with:

- Richer combat actions: `attack`, `power_attack`, `heal`, and `guard`
- Progression: hero XP and level-ups with stat growth
- Enemy behavior AI with situational choices
- Monte Carlo simulation helpers for balancing encounters
- Automatic encounter tuning to target a desired win rate

## Run one game

```bash
python game.py
```

## Run balancing simulation

```bash
python balance.py
```

## Run tests

```bash
pytest -q
```
