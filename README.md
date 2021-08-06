
# Desuwa

[![PyPI version](https://badge.fury.io/py/desuwa.svg)](https://badge.fury.io/py/desuwa)
[![Python Versions](https://img.shields.io/pypi/pyversions/desuwa.svg)](https://pypi.org/project/desuwa/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Downloads](https://pepy.tech/badge/desuwa/week)](https://pepy.tech/project/desuwa)

[![CircleCI](https://circleci.com/gh/megagonlabs/desuwa.svg?style=svg&circle-token=b10ac94d6822fadf276297d457cf219ba1bea7f6)](https://app.circleci.com/pipelines/github/megagonlabs/desuwa)
[![CodeQL](https://github.com/megagonlabs/desuwa/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/megagonlabs/desuwa/actions/workflows/codeql-analysis.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/b8277e89862471dcf827/maintainability)](https://codeclimate.com/github/megagonlabs/desuwa/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/b8277e89862471dcf827/test_coverage)](https://codeclimate.com/github/megagonlabs/desuwa/test_coverage)
[![markdownlint](https://img.shields.io/badge/markdown-lint-lightgrey)](https://github.com/markdownlint/markdownlint)
[![jsonlint](https://img.shields.io/badge/json-lint-lightgrey)](https://github.com/dmeranda/demjson)
[![yamllint](https://img.shields.io/badge/yaml-lint-lightgrey)](https://github.com/adrienverge/yamllint)

Feature annotator to morphemes and phrases based on KNP rule files (pure-Python)

## Quick Start

Desuwa exploits [Juman++](https://github.com/ku-nlp/jumanpp) outputs.

```console
$ pip install desuwa
$ echo '歌うのは楽しいですわ' | jumanpp | desuwa
+	["&表層:付与", "連体修飾", "用言:動"]
歌う うたう 歌う 動詞 2 * 0 子音動詞ワ行 12 基本形 2 "代表表記:歌う/うたう ドメイン:文化・芸術;レクリエーション"	["タグ単位始", "形態素連結-数詞", "固有修飾", "活用語", "文頭", "文節始", "Ｔ連体修飾", "ドメイン:文化・芸術;レクリエーション", "Ｔ固有付属", "内容語", "Ｔ固有末尾", "自立"]
+	["受けNONE", "外の関係", "形副名詞", "助詞", "Ｔ連用", "ハ", "タグ単位受:-1"]
の の の 名詞 6 形式名詞 8 * 0 * 0 NIL	["タグ単位始", "Ｔ動連用名詞化前文脈", "形態素連結-数詞", "固有修飾", "形副名詞", "特殊非見出語", "名詞相当語", "Ｔ固有付属", "付属", "内容語", "Ｔ固有末尾"]
は は は 助詞 9 副助詞 2 * 0 * 0 NIL	["形態素連結-数詞", "固有修飾", "Ｔ固有付属", "付属", "Ｔ固有末尾"]
+	["&表層:付与", "用言:形", "連体修飾", "助詞"]
楽しい たのしい 楽しい 形容詞 3 * 0 イ形容詞イ段 19 基本形 2 "代表表記:楽しい/たのしい"	["タグ単位始", "形態素連結-数詞", "固有修飾", "活用語", "文節始", "Ｔ連体修飾", "Ｔ固有付属", "内容語", "Ｔ固有末尾", "自立"]
です です です 助動詞 5 * 0 無活用型 26 基本形 2 NIL	["形態素連結-数詞", "固有修飾", "活用語", "Ｔ連体修飾", "Ｔ固有付属", "付属", "Ｔ固有末尾"]
わ わ わ 助詞 9 終助詞 4 * 0 * 0 NIL	["形態素連結-数詞", "固有修飾", "文末", "表現文末", "Ｔ固有付属", "付属", "Ｔ固有末尾"]
EOS

$ echo '歌うのは楽しいですわ' | jumanpp | desuwa | desuwa --predicate
歌う	歌う/うたう	1	動
楽しいですわ	楽しい/たのしい	1	形

$ echo '歌うのは楽しいですわ' | jumanpp | desuwa --segment
歌う│のは│楽しいですわ
```

## Note

Desuwa is currently confirmed to work with the following rule files.

- ``mrph_filter.rule``
- ``mrph_basic.rule``
- ``bnst_basic.rule``

## License

Apache License 2.0 except for rules files in [desuwa/knp_rules](desuwa/knp_rules) imported from [KNP](https://github.com/ku-nlp/knp)
