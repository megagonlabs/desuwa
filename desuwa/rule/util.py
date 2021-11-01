#!/usr/bin/env python3

from typing import IO, Iterator


def parse_rule_text(inf: IO) -> Iterator[str]:
    p_num = 0
    buf = ""
    for line in inf:
        line = line[: line.find(";")].strip()
        if len(line) == 0:
            continue
        p_num += line.count("(") - line.count(")")
        if p_num == 0:
            yield buf + " " + line
            buf = ""
        else:
            buf += " " + line
