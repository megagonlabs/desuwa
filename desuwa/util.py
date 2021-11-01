#!/usr/bin/env python3


from typing import Iterator, List

from pyknp import MList


def get_mlist(inf) -> Iterator[MList]:
    buf: List[str] = []
    surfs: List[str] = []
    for line in inf:
        if line == "EOS\n":
            yield MList("".join(buf))
            buf = []
            surfs = []
            continue
        buf.append(line)
        if line.startswith("@"):
            continue
        surf = line[: line.index(" ")]
        surfs.append(surf)


def tab_indent(text: str, num: int) -> str:
    return "\t" * num + text.replace("\n", "\n" + "\t" * num)


def clean_sexp(text: str) -> str:
    return text.replace("[", "(").replace("]", ")").replace("<", "(").replace(">", ")")
