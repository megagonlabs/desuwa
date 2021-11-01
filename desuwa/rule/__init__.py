#!/usr/bin/env python3

import collections
import dataclasses
import json
from typing import DefaultDict, List, Optional, Set

from pyknp import MList


class Features:
    def __init__(self, _vals: Optional[List[str]] = None):
        self.values: Set[str] = set()
        self._kvs: DefaultDict[str, Set] = collections.defaultdict(set)
        if _vals:
            for v in _vals:
                self.add(v)

    def __str__(self) -> str:
        return json.dumps(list(self.values), sort_keys=True, ensure_ascii=False)

    def add(self, name: str):
        _sep = name.find(":")
        if _sep >= 0:
            _key = name[:_sep]
            _val = name[_sep + 1 :]
            self._kvs[_key].add(_val)
        self.values.add(name)

    def __contains__(self, val: str) -> bool:
        if val in self._kvs:
            return True
        return val in self.values

    def discard(self, name: str):
        if name in self.values:
            self.values.remove(name)
            _sep = name.find(":")
            if _sep >= 0:
                _key = name[:_sep]
                _val = name[_sep + 1 :]
                self._kvs[_key].remove(_val)
                if len(self._kvs[_key]) == 0:
                    del self._kvs[_key]
            return

        vs = self._kvs.get(name)
        if vs:
            for v in vs:
                self.values.discard(f"{name}:{v}")
            del self._kvs[name]

    def get_keys(self) -> Set[str]:
        r: Set[str] = set()
        r.update(self.values)
        r.update(set(self._kvs.keys()))
        return r

    def get_by_key(self, key: str) -> Optional[Set]:
        return self._kvs.get(key)


@dataclasses.dataclass
class Tag(list):
    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.fs: Features = Features()

    def __str__(self) -> str:
        return "".join([m.midasi for m in self])


_TAG_PREFIX = "+\t"


@dataclasses.dataclass
class Tags(list):
    def __init__(self, mlist: MList, indices: List[int]):
        self.mlist = mlist
        self._indices: List[int] = sorted(indices)
        for i, m in enumerate(mlist):
            if i in self._indices:
                self.append(Tag())
            self[-1].append(m)

        # initialize
        # TODO mrphのfsからコピー?

    def get_first_m_index(self, tag_index: int) -> int:
        return self._indices[tag_index]

    def get_last_m_index(self, index: int) -> int:
        if index == len(self._indices) - 1:
            return len(self.mlist) - 1
        return self._indices[index + 1] - 1

    def __str__(self) -> str:
        return "│".join([str(t) for t in self])

    def dumps(self: List[Tag]) -> str:
        out = ""

        tag: Tag
        for tag in self:
            _tmp = json.dumps(list(tag.fs.values), sort_keys=True, ensure_ascii=False)
            out += f"{_TAG_PREFIX}{_tmp}\n"
            for m in tag:
                tmp = json.dumps(list(m.fs.values), sort_keys=True, ensure_ascii=False)
                out += f"""{m.spec()[:-1]}\t{tmp}\n"""
        out += "EOS\n"
        return out


def loads_tags(text: str) -> Tags:
    tags_fss: List[Features] = []
    mrph_fss: List[Features] = []
    indices = []
    idx = 0
    sent = ""
    for line in text.split("\n"):
        if line == "EOS":
            break
        if line.startswith(_TAG_PREFIX):
            indices.append(idx)
            info = json.loads(line[len(_TAG_PREFIX) :])
            tags_fss.append(Features(info))
        else:
            mtext, mfs = line.rsplit("\t", 1)
            sent += mtext + "\n"
            mrph_fss.append(Features(json.loads(mfs)))
            idx += 1

    mlist = MList(sent)
    for mrph, mrph_fs in zip(mlist, mrph_fss):
        mrph.fs = mrph_fs

    tags = Tags(mlist, indices)
    assert len(tags) == len(tags_fss)
    for tag, ti in zip(tags, tags_fss):
        tag.fs = ti
    return tags
