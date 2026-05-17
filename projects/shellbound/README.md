# shellbound

> A dungeon crawler for those who live in the terminal.

```
  ____  _   _ _____ _     _      ____   ___  _   _ _   _ ____
 / ___|| | | | ____| |   | |    | __ ) / _ \| | | | \ | |  _ \
 \___ \| |_| |  _| | |   | |    |  _ \| | | | | | |  \| | | | |
  ___) |  _  | |___| |___| |___ | |_) | |_| | |_| | |\  | |_| |
 |____/|_| |_|_____|_____|_____||____/ \___/ \___/|_| \_|____/
```

You wake up in a dungeon. Your muscle memory takes over.
You type `ls`. The dungeon answers.

**shellbound** is a terminal roguelike where every action is a real shell command.
Fight enemies with `rm`. Read items with `cat`. Unlock doors with `chmod`.
The dungeon is a filesystem. You are the shell.

---

## Installation

```bash
git clone https://github.com/clearablelight/shellbound
cd shellbound
python game.py
```

Requires Python 3.10+. No external dependencies.

---

## Dungeon Map

```
        [LIBRARY]
            |
            | (north)
            |
[ENTRANCE] ---east--- [ARMORY]
            |
            | (south)
            |
          [CRYPT]
            |
            | (south) <<< LOCKED DOOR >>>
            |
       [THRONE ROOM]
```

| Room         | Enemies   | Items                      | Notes                        |
|--------------|-----------|----------------------------|------------------------------|
| Entrance     | Goblin    | Health Potion              | Starting room                |
| Armory       | Skeleton  | Sword                      | Sword needed to kill dragon  |
| Library      | Skeleton  | Scroll, Gold, **Key**      | Key is hidden — use `grep`   |
| Crypt        | Goblin    | Health Potion              | Locked door to throne room   |
| Throne Room  | **Dragon**| Gold                       | Win by killing the dragon    |

---

## Commands

| Command                    | What it does                                        |
|----------------------------|-----------------------------------------------------|
| `ls`                       | List enemies, items, and exits in the current room  |
| `pwd`                      | Show your location as a filesystem path             |
| `cd north`                 | Move north (also south / east / west)               |
| `rm goblin`                | Attack a goblin                                     |
| `cat scroll`               | Read or use an item                                 |
| `cat health_potion`        | Drink a potion to restore HP                        |
| `grep key`                 | Search the room; reveals hidden items               |
| `find . -name "key"`       | Search the entire dungeon for an item               |
| `chmod 777 door`           | Unlock the locked door (must have key)              |
| `status`                   | Show HP, attack power, inventory, score             |
| `help`                     | Show all commands                                   |
| `quit`                     | Exit the game                                       |

---

## How to Win

1. **Grab the health potion** in the entrance (`cat health_potion`).
2. **Go east** to the armory and kill the skeleton (`rm skeleton`).
3. **Pick up the sword** (`cat sword`) — you need it for the dragon.
4. **Go north** to the library. Kill the skeleton (`rm skeleton`).
5. **Find the hidden key** (`grep key`) then pick it up (`cat key`).
6. **Go south to the crypt** and then **unlock the door** (`chmod 777 door`).
7. **Go south** into the throne room and **slay the dragon** (`rm dragon`).

---

## Architecture

```
shellbound/
├── game.py       — Main entry point and game loop
├── dungeon.py    — Room definitions and dungeon map
├── entities.py   — Player, Enemy, and Item data classes
├── parser.py     — Shell command parser
└── renderer.py   — ANSI-colored ASCII art display
```

---

## License

MIT. Go forth and `rm` monsters.
