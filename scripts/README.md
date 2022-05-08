# homophones作成手順
1. 必要なライブラリをインストールする。
    ```bash
    python -m pip install -r requirements.txt
    python -m unidic download
    ```

1. Wikipediaのダンプデータをダウンロードする。
    ```bash
    curl -O https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-pages-articles.xml.bz2
    ```

1. WikiExtractorを使用する。
    ```bash
    # READMEにもあるようにWindowsでは動かない
    # https://github.com/attardi/wikiextractor
    python -m wikiextractor.WikiExtractor jawiki-latest-pages-articles.xml.bz2
    ```

1. スクリプトを実行する。
    ```bash
    python create_homophones.py -i text -o homophones
    ```
