"""
game.py — Main entry point for shellbound.

Run with:  python game.py
"""
from __future__ import annotations
import os
import sys
import random

from entities import Player, Color, make_item
from dungeon import Dungeon, Room
from renderer import Renderer
from parser import parse, Action


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------
class GameState:
    def __init__(self, player: Player, dungeon: Dungeon) -> None:
        self.player   = player
        self.dungeon  = dungeon
        self.current_room: Room = dungeon.starting_room()
        self.running  = True
        self.won      = False
        self.throne_unlocked = False


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------
class GameEngine:
    def __init__(self, state: GameState, renderer: Renderer) -> None:
        self.state    = state
        self.renderer = renderer

    # ------------------------------------------------------------------ #
    # Routing                                                              #
    # ------------------------------------------------------------------ #
    def handle(self, action: Action) -> None:
        handlers = {
            "noop":      self._noop,
            "quit":      self._quit,
            "help":      self._help,
            "status":    self._status,
            "pwd":       self._pwd,
            "clear":     self._clear,
            "ls":        self._ls,
            "cd":        self._cd,
            "rm":        self._rm,
            "cat":       self._cat,
            "grep":      self._grep,
            "find":      self._find,
            "chmod":     self._chmod,
            "look":      self._look,
            "inventory": self._inventory,
            "pickup":    self._pickup,
            "error":     self._error,
            "unknown":   self._unknown,
        }
        fn = handlers.get(action.verb, self._unknown)
        fn(action)

    # ------------------------------------------------------------------ #
    # Individual handlers                                                  #
    # ------------------------------------------------------------------ #
    def _noop(self, _: Action) -> None:
        pass

    def _quit(self, _: Action) -> None:
        print()
        self.renderer.render_info("Farewell, adventurer. The dungeon will remember you.")
        print()
        self.state.running = False

    def _help(self, _: Action) -> None:
        self.renderer.render_help()

    def _status(self, _: Action) -> None:
        self.renderer.render_status(self.state.player, self.state.current_room)

    def _pwd(self, _: Action) -> None:
        path = self.state.current_room.path()
        print(f"  {Color.wrap(path, Color.CYAN)}")
        print()

    def _clear(self, _: Action) -> None:
        os.system("clear" if os.name == "posix" else "cls")

    def _ls(self, _: Action) -> None:
        self.renderer.render_ls(self.state.current_room)

    def _look(self, action: Action) -> None:
        target = action.first_arg()
        room   = self.state.current_room
        player = self.state.player

        if not target:
            self.renderer.render_room(room, player, verbose=True)
            return

        enemy = room.enemy_by_name(target)
        if enemy:
            print()
            print(f"  {enemy}")
            print(f"  {Color.wrap(enemy.description, Color.WHITE)}")
            print(f"  HP: {enemy.hp_bar(20)}")
            print()
            return

        item = room.item_by_name(target)
        if item:
            print()
            print(f"  {Color.wrap(item.name, Color.CYAN)}")
            print(f"  {Color.wrap(item.description, Color.WHITE)}")
            print()
            return

        if player.has_item(target):
            inv_item = next(i for i in player.inventory if i.name == target)
            print()
            print(f"  {Color.wrap(inv_item.name, Color.CYAN)} {Color.wrap('(in inventory)', Color.WHITE)}")
            print(f"  {Color.wrap(inv_item.description, Color.WHITE)}")
            print()
            return

        self.renderer.render_error(f"You don't see '{target}' here.")

    def _inventory(self, _: Action) -> None:
        player = self.state.player
        print()
        if not player.inventory:
            self.renderer.render_info("Your inventory is empty.")
        else:
            print(f"  {Color.wrap('Inventory:', Color.BOLD)}")
            for item in player.inventory:
                type_color = {
                    "weapon": Color.BRIGHT_CYAN,
                    "consumable": Color.GREEN,
                    "key": Color.BRIGHT_YELLOW,
                    "treasure": Color.YELLOW,
                    "readable": Color.MAGENTA,
                }.get(item.item_type, Color.WHITE)
                print(f"    {Color.wrap(item.name, type_color):<40} {Color.wrap(item.description.splitlines()[0], Color.WHITE)}")
        print()

    def _cd(self, action: Action) -> None:
        direction = action.first_arg()
        room      = self.state.current_room
        player    = self.state.player

        if direction not in room.exits:
            self.renderer.render_error(
                f"There is no exit to the {direction}. "
                f"Available exits: {', '.join(room.exits.keys())}"
            )
            return

        if direction in room.locked_exits:
            self.renderer.render_warn(
                "The door to the south is sealed with an ancient lock."
            )
            self.renderer.render_info(
                "Hint: Find the key and use  chmod 777 door  to unlock it."
            )
            return

        dest_id   = room.exits[direction]
        dest_room = self.state.dungeon.get_room(dest_id)

        self.state.current_room = dest_room
        print()
        print(Color.wrap(f"  You move {direction}...", Color.WHITE))
        self.renderer.render_room(dest_room, player, verbose=True)

        self._room_entry_attacks()

    def _rm(self, action: Action) -> None:
        target = action.first_arg()
        room   = self.state.current_room
        player = self.state.player

        enemy = room.enemy_by_name(target)
        if enemy is None:
            dead = next((e for e in room.enemies if e.name == target), None)
            if dead:
                self.renderer.render_error(f"{target} is already dead.")
            else:
                self.renderer.render_error(
                    f"There is no '{target}' here to attack. "
                    f"Try: {', '.join(e.name for e in room.living_enemies()) or 'no enemies present'}."
                )
            return

        if enemy.requires_sword and not player.has_sword:
            self.renderer.render_warn(
                "Your bare hands bounce off the dragon's armour-like scales!"
            )
            self.renderer.render_info(
                "You need a sword to harm the dragon. Find one in the armory."
            )
            self._enemy_attacks(enemy)
            return

        dmg = self._calc_player_dmg()
        actual = enemy.take_damage(dmg)
        self.renderer.render_combat(player.name, str(enemy), actual)

        if not enemy.is_alive():
            self.renderer.render_death(enemy.display_name)
            player.kills += 1
            player.score += {"goblin": 10, "skeleton": 25, "dragon": 100}.get(enemy.name, 10)

            loot_table = {
                "goblin":   ["gold"],
                "skeleton": ["health_potion"],
                "dragon":   ["gold"],
            }
            for loot_name in loot_table.get(enemy.name, []):
                loot = make_item(loot_name)
                room.add_item(loot)
                self.renderer.render_info(f"{enemy.display_name} dropped: {loot_name}")

            if enemy.name == "dragon":
                self.state.won    = True
                self.state.running = False
                return
        else:
            self.renderer.render_enemy_hp(enemy)
            self._enemy_attacks(enemy)

    def _cat(self, action: Action) -> None:
        item_name = action.first_arg()
        room      = self.state.current_room
        player    = self.state.player

        item = room.item_by_name(item_name)
        in_room = item is not None

        if item is None:
            item = next((i for i in player.inventory if i.name == item_name), None)

        if item is None:
            self.renderer.render_error(
                f"No item named '{item_name}' here or in your inventory."
            )
            return

        print()
        print(f"  {Color.wrap(item.name, Color.CYAN, Color.BOLD)}")
        print(f"  {Color.wrap('─' * 40, Color.BLUE)}")

        if item.item_type == "readable":
            for line in item.description.splitlines():
                print(f"  {Color.wrap(line, Color.WHITE)}")
            print()
            if in_room:
                room.remove_item(item_name)
                player.pickup(item)
                self.renderer.render_pickup(item_name)

        elif item.item_type == "consumable":
            print(f"  {Color.wrap(item.description, Color.WHITE)}")
            print()
            healed = player.heal(item.value)
            self.renderer.render_success(f"You drink the {item_name}. Restored {healed} HP.")
            print(f"  Your HP: {player.hp_bar(20)}")
            print()
            if in_room:
                room.remove_item(item_name)
            else:
                player.drop_item(item_name)

        elif item.item_type == "weapon":
            print(f"  {Color.wrap(item.description, Color.WHITE)}")
            print()
            if player.has_item(item_name):
                self.renderer.render_info(f"You already have the {item_name}.")
            else:
                room.remove_item(item_name)
                player.pickup(item)
                self.renderer.render_pickup(item_name)
                self.renderer.render_success(f"Attack power increased by +{item.value}!")
            print()

        elif item.item_type == "key":
            print(f"  {Color.wrap(item.description, Color.WHITE)}")
            print()
            if player.has_item(item_name):
                self.renderer.render_info(f"You already have the {item_name}.")
            else:
                room.remove_item(item_name)
                player.pickup(item)
                self.renderer.render_pickup(item_name)
                self.renderer.render_info("The key might open the locked door in the crypt.")
            print()

        elif item.item_type == "treasure":
            print(f"  {Color.wrap(item.description, Color.WHITE)}")
            print()
            if in_room:
                room.remove_item(item_name)
                player.pickup(item)
                self.renderer.render_pickup(item_name)
                self.renderer.render_success(f"Added {item.value} gold to your score!")
            else:
                self.renderer.render_info(f"You admire your {item_name}.")
            print()

        else:
            print(f"  {Color.wrap(item.description, Color.WHITE)}")
            print()

    def _grep(self, action: Action) -> None:
        pattern = action.first_arg()
        room    = self.state.current_room

        print()
        print(Color.wrap(f"  grep '{pattern}' .", Color.BRIGHT_YELLOW))
        print()

        found_anything = False

        for enemy in room.living_enemies():
            if pattern in enemy.name or pattern in enemy.display_name.lower():
                print(f"  {Color.wrap(enemy.name, Color.RED)}: {Color.wrap(enemy.description.splitlines()[0], Color.WHITE)}")
                found_anything = True

        for item in room.visible_items():
            if pattern in item.name:
                print(f"  {Color.wrap(item.name, Color.CYAN)}: {Color.wrap(item.description.splitlines()[0], Color.WHITE)}")
                found_anything = True

        revealed = []
        for item in room.hidden_items():
            if pattern in item.name or pattern == item.name:
                revealed.append(item)

        if revealed:
            for item in revealed:
                item.hidden = False
                print(f"  {Color.wrap('!', Color.BRIGHT_YELLOW)} Found hidden item: {Color.wrap(item.name, Color.BRIGHT_YELLOW)}")
                print(f"    {Color.wrap(item.description, Color.WHITE)}")
                found_anything = True
        elif room.hidden_items():
            if random.random() < 0.4:
                self.renderer.render_info("You sense something hidden nearby...")

        if not found_anything:
            print(Color.wrap(f"  (no matches for '{pattern}')", Color.WHITE))

        print()

    def _find(self, action: Action) -> None:
        item_name = action.first_arg()
        dungeon   = self.state.dungeon
        player    = self.state.player

        print()
        print(Color.wrap(f"  find . -name \"{item_name}\"", Color.BRIGHT_YELLOW))
        print()

        results = dungeon.find_item_everywhere(item_name)
        inv_match = [i for i in player.inventory if i.name == item_name]

        if not results and not inv_match:
            print(Color.wrap(f"  (no results for '{item_name}')", Color.WHITE))
        else:
            for room, item in results:
                vis_label = "" if not item.hidden else Color.wrap(" [hidden]", Color.YELLOW)
                print(f"  {Color.wrap(room.path() + '/' + item.name, Color.CYAN)}{vis_label}")
                if item.hidden:
                    self.renderer.render_info(f"Something named '{item_name}' is hidden in {room.name}. Try grep to reveal it.")
            for item in inv_match:
                print(f"  {Color.wrap('./inventory/' + item.name, Color.GREEN)}")

        print()

    def _chmod(self, action: Action) -> None:
        target = action.first_arg()
        room   = self.state.current_room
        player = self.state.player

        is_door_target = target in ("door", "south", "throne_room", "lock")

        if not is_door_target:
            self.renderer.render_error(
                f"chmod: cannot change permissions of '{target}': "
                f"No such file or locked object. Did you mean 'door'?"
            )
            return

        if room.id != "crypt":
            self.renderer.render_error(
                "There is no locked door here. The locked door is in the crypt."
            )
            return

        if not player.has_key:
            self.renderer.render_warn(
                "The lock mechanism clicks but doesn't yield — you're missing the key."
            )
            self.renderer.render_info(
                "Find the key (hint: it's hidden in the library — try  grep key  there)."
            )
            return

        if "south" not in room.locked_exits:
            self.renderer.render_info("The door is already unlocked.")
            return

        room.locked_exits.discard("south")
        self.state.throne_unlocked = True
        print()
        print(Color.wrap("  chmod 777 door", Color.BRIGHT_YELLOW))
        print()
        print(Color.wrap("  The ancient lock mechanism shudders.", Color.WHITE))
        print(Color.wrap("  Gears grind. Dust falls from the ceiling.", Color.WHITE))
        print(Color.wrap("  With a resonant CLUNK, the door to the throne room swings open.", Color.BRIGHT_GREEN, Color.BOLD))
        print()
        self.renderer.render_success("The throne room is now accessible to the south!")
        print()

    def _pickup(self, action: Action) -> None:
        item_name = action.first_arg()
        room      = self.state.current_room
        player    = self.state.player

        item = room.item_by_name(item_name)
        if item is None:
            self.renderer.render_error(f"No item named '{item_name}' here.")
            return

        room.remove_item(item_name)
        player.pickup(item)
        self.renderer.render_pickup(item_name)
        if item.item_type == "treasure":
            self.renderer.render_success(f"Added {item.value} gold to your score!")
        print()

    def _error(self, action: Action) -> None:
        msg = action.first_arg() or "Invalid command."
        self.renderer.render_error(msg)

    def _unknown(self, action: Action) -> None:
        verb = action.first_arg() or action.raw
        print()
        print(Color.wrap(f"  bash: {verb}: command not found", Color.RED))
        self.renderer.render_info(f"Type  help  to see available commands.")
        print()

    # ------------------------------------------------------------------ #
    # Combat helpers                                                       #
    # ------------------------------------------------------------------ #
    def _calc_player_dmg(self) -> int:
        base = self.state.player.attack
        variance = max(1, base // 5)
        return base + random.randint(-variance, variance)

    def _enemy_attacks(self, enemy) -> None:
        player = self.state.player
        dmg    = enemy.attack + random.randint(-2, 3)
        dmg    = max(1, dmg)
        actual = player.take_damage(dmg)
        self.renderer.render_player_hit(enemy.display_name, actual, player)
        if not player.is_alive():
            self.state.running = False

    def _room_entry_attacks(self) -> None:
        room   = self.state.current_room
        player = self.state.player
        living = room.living_enemies()
        if not living:
            return
        for enemy in living:
            if random.random() < 0.4:
                print(Color.wrap(f"  {enemy.display_name} lurches at you as you enter!", Color.BRIGHT_RED))
                self._enemy_attacks(enemy)
                if not player.is_alive():
                    return


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------
def get_player_name() -> str:
    print(Color.wrap("  Enter your name, adventurer: ", Color.BRIGHT_WHITE), end="", flush=True)
    try:
        name = input().strip()
    except EOFError:
        name = ""
    return name if name else "Adventurer"


def main() -> None:
    renderer = Renderer()
    renderer.print_welcome()

    name   = get_player_name()
    print()
    print(Color.wrap(f"  Welcome, {name}. The dungeon opens before you.", Color.BRIGHT_GREEN))
    print()

    player  = Player(name=name)
    dungeon = Dungeon()
    state   = GameState(player, dungeon)
    engine  = GameEngine(state, renderer)

    renderer.render_room(state.current_room, player, verbose=True)

    while state.running:
        try:
            prompt = (
                Color.wrap(f"{player.name}", Color.BRIGHT_GREEN)
                + Color.wrap("@shellbound", Color.CYAN)
                + Color.wrap(":", Color.WHITE)
                + Color.wrap(state.current_room.id, Color.BLUE)
                + Color.wrap("$ ", Color.WHITE)
            )
            raw = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            engine.handle(parse("quit"))
            break

        action = parse(raw)
        engine.handle(action)

        if not player.is_alive() and not state.won:
            renderer.render_game_over(player)
            break

    if state.won:
        renderer.render_win(player)


if __name__ == "__main__":
    main()
