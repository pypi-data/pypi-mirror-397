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
class Parameters_strings(ReverseCli):
    a: str
    b: list[str]


@dataclass(kw_only=True)
class Nested(ReverseCli):
    a: int
    b: Parameters


class TestReverseCli(unittest.TestCase):
    def test_reverse_cli(self) -> None:
        parameters = Parameters(a=1, b="2", c=True, d=[3, 4], e=[(0.1, 0.2)])
        self.assertEqual(
            parameters.to_command_string(), " --a 1 --b 2 --c --d 3 4 --e 0.1 0.2"
        )

    def test_nested(self) -> None:
        parameters = Nested(
            a=1, b=Parameters(a=1, b="2", c=True, d=[3, 4], e=[(0.1, 0.2)])
        )
        self.assertEqual(
            parameters.to_command_string(),
            " --a 1 --b.a 1 --b.b 2 --b.c --b.d 3 4 --b.e 0.1 0.2",
        )

    def test_ignore(self) -> None:
        parameters = Nested(
            a=1, b=Parameters(a=1, b="2", c=True, d=[3, 4], e=[(0.1, 0.2)])
        )
        self.assertEqual(
            parameters.to_command_string(ignore=set(["--b.b"])),
            " --a 1 --b.a 1 --b.c --b.d 3 4 --b.e 0.1 0.2",
        )

        self.assertEqual(
            parameters.to_command_string(ignore=set(["--b.b", "--a"])),
            " --b.a 1 --b.c --b.d 3 4 --b.e 0.1 0.2",
        )

    def test_spaced_string(self) -> None:
        parameters = Parameters_strings(
            a="solar panel",
            b=["one", "two three"],
        )
        self.assertEqual(
            parameters.to_command_string(),
            ' --a "solar panel" --b one "two three"',
        )
