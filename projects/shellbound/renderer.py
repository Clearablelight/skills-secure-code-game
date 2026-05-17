"""
renderer.py — ASCII art rendering and status display for shellbound.
"""
from __future__ import annotations
from entities import Color, Player
from dungeon import Room
import re as _re


def horizontal_rule(char: str = "─", width: int = 60) -> str:
    return Color.wrap(char * width, Color.BLUE)


def section_header(title: str, width: int = 60) -> str:
    pad = (width - len(title) - 2) // 2
    left  = "─" * pad
    right = "─" * (width - len(title) - 2 - pad)
    return Color.wrap(f"╔{left}[ ", Color.BLUE) + Color.wrap(title, Color.BRIGHT_YELLOW, Color.BOLD) + Color.wrap(f" ]{right}╗", Color.BLUE)


def box_bottom(width: int = 60) -> str:
    return Color.wrap("╚" + "─" * (width - 2) + "╝", Color.BLUE)


def _strip_ansi(text: str) -> str:
    return _re.sub(r"\x1b\[[0-9;]*m", "", text)


class Renderer:
    WIDTH = 60

    def print_logo(self) -> None:
        logo = r"""
  ____  _   _ _____ _     _      ____   ___  _   _ _   _ ____
 / ___|| | | | ____| |   | |    | __ ) / _ \| | | | \ | |  _ \
 \___ \| |_| |  _| | |   | |    |  _ \| | | | | | |  \| | | | |
  ___) |  _  | |___| |___| |___ | |_) | |_| | |_| | |\  | |_| |
 |____/|_| |_|_____|_____|_____|\|____/ \___/ \___/|_| \_|____/
"""
        tagline = "  A dungeon crawler for those who live in the terminal."
        print(Color.wrap(logo, Color.BRIGHT_CYAN, Color.BOLD))
        print(Color.wrap(tagline, Color.CYAN))
        print()

    def print_welcome(self) -> None:
        self.print_logo()
        msg = [
            Color.wrap("Welcome, adventurer. The dungeon awaits.", Color.BRIGHT_WHITE),
            "",
            f"  Type {Color.wrap('help', Color.BRIGHT_YELLOW)} to see available commands.",
            f"  Type {Color.wrap('ls', Color.BRIGHT_YELLOW)} to look around.",
            f"  Type {Color.wrap('status', Color.BRIGHT_YELLOW)} to see your stats.",
            "",
            Color.wrap("  Your goal: find the sword, get the key, unlock the throne room,", Color.WHITE),
            Color.wrap("  and slay the dragon. Good luck.", Color.WHITE),
        ]
        print(horizontal_rule())
        for line in msg:
            print(f"  {line}")
        print(horizontal_rule())
        print()

    def render_room(self, room: Room, player: Player, verbose: bool = True) -> None:
        print()
        print(section_header(room.name, self.WIDTH))
        if room.ascii_art:
            for line in room.ascii_art.splitlines():
                print(f"    {Color.wrap(line, Color.YELLOW)}")
        print()
        if verbose:
            for line in room.long_desc.splitlines():
                print(f"  {Color.wrap(line, Color.WHITE)}")
        else:
            print(f"  {Color.wrap(room.short_desc, Color.WHITE)}")
        print()

        exits = []
        for direction, dest_id in room.exits.items():
            locked = direction in room.locked_exits
            lock_str = Color.wrap(" [LOCKED]", Color.RED) if locked else ""
            exits.append(f"{Color.wrap(direction, Color.BRIGHT_CYAN)}{lock_str}")
        print(f"  {Color.wrap('Exits:', Color.BOLD)} {', '.join(exits)}")

        living = room.living_enemies()
        if living:
            print(f"  {Color.wrap('Enemies:', Color.BOLD)} {', '.join(Color.wrap(e.name, Color.RED) for e in living)}")
        else:
            print(f"  {Color.wrap('Enemies:', Color.BOLD)} {Color.wrap('none', Color.GREEN)}")

        visible = room.visible_items()
        if visible:
            item_strs = [Color.wrap(i.name, Color.CYAN) for i in visible]
            print(f"  {Color.wrap('Items:', Color.BOLD)}   {', '.join(item_strs)}")
        else:
            print(f"  {Color.wrap('Items:', Color.BOLD)}   {Color.wrap('none', Color.WHITE)}")

        print(box_bottom(self.WIDTH))
        print()

    def render_ls(self, room: Room) -> None:
        print()
        print(Color.wrap(f"  /dungeon/{room.id}/", Color.BRIGHT_YELLOW, Color.BOLD))
        print()

        living = room.living_enemies()
        visible = room.visible_items()

        items_out = []
        for enemy in living:
            items_out.append(Color.wrap(enemy.name + "/", Color.RED, Color.BOLD))
        for item in visible:
            type_color = {
                "weapon": Color.BRIGHT_CYAN,
                "consumable": Color.GREEN,
                "key": Color.BRIGHT_YELLOW,
                "treasure": Color.YELLOW,
                "readable": Color.MAGENTA,
            }.get(item.item_type, Color.WHITE)
            items_out.append(Color.wrap(item.name, type_color))
        for direction in room.exits:
            locked = direction in room.locked_exits
            label = direction + ("/" if not locked else "/\U0001f512")
            items_out.append(Color.wrap(label, Color.BLUE))

        if items_out:
            col_w = 20
            for i, entry in enumerate(items_out):
                end = "\n" if (i + 1) % 4 == 0 or i == len(items_out) - 1 else ""
                plain = _strip_ansi(entry)
                pad = max(0, col_w - len(plain))
                print(f"  {entry}{' ' * pad}", end=end)
        else:
            print(Color.wrap("  (empty room)", Color.WHITE))

        print()

    def render_status(self, player: Player, room: Room) -> None:
        print()
        print(section_header("STATUS", self.WIDTH))
        print(f"  {Color.wrap('Name:', Color.BOLD)}      {Color.wrap(player.name, Color.BRIGHT_WHITE)}")
        print(f"  {Color.wrap('HP:', Color.BOLD)}        {player.hp_bar(20)}")
        print(f"  {Color.wrap('Attack:', Color.BOLD)}    {Color.wrap(str(player.attack), Color.BRIGHT_YELLOW)} dmg")
        print(f"  {Color.wrap('Score:', Color.BOLD)}     {Color.wrap(str(player.score), Color.YELLOW)}")
        print(f"  {Color.wrap('Kills:', Color.BOLD)}     {Color.wrap(str(player.kills), Color.RED)}")
        print(f"  {Color.wrap('Location:', Color.BOLD)} {Color.wrap(room.path(), Color.CYAN)}")
        print(f"  {Color.wrap('Inventory:', Color.BOLD)} {player.inventory_str()}")
        print(box_bottom(self.WIDTH))
        print()

    def render_enemy_hp(self, enemy) -> None:
        print(f"  {enemy} {enemy.hp_bar(20)}")

    def render_combat(self, attacker: str, target: str, dmg: int, color: str = Color.BRIGHT_RED) -> None:
        print(Color.wrap(f"  ⚔  {attacker} hits {target} for {dmg} damage!", color))

    def render_death(self, enemy_name: str) -> None:
        print(Color.wrap(f"  ☠  {enemy_name} has been slain!", Color.BRIGHT_YELLOW, Color.BOLD))

    def render_player_hit(self, enemy_name: str, dmg: int, player: Player) -> None:
        print(Color.wrap(f"  \U0001f4a5 {enemy_name} strikes you for {dmg} damage!", Color.RED))
        print(f"  Your HP: {player.hp_bar(20)}")

    def render_pickup(self, item_name: str) -> None:
        print(Color.wrap(f"  + Picked up: {item_name}", Color.BRIGHT_GREEN))

    def render_error(self, msg: str) -> None:
        print(Color.wrap(f"  ✗  {msg}", Color.RED))

    def render_info(self, msg: str) -> None:
        print(Color.wrap(f"  ℹ  {msg}", Color.CYAN))

    def render_success(self, msg: str) -> None:
        print(Color.wrap(f"  ✔  {msg}", Color.BRIGHT_GREEN))

    def render_warn(self, msg: str) -> None:
        print(Color.wrap(f"  ⚠  {msg}", Color.BRIGHT_YELLOW))

    def render_win(self, player: Player) -> None:
        banner = r"""
  ██╗   ██╗██╗ ██████╗███████╗ ██████╗ ██████╗ ██╗   ██╗██╗
  ██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝██║
  ██║   ██║██║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ ██║
  ╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  ╚═╝
   ╚████╔╝ ██║╚██████╗   ██║   ╚█████╔╝██║  ██║   ██║   ██╗
    ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝
"""
        print(Color.wrap("  The dragon falls! The dungeon trembles!", Color.BRIGHT_WHITE))
        print(Color.wrap("  You have conquered Shellbound!", Color.BRIGHT_GREEN, Color.BOLD))
        print()
        print(f"  {Color.wrap('Final Score:', Color.BOLD)} {Color.wrap(str(player.score), Color.BRIGHT_YELLOW)}")
        print(f"  {Color.wrap('Total Kills:', Color.BOLD)} {Color.wrap(str(player.kills), Color.RED)}")
        print(f"  {Color.wrap('HP Remaining:', Color.BOLD)} {player.hp_bar(20)}")
        print()

    def render_game_over(self, player: Player) -> None:
        print(Color.wrap("  You have been slain. The dungeon claims another soul.", Color.RED))
        print()
        print(f"  {Color.wrap('Final Score:', Color.BOLD)} {Color.wrap(str(player.score), Color.BRIGHT_YELLOW)}")
        print(f"  {Color.wrap('Total Kills:', Color.BOLD)} {Color.wrap(str(player.kills), Color.RED)}")
        print()

    def render_help(self) -> None:
        commands = [
            ("ls",                     "List enemies, items, and exits in the current room"),
            ("pwd",                    "Show your current location path"),
            ("cd <direction>",         "Move in a direction (north/south/east/west)"),
            ("rm <enemy>",             "Attack an enemy (e.g.  rm goblin)"),
            ("cat <item>",             "Use/read an item (e.g.  cat scroll)"),
            ("grep <name>",            "Search the room; may reveal hidden items"),
            ('find . -name "<item>"',  "Search the entire dungeon for an item"),
            ("chmod 777 door",         "Unlock the locked door in the crypt (needs key)"),
            ("status",                 "Show your HP, attack, inventory, and score"),
            ("help",                   "Show this help message"),
            ("quit / exit",            "Quit the game"),
        ]
        print()
        print(section_header("AVAILABLE COMMANDS", self.WIDTH))
        for cmd, desc in commands:
            cmd_str = Color.wrap(f"  {cmd:<28}", Color.BRIGHT_YELLOW)
            print(f"{cmd_str}{Color.wrap(desc, Color.WHITE)}")
        print()
        print(f"  {Color.wrap('Tip:', Color.BOLD, Color.CYAN)} The dungeon is a real shell session in disguise.")
        print(f"  {Color.wrap('Tip:', Color.BOLD, Color.CYAN)} Read the scroll for hints about the throne room.")
        print(box_bottom(self.WIDTH))
        print()
