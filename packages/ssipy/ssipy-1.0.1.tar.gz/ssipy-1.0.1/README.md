# Tackling the UNO Card Game with Reinforcement Learning

Author: [Bernhard Pfann](https://www.linkedin.com/in/bernhard-pfann/)<br>
Article: [https://towardsdatascience.com/tackling-uno-card-game-with-reinforcement-learning](https://towardsdatascience.com/tackling-uno-card-game-with-reinforcement-learning-fad2fc19355c)<br>
Status: Done<br>

## 🎮 Play UNO with a Trained RL Agent!

This project now includes a **professional GUI** and **state-of-the-art RL agents** using Stable Baselines3!

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI and play against the AI or watch the trained PPO agent!
python uno_gui.py
```

### Features
- 🎴 Beautiful graphical interface with animations
- 🤖 **PPO Agent** trained using Stable Baselines3
- 👀 Watch mode to see the RL agent play automatically
- 🎯 Play manually against a rule-based AI

---

## Training Your Own RL Agent

### Train with Stable Baselines3 (Recommended)

```bash
# Train PPO agent (best for games)
python train_sb3.py --algorithm ppo --timesteps 100000

# Train DQN agent
python train_sb3.py --algorithm dqn --timesteps 100000

# Train A2C agent
python train_sb3.py --algorithm a2c --timesteps 100000

# Compare all algorithms
python train_sb3.py --compare --timesteps 50000 --eval-episodes 100
```

### Train with Custom Implementation

```bash
# Train custom DQN with experience replay
python train_rl.py --agent dqn --episodes 1000

# Train improved Q-learning agent
python train_rl.py --agent qlearning --episodes 1000
```

---

## Description
In this project I tried to analytically derive an optimal strategy, for the classic UNO card game. To do so, I structured my work as follows:
1. Creating a game engine of the UNO card game in Python from scratch
2. Obtaining game statistics from simulating a series of 100,000 games
3. Implementing basic Reinforcement Learning techniques (Q-Learning & Monte Carlo) in order to discover an optimal game strategy
4. **NEW:** Implementing state-of-the-art RL algorithms (PPO, DQN, A2C) using Stable Baselines3

<b>UNO card engine:</b> In order to train a Reinforcement Learning (RL) agent how to play intelligently, a fully-fledged game environment needs to be in place, capturing all the mechanics and rules of the game. Class objects for <code>Card</code>, <code>Deck</code>, <code>Player</code>, <code>Turn</code> and <code>Game</code> are defined.

<b>Statistics from simulations:</b> By running multiple simulations of the game, the following questions are being tackled:
* How many turns do games last?
* How big is the advantage of the player making the first turn?
* What are the most likely situations in the course of a game?

<b>Application of Reinforcement Learning:</b> The project now supports multiple RL approaches:
- **Stable Baselines3**: PPO, DQN, A2C algorithms with neural networks
- **Custom DQN**: PyTorch-based implementation with experience replay
- **Q-Learning**: Tabular method with improved reward shaping
- **Monte Carlo**: Episode-based learning

## Repository Structure

 - `assets/` collection of .csv files and training curves
 - `models/` saved RL models (PPO, DQN, Q-learning)
 - `notebooks/` analysis of simulated games
 - `src/` core package to simulate games
   - `sb3_agent.py` Stable Baselines3 agent wrapper
   - `dqn_agent.py` Custom DQN and improved Q-learning
   - `agents.py` Legacy Q-learning and Monte Carlo
 - `config.py` configurable parameters
 - `run.py` legacy execution file
 - `train_sb3.py` train with Stable Baselines3
 - `train_rl.py` train with custom implementations
 - `uno_gui.py` graphical interface

## Installation

Clone repository via HTTPS:

```bash
git clone https://github.com/bernhard-pfann/uno-card-game-rl.git
cd uno-card-game-rl
```

Install requirements:

```bash
pip install -r requirements.txt
```

## Execution

### Play the Game
```bash
python uno_gui.py
```

### Train RL Agents
```bash
# Recommended: PPO with 100k timesteps
python train_sb3.py --algorithm ppo --timesteps 100000

# Quick training for testing
python train_sb3.py --algorithm ppo --timesteps 20000 --eval-episodes 50
```

### Legacy Execution
```bash
python run.py
```
