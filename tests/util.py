#!/usr/bin/env python3

from pathlib import Path
from typing import List, Optional

from pyknp import MList


class DummyJumanpp(object):
    def __init__(self, inpath: Path):
        self.surf2parsed = {}

        with inpath.open() as inf:
            buf: List[str] = []
            surfs: List[str] = []
            for line in inf:
                if line == 'EOS\n':
                    self.surf2parsed[''.join(surfs)] = ''.join(buf)
                    buf = []
                    surfs = []
                    continue
                buf.append(line)
                if line.startswith('@'):
                    continue
                surf = line[:line.index(' ')]
                surfs.append(surf)

    def get(self, sentence: str) -> Optional[MList]:
        parsed = self.surf2parsed.get(sentence)
        if parsed:
            return MList(parsed)
        return None
