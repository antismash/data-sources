#!/usr/bin/env python3
""" Build a 34 AA and 8 AA signature table from the PARAS dataset """

from argparse import ArgumentParser, FileType
from collections import defaultdict
from dataclasses import dataclass
from typing import IO, Optional

from antismash.common.test.helpers import DummyAntismashDomain
from antismash.config import build_config
from antismash.modules.nrps_pks.signatures import get_a_dom_signatures

from name_mappings import get_substrate_by_name


def main() -> None:
    """ Command line wrangling """
    parser = ArgumentParser()
    parser.add_argument("data", type=FileType('r', encoding="utf-8"),
                        help="PARAS datafile to load")
    parser.add_argument("outfile", type=FileType('w', encoding="utf-8"),
                        help="Signature table file to write")
    args = parser.parse_args()

    build_config([])

    run(args.data, args.outfile)


@dataclass
class TempSignature:
    """ A signature as read from a PARAS data line """
    aa10: str
    aa34: str
    name: str
    ids: set[str]


@dataclass
class Signature:
    """ A signature for the signature table """
    aa10: str
    aa34: str
    names: set[str]
    winners: set[str]
    ids: set[str]

    def __str__(self) -> str:
        longs: list[str] = []
        shorts: list[str] = []
        norines: list[str] = []
        for name in self.names:
            sig_name = get_substrate_by_name(name)
            longs.append(sig_name.long)
            shorts.append(sig_name.short)
            norines.append(sig_name.norine)

        winners = list(map(lambda x: get_substrate_by_name(x).short, self.winners))

        return "\t".join([
            self.aa10,
            self.aa34,
            "|".join(longs),
            "|".join(shorts),
            "|".join(norines),
            "|".join(winners),
            "|".join(self.ids),
        ])


def run(data: IO, outfile: IO) -> None:
    """ Build the signature table"""
    signatures: dict[str, Signature] = {}
    table: dict[str, list[TempSignature]] = defaultdict(list)

    lines = parse_data_lines(data)

    skipped = 0
    for line in lines:
        for specificity in line.specificity.split("|"):
            aa10, aa34 = extract_signatures(line.sequence, line.domain_id)
            if not (aa10 and aa34):
                continue
            if "-" in aa10:
                skipped += 1
                continue
            table[aa34].append(
                TempSignature(aa10, aa34, specificity, set(line.domain_id.split("|")))
            )

    print("skipped", skipped)

    for aa34, temp_sigs in table.items():
        if len(temp_sigs) == 1:
            winner = temp_sigs[0]
            signatures[aa34] = Signature(
                winner.aa10, winner.aa34, {winner.name}, {winner.name}, winner.ids)
            continue

        signatures[aa34] = pick_winning_substrates(aa34, temp_sigs)

    for signature in signatures.values():
        print(signature, file=outfile)


def pick_winning_substrates(aa34: str, temp_sigs: list[TempSignature]) -> Signature:
    """ Pick the substrate(s) that occur(s) most often as the winner(s) """
    options: dict[str, list[TempSignature]] = defaultdict(list)
    for temp_sig in temp_sigs:
        options[temp_sig.name].append(temp_sig)

    sorted_sigs = sorted(options.items(), key=lambda x: len(x[1]), reverse=True)
    winning_sigs = options[sorted_sigs[0][0]]
    for key, sigs in sorted_sigs[1:]:
        if len(sigs) < len(sorted_sigs[0][1]):
            break
        winning_sigs.extend(options[key])

    names: set[str] = set()
    ids: set[str] = set()
    aa10 = temp_sigs[0].aa10
    for sig in winning_sigs:
        names.add(sig.name)
        ids.update(sig.ids)
    return Signature(aa10, aa34, names, names, ids)


@dataclass
class ParasLine:
    """ A line from the PARAS datafile """
    domain_id: str
    sequence: str
    specificity: str

    @classmethod
    def from_line(cls, line: str) -> "ParasLine":
        """ Parse fromt he PARAS datafile table """
        line = line.strip()
        parts = line.split("\t")
        assert len(parts) == 3, f"Bad line {line}"
        return cls(parts[0], parts[1], parts[2])


def parse_data_lines(data: IO) -> list[ParasLine]:
    """ Parse the PARAS datafile """
    # skip the header line
    data.readline()
    return [ParasLine.from_line(line) for line in data]


def extract_signatures(sequence: str, domain_id: str) -> tuple[Optional[str], Optional[str]]:
    """ Extract the 34 AA and 10 AA signatures from an A domain sequence """
    domain = DummyAntismashDomain(domain_id=domain_id)
    domain._translation = sequence
    return get_a_dom_signatures(domain)


if __name__ == "__main__":
    main()
