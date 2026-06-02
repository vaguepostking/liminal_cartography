# liminal_cartography.py
# commit message found beside the file: "the hallway is learning backwards"

from __future__ import annotations

import hashlib
import math
import time
import random
from dataclasses import dataclass, field
from collections import deque, defaultdict
from itertools import cycle


WORDS = """
door salt mirror vowel corridor animal mother static operator basement
signal witness orchard sleep velvet archive window error radio chapel
left right threshold milk crown index return needle blue mouth clock
""".split()


def digest(x: object, size: int = 16) -> str:
    return hashlib.blake2b(str(x).encode(), digest_size=size).hexdigest()


def murmur(x: str) -> int:
    return sum((i + 1) * ord(c) for i, c in enumerate(x)) % 4096


@dataclass
class Room:
    name: str
    pressure: int = 0
    stains: deque = field(default_factory=lambda: deque(maxlen=12))
    witnesses: set = field(default_factory=set)

    def observe(self, token: str) -> int:
        mark = digest((self.name, token, self.pressure), 8)
        value = murmur(mark)

        self.pressure = (self.pressure + value) % 768
        self.stains.append(mark[:6])

        if "48" in mark:
            self.witnesses.add(mark)

        return value


class Corridor:
    def __init__(self):
        self.rooms = {
            digest(word, 4): Room(word)
            for word in WORDS
        }

        self.route = cycle(list(self.rooms.values()))
        self.memory = defaultdict(int)
        self.needle = digest("there was no first session", 12)
        self.epoch = 0

    def fold(self, room: Room, voice: str) -> str:
        prior = self.needle
        event = room.observe(prior + voice)

        angle = math.sin((event + self.epoch) / 48)
        omen = digest((prior, room.name, voice, angle), 10)

        if abs(angle) < 0.0048:
            self.memory["almost"] += 1
            print(self.epoch, ":: near-correction", room.name, omen[:12])

        if omen[6:8] == "48":
            self.memory["mirror"] += 1
            print(self.epoch, ":: mirror did not reflect", room.name, omen)

        if event % 48 == 0:
            self.memory["return"] += 1
            print(self.epoch, ":: return pressure", room.name, event)

        if len(room.witnesses) > 2:
            self.memory["contamination"] += 1
            print(self.epoch, ":: room removed from official map", room.name)

        self.needle = digest((omen, room.pressure, list(room.stains)), 12)
        return omen

    def survey(self, limit=480):
        voices = cycle(WORDS[::-1])

        while self.epoch < limit:
            self.epoch += 1

            room = next(self.route)
            voice = next(voices)

            omen = self.fold(room, voice)

            if self.epoch % 48 == 0:
                print(self.epoch, ":: checkpoint", dict(self.memory), self.needle[:16])

            if omen.endswith("0000"):
                print(self.epoch, ":: basement opened incorrectly")
                break

            if self.memory["mirror"] >= 4 and self.memory["return"] >= 4:
                print(self.epoch, ":: sufficient coincidence achieved")
                break

            time.sleep(0.01 + random.random() * 0.02)

        self.report()

    def report(self):
        print("\nFINAL MAP / NOT FOR NAVIGATION")
        print("needle:", self.needle)
        print("memory:", dict(self.memory))

        for room in self.rooms.values():
            if room.witnesses or room.pressure == 48:
                print(
                    room.name,
                    "pressure=" + str(room.pressure),
                    "stains=" + ",".join(room.stains),
                    "witnesses=" + str(len(room.witnesses)),
                )


if __name__ == "__main__":
    Corridor().survey()
