"""
entities.py — Player, Enemy, and Item definitions for shellbound.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    BRIGHT_RED    = "\033[91m"
    BRIGHT_GREEN  = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_CYAN   = "\033[96m"
    BRIGHT_WHITE  = "\033[97m"

    @staticmethod
    def wrap(text: str, *codes: str) -> str:
        return "".join(codes) + text + Color.RESET


@dataclass
class Item:
    name: str
    description: str
    item_type: str
    value: int = 0
    hidden: bool = False

    def __str__(self) -> str:
        return self.name


def make_item(name: str) -> Item:
    catalogue: dict[str, Item] = {
        "health_potion": Item(
            name="health_potion",
            description="A bubbling red vial. Restores 30 HP when consumed.",
            item_type="consumable",
            value=30,
        ),
        "sword": Item(
            name="sword",
            description="A steel longsword. Required to harm the dragon.",
            item_type="weapon",
            value=10,
        ),
        "scroll": Item(
            name="scroll",
            description=(
                "A dusty scroll. It reads:\n"
                "  'The dragon fears only cold steel forged in the armory.\n"
                "   The key to the throne lies hidden in the library.\n"
                "   chmod opens what locks cannot.'"
            ),
            item_type="readable",
        ),
        "key": Item(
            name="key",
            description="An ornate iron key. It looks like it opens something important.",
            item_type="key",
            hidden=True,
        ),
        "gold": Item(
            name="gold",
            description="A pouch of gold coins. Very shiny. Worth 50 points.",
            item_type="treasure",
            value=50,
        ),
    }
    if name not in catalogue:
        raise ValueError(f"Unknown item: {name}")
    return catalogue[name]


@dataclass
class Enemy:
    name: str
    display_name: str
    hp: int
    max_hp: int
    attack: int
    description: str
    requires_sword: bool = False
    alive: bool = True
    color: str = Color.RED

    def is_alive(self) -> bool:
        return self.alive and self.hp > 0

    def take_damage(self, dmg: int) -> int:
        actual = min(dmg, self.hp)
        self.hp -= actual
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return actual

    def hp_bar(self, width: int = 20) -> str:
        filled = int((self.hp / self.max_hp) * width)
        bar = "█" * filled + "░" * (width - filled)
        color = Color.GREEN if filled > width // 2 else Color.YELLOW if filled > 0 else Color.RED
        return f"[{Color.wrap(bar, color)}] {self.hp}/{self.max_hp}"

    def __str__(self) -> str:
        return Color.wrap(self.display_name, self.color, Color.BOLD)


def make_enemy(name: str) -> Enemy:
    catalogue: dict[str, Enemy] = {
        "goblin": Enemy(
            name="goblin",
            display_name="Goblin",
            hp=20, max_hp=20,
            attack=5,
            description="A scrawny green creature with beady eyes and a rusty dagger.",
            color=Color.GREEN,
        ),
        "skeleton": Enemy(
            name="skeleton",
            display_name="Skeleton",
            hp=35, max_hp=35,
            attack=10,
            description="Animated bones rattling in rusted armour. Its eyes glow crimson.",
            color=Color.WHITE,
        ),
        "dragon": Enemy(
            name="dragon",
            display_name="Dragon",
            hp=80, max_hp=80,
            attack=25,
            description=(
                "A massive ancient dragon. Scales black as midnight, eyes like molten gold.\n"
                "  Its breath alone could end you. You need a sword to pierce its hide."
            ),
            requires_sword=True,
            color=Color.BRIGHT_RED,
        ),
    }
    if name not in catalogue:
        raise ValueError(f"Unknown enemy: {name}")
    return catalogue[name]


@dataclass
class Player:
    name: str
    hp: int = 100
    max_hp: int = 100
    base_attack: int = 8
    inventory: list[Item] = field(default_factory=list)
    score: int = 0
    kills: int = 0

    @property
    def attack(self) -> int:
        bonus = sum(i.value for i in self.inventory if i.item_type == "weapon")
        return self.base_attack + bonus

    @property
    def has_sword(self) -> bool:
        return any(i.name == "sword" for i in self.inventory)

    @property
    def has_key(self) -> bool:
        return any(i.name == "key" for i in self.inventory)

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, dmg: int) -> int:
        actual = min(dmg, self.hp)
        self.hp -= actual
        if self.hp < 0:
            self.hp = 0
        return actual

    def heal(self, amount: int) -> int:
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before

    def pickup(self, item: Item) -> None:
        self.inventory.append(item)
        if item.item_type == "treasure":
            self.score += item.value

    def drop_item(self, name: str) -> Optional[Item]:
        for i, item in enumerate(self.inventory):
            if item.name == name:
                return self.inventory.pop(i)
        return None

    def has_item(self, name: str) -> bool:
        return any(i.name == name for i in self.inventory)

    def hp_bar(self, width: int = 20) -> str:
        filled = int((self.hp / self.max_hp) * width)
        bar = "█" * filled + "░" * (width - filled)
        color = Color.GREEN if filled > width // 2 else Color.YELLOW if filled > width // 4 else Color.RED
        return f"[{Color.wrap(bar, color)}] {self.hp}/{self.max_hp}"

    def inventory_str(self) -> str:
        if not self.inventory:
            return Color.wrap("(empty)", Color.WHITE)
        return "  ".join(
            Color.wrap(i.name, Color.CYAN) for i in self.inventory
        )
