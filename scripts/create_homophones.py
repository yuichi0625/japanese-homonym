from __future__ import annotations

import collections
import dataclasses
import functools
import pathlib
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union

import fugashi
import regex
import tqdm
from absl import app
from absl import flags
from absl import logging

FLAGS = flags.FLAGS
flags.DEFINE_string(
    'input_dir', default='text', help='WikiExtractorの出力フォルダ', short_name='i'
)
flags.DEFINE_string(
    'output_dir', default='homophones', help='同音異字を出力するフォルダ', short_name='o'
)

KATAKANA_REGEX = regex.compile(r'\p{Script=Katakana}')
LATIN_REGEX = regex.compile(r'\p{Script=Latin}')

tagger = fugashi.Tagger('-Owakati')


@dataclasses.dataclass(frozen=True)
@functools.total_ordering
class Word:
    surface: str
    pos: str

    def __eq__(self, other: Word):
        return all(getattr(self, var) == getattr(other, var) for var in vars(self))

    def __lt__(self, other: Word):
        return self.surface < other.surface


def extract_homophones(input_dir: pathlib.Path) -> Dict[str, List[Word]]:
    """input_dir内の全ファイルから同音異字を抽出する

    Args:
        input_dir (pathlib.Path): 抽出元のファイルが格納されたフォルダ

    Returns:
        Dict[str, List[str]]: 読み仮名をキーとした同音異字
    """
    kana2words = collections.defaultdict(set)
    # WikiExtractorの出力ファイルには拡張子がついていないため
    file_paths = [path for path in input_dir.rglob('*') if path.is_file()]
    for file_path in tqdm.tqdm(file_paths):
        for text in readline(file_path):
            for word in tagger(text):
                katakana = word.feature.kana
                if katakana is None or katakana == '*':
                    continue
                hiragana = kata2hira(katakana)
                # 読み仮名orアルファベットの場合は同音異字としてカウントしない
                if (
                    word.surface == katakana
                    or word.surface == hiragana
                    or LATIN_REGEX.search(word.surface)
                ):
                    continue
                kana2words[hiragana].add(
                    Word(surface=word.surface, pos=word.feature.pos1)
                )

    # len(words)==1の場合は同音異字がないので省く
    return {kana: words for kana, words in kana2words.items() if len(words) > 1}


def save_homophones(
    kana2words: Dict[str, List[Word]],
    output_path: pathlib.Path,
    pos: Optional[str] = None,
) -> None:
    """同音異字を保存する

    Args:
        kana2words (Dict[str, List[Word]]): 読み仮名をキーとした同音異字
        output_path (pathlib.Path): 出力先のファイル
        pos (Optional[str]): 保存する品詞を限定する
    """
    with open(output_path, 'w', encoding='utf-8') as out:
        for kana, words in sorted(kana2words.items()):
            if pos is not None:
                words = [word for word in words if word.pos == pos]
                if len(words) <= 1:
                    continue
            homophones = ' '.join(sorted(set([word.surface for word in words])))
            out.write(f'{kana}\t{homophones}\n')


def readline(path: Union[str, pathlib.Path]) -> Iterator[str]:
    """ファイルを1行ずつ読み込む

    Args:
        path (Union[str, pathlib.Path]): 入力ファイル

    Yields:
        Iterator[str]: 1行ずつ返すジェネレータ
    """
    # WikiExtractorの出力ファイルがどのencodingでもうまく読み込めないため
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in iter(f.readline, ''):
            yield line.strip()


def kata2hira(text: str) -> str:
    """カタカナをひらがなに変換する

    Args:
        text (str): 文字列

    Returns:
        str: カタカナがひらがなになった文字列
    """
    return KATAKANA_REGEX.sub(lambda match: chr(ord(match.group()) - 96), text)


def main(_argv) -> None:
    input_dir = pathlib.Path(FLAGS.input_dir)
    output_dir = pathlib.Path(FLAGS.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logging.info('Start extracting homophones ...')
    kana2words = extract_homophones(input_dir)
    logging.info(f'Finish extracting: found {len(kana2words):,} unique kana.')

    head = 'homophones'
    tails = ['', '_noun', '_verb', '_adj', '_adv']
    pos_tags = [None, '名詞', '動詞', '形容詞', '副詞']
    for tail, pos_tag in zip(tails, pos_tags):
        save_homophones(kana2words, output_dir / f'{head}{tail}.tsv', pos=pos_tag)


if __name__ == '__main__':
    app.run(main)
