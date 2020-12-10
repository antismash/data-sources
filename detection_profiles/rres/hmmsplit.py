#!/usr/bin/env python3
"""Take a multi-profile hmm file and split it into one file per profile."""

import argparse
from dataclasses import dataclass, field
import sys
from typing import List


# Obtained from antiSMMASH using the command
# grep -B1 "CATEGORY RiPP" antismash/detection/hmm_detection/cluster_rules/strict.txt | grep RULE | cut -d" " -f2 | sort
RIPP_CLASSES = [
    "bacteriocin",
    "bottromycin",
    "cyanobactin",
    "fungal-RiPP",
    "fused",
    "head_to_tail",
    "lanthidin",
    "lanthipeptide",
    "LAP",
    "lassopeptide",
    "lipolanthine",
    "microviridin",
    "proteusin",
    "RaS-RiPP",
    "sactipeptide",
    "thioamitides",
    "thiopeptide",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hmmfile", type=argparse.FileType(),
                        help="multi-profile HMM file to split")
    parser.add_argument("-r", "--rule-file", type=argparse.FileType(mode="a"), default=sys.stderr,
                        help="Rule file to append the rule to (default: stderr)")
    parser.add_argument("-D", "--details", type=argparse.FileType(mode="a"), default=sys.stdout,
                        help="hmmdetails file to append the file info to (default: stdout)")
    args = parser.parse_args()

    profiles = sorted(parse(args.hmmfile), key=lambda x: x.accession)
    write(profiles)


@dataclass
class Profile:
    """Class for keeping track of the individual HMM profiles."""
    accession: str = field(default="")
    description: str = field(default="")
    name: str = field(default="")
    lines: List[str] = field(default_factory=list)


def parse(infile) -> List[Profile]:
    profiles: List[Profile] = []
    line = infile.readline()
    current = Profile()
    while line:
        current.lines.append(line)
        if line.startswith("ACC"):
            current.accession = line.split()[-1].split(".")[0]
        elif line.startswith("NAME"):
            current.name = line.split()[-1]
        elif line.startswith("DESC"):
            current.description = line[6:-1]
        elif line == "//\n":
            profiles.append(current)
            current = Profile()
        line = infile.readline()

    return profiles


def write(profiles: List[Profile]) -> None:
    names: List[str] = []
    for profile in profiles:
        names.append(profile.name)
        with open(f"{profile.accession}.hmm", "w") as handle:
            handle.writelines(profile.lines)
        print(profile.name, profile.description, "25", f"{profile.accession}.hmm", sep="\t")

    print(f"""RULE RRE-containing
    CATEGORY RiPP
    COMMENT RRE-element containing cluster
    SUPERIORS {", ".join(RIPP_CLASSES)}
    CUTOFF 10
    NEIGHBOURHOOD 10
    CONDITIONS {" or ".join(names)}
""")


if __name__ == "__main__":
    main()
