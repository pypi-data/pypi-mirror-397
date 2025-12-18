import unittest
from dataclasses import dataclass

from dataclasses_reverse_cli.reverse_cli import ReverseCli


@dataclass(kw_only=True)
class Parameters(ReverseCli):
    a: int
    b: str
    c: bool
    d: list[int]
    e: list[tuple[float, float]]


@dataclass(kw_only=True)
class Nested(ReverseCli):
    a: int
    b: Parameters


class TestLogableDict(unittest.TestCase):
    def test_logable_dict(self):
        parameters = Nested(
            a=1, b=Parameters(a=1, b="2", c=True, d=[3, 4], e=[(0.1, 0.2)])
        )
        self.assertEqual(
            parameters.to_loggable_dict(),
            {
                "a": 1,
                "b.a": 1,
                "b.b": "2",
                "b.c": True,
                "b.d": [3, 4],
                "b.e": [(0.1, 0.2)],
            },
        )

    def test_ignore(self):
        parameters = Nested(
            a=1, b=Parameters(a=1, b="2", c=True, d=[3, 4], e=[(0.1, 0.2)])
        )
        self.assertEqual(
            parameters.to_loggable_dict(ignore=set(["b.b"])),
            {"a": 1, "b.a": 1, "b.c": True, "b.d": [3, 4], "b.e": [(0.1, 0.2)]},
        )

        self.assertEqual(
            parameters.to_loggable_dict(ignore=set(["b.b", "b.d", "b.e"])),
            {"a": 1, "b.a": 1, "b.c": True},
        )
