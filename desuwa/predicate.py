#!/usr/bin/env python3

from typing import Iterator

from pyknp import Morpheme

from desuwa.rule import Tags


def _get_pred(m: Morpheme):
    _sufs = m.fs.get_by_key("用言見出接辞")
    tok = m.repname
    if len(tok) == 0:
        tok = f"{m.genkei}/{m.genkei}"
    if _sufs:
        return f"""{tok}~{'|'.join(list(_sufs))}"""
    return tok


def parse(tags: Tags) -> Iterator[str]:
    for tag in tags:
        pred_type_set = tag.fs.get_by_key("用言")
        if pred_type_set is None:
            continue
        pred_type = "".join(list(pred_type_set))

        head_idx = 0
        for midx, m in enumerate(tag):
            if "内容語" in m.fs or "準内容語" in m.fs:
                head_idx = midx
                break

        reps = []
        _found_start = False
        for midx, m in enumerate(tag):
            if midx == len(tag) - 1:
                break
            if midx >= head_idx:
                break

            if "Ｔ用言見出←" in tag[midx + 1].fs:
                if _found_start:
                    tag[midx + 1].fs.add("用言表記先頭")
                    _found_start = True
                reps.append(_get_pred(m))
        if not _found_start:
            tag[head_idx].fs.add("用言表記先頭")
            reps.append(_get_pred(tag[head_idx]))

        last_idx = head_idx
        now_idx = head_idx
        for m in tag[head_idx:]:
            if "Ｔ用言見出→" not in m.fs:
                break
            now_idx += 1
            if now_idx >= len(tag) - 1:
                break

            if tag[now_idx].hinsi == "助詞":
                continue
            reps.append(_get_pred(tag[now_idx]))
            last_idx = now_idx
        tag[last_idx].fs.add("用言表記末尾")

        #         yield f'\n{tag} {tag.fs}'
        #         for m in tag:
        #             yield f'\t{m.midasi} {m.fs}'
        yield f"""{tag}\t{'+'.join(reps)}\t{len(reps)}\t{pred_type}"""
