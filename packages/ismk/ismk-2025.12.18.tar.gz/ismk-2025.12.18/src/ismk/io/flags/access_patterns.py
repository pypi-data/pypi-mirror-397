from enum import Enum
from ismk.io import flag
from ismk.io.flags import FlaggableItemOrIterable


STORE_KEY = "access_pattern"


class AccessPattern(Enum):
    RANDOM = "random"
    SEQUENTIAL = "sequential"
    MULTI = "multi"

    def __str__(self):
        return self.value


class AccessPatternFactory:
    @classmethod
    def random(cls, item: FlaggableItemOrIterable):
        return flag(item, STORE_KEY, AccessPattern.RANDOM)

    @classmethod
    def sequential(cls, item: FlaggableItemOrIterable):
        return flag(item, STORE_KEY, AccessPattern.SEQUENTIAL)

    @classmethod
    def multi(cls, item: FlaggableItemOrIterable):
        return flag(item, STORE_KEY, AccessPattern.MULTI)
