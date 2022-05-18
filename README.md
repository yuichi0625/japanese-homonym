# japanese-homophone
日本語の同音異字をまとめたデータ。  
（同音異義語だけでなく、音も意味も同じだけど表記が違うものも混ざっている、という意味合いです。）

`homophones`ディレクトリにデータが格納されています。
- ファイルの各行は、読み仮名と同音異字がタブ区切り、同音異字同士が半角スペース区切りになっています
- `homophones.tsv`は品詞を考慮しない全単語が入っています
- `homophoes_*.tsv`は`*`部分の品詞を持つ単語が入っています
- 単語分割・品詞ラベリングには`fugashi`を使用しています

## データ作成手順
`scripts`ディレクトリをご参照ください。

## 参考
- [同音異字](https://ja.wikipedia.org/wiki/%E5%90%8C%E9%9F%B3%E7%95%B0%E5%AD%97)
- [homophone](https://dictionary.cambridge.org/dictionary/english/homophone)
