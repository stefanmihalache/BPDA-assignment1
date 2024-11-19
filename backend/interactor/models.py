from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Rarity(Enum):
    COMMON = 0
    RARE = 1
    EPIC = 2
    LEGENDARY = 3

    @staticmethod
    def from_int(value: int):
        try:
            return Rarity(value)
        except ValueError:
            raise ValueError("Invalid integer for Rarity")


class Class(Enum):
    WARRIOR = 0
    MAGE = 1
    ROGUE = 2
    PRIEST = 3
    HUNTER = 4
    WARLOCK = 5
    SHAMAN = 6
    DRUID = 7
    PALADIN = 8

    @staticmethod
    def from_int(value: int):
        try:
            return Class(value)
        except ValueError:
            raise ValueError("Invalid integer for Class")


class Power(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

    @staticmethod
    def from_int(value: int):
        try:
            return Power(value)
        except ValueError:
            raise ValueError("Invalid integer for Power")


@dataclass
class CardProperties:
    class_: Optional[Class] = None
    rarity: Optional[Rarity] = None
    power: Optional[Power] = None

    @staticmethod
    def new(class_: int, rarity: int, power: int):
        try:
            return CardProperties(
                class_=Class.from_int(class_) if class_ is not None else None,
                rarity=Rarity.from_int(rarity) if rarity is not None else None,
                power=Power.from_int(power) if power is not None else None,
            )
        except ValueError as e:
            raise ValueError(f"Error creating CardProperties: {e}")

    def to_list(self):

        return [self.class_, self.rarity, self.power]

    def __str__(self):
        # String representation for CardProperties
        class_name = Class(self.class_) if self.class_ else "None"
        rarity_name = Rarity(self.rarity) if self.rarity else "None"
        power_name = Power(self.power) if self.power else "None"

        return f"Card Properties: Class = {class_name}, Rarity = {rarity_name}, Power = {power_name}"
