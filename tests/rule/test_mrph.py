#!/usr/bin/env python3


import unittest
from dataclasses import dataclass
from pathlib import Path

from pyknp import MList
from sexpdata import loads

import tests.util
from desuwa.rule.mrph import MrphsRule


@dataclass
class Data(object):
    rule_text: str
    forward: bool
    gold: bool
    position: int = 0
    span_start: int = 0
    span_end: int = 2


class TestMrphsRule(unittest.TestCase):
    def setUp(self):
        path_parsed = Path(__file__).parent.joinpath('..', 'data', 'parsed.jumanpp')
        self.jumanpp = tests.util.DummyJumanpp(path_parsed)

    def test_rule(self):
        mytest = '無停止だ'
        mlist: MList = self.jumanpp.get(mytest)

        testcases = [
            Data(rule_text='( ?* )',
                 forward=True,
                 gold=True,
                 ),
            Data(rule_text='( (接頭辞) )',
                 forward=True,
                 gold=False,
                 ),

            Data(rule_text='( (接頭辞) )',
                 forward=True,
                 gold=False,
                 position=1,
                 ),

            Data(rule_text='( (接頭辞) ?* )',
                 forward=True,
                 gold=True,
                 ),

            Data(rule_text='( (接頭辞) ? )',
                 forward=True,
                 gold=False,
                 ),

            Data(rule_text='( (接頭辞) (*) (判定詞) )',
                 forward=True,
                 gold=True,
                 ),

            Data(rule_text='( (接頭辞) ?* (判定詞) )',
                 forward=True,
                 gold=True,
                 ),

            Data(rule_text='( (接頭辞) (*) (*) (判定詞) )',
                 forward=True,
                 gold=False,
                 ),

            Data(rule_text='( (接頭辞) (*) (*) (*) )',
                 forward=True,
                 gold=False,
                 ),

            Data(rule_text='( (名詞) )',
                 forward=True,
                 gold=False,
                 ),

            Data(rule_text='( ?* (名詞) )',
                 forward=True,
                 gold=False,
                 ),

            Data(rule_text='( ?* (判定詞) )',
                 forward=True,
                 gold=True,
                 ),

            Data(rule_text='( (判定詞) )',
                 forward=False,
                 gold=False,
                 position=2,
                 ),

            Data(rule_text='( (判定詞) )',
                 forward=False,
                 gold=False,
                 position=2,
                 span_start=0,
                 span_end=2,
                 ),

            Data(rule_text='( ?* (判定詞) )',
                 forward=False,
                 gold=True,
                 position=2,
                 ),

            Data(rule_text='( ?* (接頭辞) ?*)',
                 forward=False,
                 gold=True,
                 position=2,
                 ),

            Data(rule_text='( (ダミー) ?*)',
                 forward=False,
                 gold=False,
                 position=2,
                 ),

            Data(rule_text='( (接頭辞) ?*)',
                 forward=False,
                 gold=True,
                 position=2,
                 ),

            Data(rule_text='((接頭辞) ?* (判定詞))',
                 forward=False,
                 gold=True,
                 position=2,
                 ),

            Data(rule_text='(?* (接頭辞) ?* (判定詞))',
                 forward=False,
                 gold=True,
                 position=2,
                 ),

        ]

        for idx, tc in enumerate(testcases):
            r = MrphsRule(loads(tc.rule_text), tc.forward)
#             print(f'##{idx}\t{tc.rule_text}\n', r)
            self.assertEqual(tc.gold,
                             r.match(mlist, tc.position, tc.span_start, tc.span_end))


if __name__ == '__main__':
    unittest.main()
