#!/usr/bin/env python3
""" Build a 34 AA and 8 AA signature table from the PARAS dataset """

from argparse import ArgumentParser, FileType
from dataclasses import dataclass
from typing import IO


def main() -> None:
    """ Command line wrangling """
    parser = ArgumentParser()
    parser.add_argument("data", type=FileType('r', encoding="utf-8"),
                        help="old PARAS signature table to infer the name mappings from")
    parser.add_argument("outfile", type=FileType('w', encoding="utf-8"),
                        help="Python file to write name mappings into")
    args = parser.parse_args()

    run(args.data, args.outfile)


@dataclass
class SubstrateName:
    """ A mapping of substrate names using multiple naming conventions """
    long: str
    short: str
    norine: str

    def __str__(self) -> str:
        line = f'    SubstrateName("{self.long}", "{self.short}", "{self.norine}"),'
        if len(line) > 100:
            # Tell flake8 to ignore the long line
            line += "  # noqa: E501"
        return line


HEADER = '''\
# License: GNU Affero General Public License v3 or later
# A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.
# pylint: disable=line-too-long
""" A mapping of A-domain substrate names in multiple naming conventions """

from dataclasses import dataclass


@dataclass(frozen=True)
class SubstrateName:
    """ A mapping of substrate names using multiple naming conventions """
    long: str
    short: str
    norine: str


KNOWN_SUBSTRATES: list[SubstrateName] = [
'''

FOOTER = ''']

_LONG_TO_SUBSTRATE: dict[str, SubstrateName] = {
    sub.long: sub for sub in KNOWN_SUBSTRATES
}

_SHORT_TO_SUBSTRATE: dict[str, SubstrateName] = {
    sub.short: sub for sub in KNOWN_SUBSTRATES
}


def get_substrate_by_name(name: str) -> SubstrateName:
    """ Look up a substrate by long or short name """
    if name in _LONG_TO_SUBSTRATE:
        return _LONG_TO_SUBSTRATE[name]
    if name in _SHORT_TO_SUBSTRATE:
        return _SHORT_TO_SUBSTRATE[name]
    raise ValueError(f"Substrate {name} not found")
'''


def run(data: IO, outfile: IO) -> None:
    """ Build the signature tables"""
    substrates: dict[str, SubstrateName] = {}
    # drop the first line
    data.readline()
    for line in data:
        line = line.strip()
        parts = line.split("\t")
        assert len(parts) == 5, f"invalid line {line}"
        _, _, longs, shorts, norines = parts
        long_parts = longs.split("|")
        short_parts = shorts.split("|")
        norine_parts = norines.split("|")
        for full, short, norine in zip(long_parts, short_parts, norine_parts, strict=True):
            substrates[full] = SubstrateName(full, short, norine)

    keys = sorted(substrates.keys())

    print(HEADER, file=outfile, end="")
    for key in keys:
        print(substrates[key], file=outfile)
    print(FOOTER, file=outfile, end="")


if __name__ == "__main__":
    main()