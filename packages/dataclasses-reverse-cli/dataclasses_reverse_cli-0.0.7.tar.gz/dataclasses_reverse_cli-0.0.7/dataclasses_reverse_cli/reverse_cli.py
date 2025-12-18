import dataclasses
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from deprecated import deprecated


@dataclass(kw_only=True)
class ReverseCli:
    @staticmethod
    def _flatten(
        dictionary: dict[str, Any], parent_key: str = "", separator: str = "."
    ) -> dict[str, Any]:
        """
        This method takes in a dictionary `parent_key` infront of the keys of the
        dictionary.
        """
        items = []
        for key, value in dictionary.items():
            new_key = parent_key + separator + key if parent_key else key
            if isinstance(value, dict):
                items.extend(
                    ReverseCli._flatten(value, new_key, separator=separator).items()
                )
            else:
                items.append((new_key, value))
        return dict(items)

    def to_loggable_dict(self, ignore: set[str] | None = None) -> dict[str, Any]:
        if ignore is None:
            ignore = set()

        dict_values = asdict(self)

        flattened = ReverseCli._flatten(dict_values)

        # Drop the keys in ignore
        for key in ignore:
            flattened.pop(key, None)

        return flattened

    @property
    @deprecated("Use the to_loggable_dict function instead")
    def loggable_dict(self, ignore: set[str] | None = None) -> dict[str, Any]:
        """Test docstring"""
        if ignore is None:
            ignore = set()

        dict_values = asdict(self)

        # Drop the keys in ignore
        for key in ignore:
            dict_values.pop(key, None)

        return ReverseCli._flatten(dict_values)

    def to_command_string(
        self, parameter_name: str = "", ignore: set[str] | None = None
    ) -> str:
        """
        Converts a dataclass into something that can be added to a tyro.cli parsable
        command. Note that this will fail for variables that are declared as bool
        without a default value.
        :return: string of the command parsed by tyro
        """
        if ignore is None:
            ignore = set()

        if parameter_name != "":
            parameter_name += "."

        command_string = ""
        for attribute in dataclasses.fields(self):
            key_string = attribute.name.replace("_", "-")
            value = getattr(self, attribute.name)

            if f"--{parameter_name}{key_string}" in ignore:
                continue

            if isinstance(value, list) | isinstance(value, tuple):
                value_string: list[str] = []
                for element in value:
                    if isinstance(element, tuple):
                        for y in element:
                            value_string.append(
                                f'"{str(y)}"' if " " in str(y) else str(y)
                            )
                    else:
                        value_string.append(
                            f'"{str(element)}"' if " " in str(element) else str(element)
                        )

                command_string += f" --{parameter_name}{key_string} " + " ".join(
                    value_string
                )
                continue

            if isinstance(value, bool) and value is True:
                command_string += f" --{parameter_name}{key_string}"
                continue

            if isinstance(value, bool) and value is False:
                command_string += f" --{parameter_name}no-{key_string}"
                continue

            if value == "":
                command_string += f" --{parameter_name}{key_string} ''"
                continue

            if isinstance(value, ReverseCli):
                command_string += value.to_command_string(
                    parameter_name=parameter_name + str(key_string), ignore=ignore
                )
                continue

            if isinstance(value, Enum):
                command_string += f" --{parameter_name}{key_string} {value.name}"
                continue

            if isinstance(value, str):
                if " " in value:
                    value = f'"{value}"'

            command_string += f" --{parameter_name}{key_string} {value}"

        return command_string
