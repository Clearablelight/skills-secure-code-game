"""
dungeon.py — Dungeon map, rooms, and connections for shellbound.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from entities import Item, Enemy, make_item, make_enemy, Color


@dataclass
class Room:
    id: str
    name: str
    short_desc: str
    long_desc: str
    exits: dict[str, str]
    enemy_names: list[str]
    item_names: list[str]
    hidden_item_names: list[str] = field(default_factory=list)
    locked_exits: set[str] = field(default_factory=set)
    ascii_art: str = ""

    enemies: list[Enemy] = field(default_factory=list, init=False, repr=False)
    items: list[Item]   = field(default_factory=list, init=False, repr=False)

    def living_enemies(self) -> list[Enemy]:
        return [e for e in self.enemies if e.is_alive()]

    def enemy_by_name(self, name: str) -> Optional[Enemy]:
        for e in self.enemies:
            if e.name == name and e.is_alive():
                return e
        return None

    def item_by_name(self, name: str) -> Optional[Item]:
        for i in self.items:
            if i.name == name and not i.hidden:
                return i
        return None

    def visible_items(self) -> list[Item]:
        return [i for i in self.items if not i.hidden]

    def hidden_items(self) -> list[Item]:
        return [i for i in self.items if i.hidden]

    def reveal_hidden(self, name: Optional[str] = None) -> list[Item]:
        revealed = []
        for item in self.items:
            if item.hidden:
                if name is None or item.name == name:
                    item.hidden = False
                    revealed.append(item)
        return revealed

    def remove_item(self, name: str) -> Optional[Item]:
        for i, item in enumerate(self.items):
            if item.name == name:
                return self.items.pop(i)
        return None

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def path(self) -> str:
        return f"/dungeon/{self.id}"


class Dungeon:
    """
    Five-room layout:

         [library]
             |
    [entrance] -- [armory]
             |
         [crypt]
             |
        [throne_room]  (locked door between crypt and throne_room)
    """

    ROOM_DEFS: list[dict] = [
        {
            "id": "entrance",
            "name": "Dungeon Entrance",
            "short_desc": "The main entrance hall. Torches flicker on damp stone walls.",
            "long_desc": (
                "You stand in the dungeon entrance. Moss creeps between ancient stone blocks.\n"
                "Water drips from the vaulted ceiling. The air smells of rot and old iron.\n"
                "Passages lead north to the library, east to the armory, and south to the crypt."
            ),
            "exits": {"north": "library", "east": "armory", "south": "crypt"},
            "enemy_names": ["goblin"],
            "item_names": ["health_potion"],
            "hidden_item_names": [],
            "ascii_art": (
                "  ___________\n"
                " |  ENTRANCE  |\n"
                " |  ~~~~~~~~~  |\n"
                " | torch  torch|\n"
                " |_____________|"
            ),
        },
        {
            "id": "armory",
            "name": "The Armory",
            "short_desc": "Racks of ancient weapons line the walls. Smells of oil and iron.",
            "long_desc": (
                "The armory is lined with weapon racks, most empty or rusted beyond use.\n"
                "A single well-maintained sword gleams on a stand. A skeleton guards it.\n"
                "The exit leads west back to the entrance."
            ),
            "exits": {"west": "entrance"},
            "enemy_names": ["skeleton"],
            "item_names": ["sword"],
            "hidden_item_names": [],
            "ascii_art": (
                "  ___________\n"
                " |   ARMORY   |\n"
                " | /\\ /\\ /\\  |\n"
                " | || || ||  |\n"
                " |_____________|"
            ),
        },
        {
            "id": "library",
            "name": "The Library",
            "short_desc": "Shelves packed with crumbling tomes. A skeleton browses the stacks.",
            "long_desc": (
                "Towering shelves sag under the weight of ancient books.\n"
                "Dust motes drift through pale light filtering from cracks above.\n"
                "A scroll and a hidden key wait among the tomes.\n"
                "The exit leads south back to the entrance."
            ),
            "exits": {"south": "entrance"},
            "enemy_names": ["skeleton"],
            "item_names": ["scroll", "gold"],
            "hidden_item_names": ["key"],
            "ascii_art": (
                "  ___________\n"
                " |  LIBRARY   |\n"
                " | ||| ||| ||||\n"
                " | ||| ||| ||||\n"
                " |_____________|"
            ),
        },
        {
            "id": "crypt",
            "name": "The Crypt",
            "short_desc": "Stone sarcophagi line the walls. The air is ice-cold.",
            "long_desc": (
                "The crypt is eerily silent save for the creak of old stone.\n"
                "Stone coffins line every wall, their lids carved with forgotten faces.\n"
                "A goblin lurks in the shadows. A health potion sits on a tomb ledge.\n"
                "The exit north leads back to the entrance.\n"
                "A heavy door to the south bears an ancient lock — the throne room lies beyond."
            ),
            "exits": {"north": "entrance", "south": "throne_room"},
            "locked_exits": {"south"},
            "enemy_names": ["goblin"],
            "item_names": ["health_potion"],
            "hidden_item_names": [],
            "ascii_art": (
                "  ___________\n"
                " |   CRYPT    |\n"
                " |[_][_][_][_]|\n"
                " |[_][_][_][_]|\n"
                " |_____________|"
            ),
        },
        {
            "id": "throne_room",
            "name": "The Throne Room",
            "short_desc": "A vast chamber. The dragon coils around a crumbling throne.",
            "long_desc": (
                "The throne room is immense. A cracked obsidian throne dominates the far wall.\n"
                "Ancient banners hang in tatters from iron chains.\n"
                "Coiled atop a mound of gold and bones, the dragon regards you with one molten eye.\n"
                "  *** This is where the legend ends — or you do. ***\n"
                "The only exit leads north back to the crypt."
            ),
            "exits": {"north": "crypt"},
            "enemy_names": ["dragon"],
            "item_names": ["gold"],
            "hidden_item_names": [],
            "ascii_art": (
                "  _____________\n"
                " | THRONE ROOM  |\n"
                " |    ,   ,     |\n"
                " |   ((_O_))    |\n"
                " |  >>=====>>   |\n"
                " |_______________|"
            ),
        },
    ]

    def __init__(self) -> None:
        self.rooms: dict[str, Room] = {}
        self._build()

    def _build(self) -> None:
        for rd in self.ROOM_DEFS:
            room = Room(
                id=rd["id"],
                name=rd["name"],
                short_desc=rd["short_desc"],
                long_desc=rd["long_desc"],
                exits=rd["exits"],
                enemy_names=rd["enemy_names"],
                item_names=rd["item_names"],
                hidden_item_names=rd.get("hidden_item_names", []),
                locked_exits=set(rd.get("locked_exits", [])),
                ascii_art=rd.get("ascii_art", ""),
            )
            for ename in rd["enemy_names"]:
                room.enemies.append(make_enemy(ename))
            for iname in rd["item_names"]:
                item = make_item(iname)
                item.hidden = False
                room.items.append(item)
            for iname in rd.get("hidden_item_names", []):
                item = make_item(iname)
                item.hidden = True
                room.items.append(item)
            self.rooms[room.id] = room

    def get_room(self, room_id: str) -> Room:
        return self.rooms[room_id]

    def starting_room(self) -> Room:
        return self.rooms["entrance"]

    def find_item_everywhere(self, item_name: str) -> list[tuple[Room, Item]]:
        results = []
        for room in self.rooms.values():
            for item in room.items:
                if item.name == item_name:
                    results.append((room, item))
        return results
