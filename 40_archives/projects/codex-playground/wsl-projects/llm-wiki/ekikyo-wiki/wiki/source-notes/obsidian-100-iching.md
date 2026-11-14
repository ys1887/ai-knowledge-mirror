# Obsidian 100_易経

**ページ目的:** Obsidian 側ノート群がどのような混成ソースかを整理し、どの層を durable に使いやすいかを示す。

## ソースの性格

この vault には約 1,400 以上の markdown があり、全体としては「個人の易占実践ログ + 参照ライブラリ」である。初回 ingest で見えた大きな層は次のとおり。

- `110_易占`, `120_易で社会を見る`
  - 月別・状況別の占い記録や、LLM ごとの回答比較が多い。大半は question-specific で transient。
- `130_易研究`
  - LLM 比較メモが多い一方、テンプレート改善や複数占断を束ねた研究ノートがあり、一部は durable。
- `140_高島易断`
  - 高島系テキスト、占例、現代語訳がまとまった参照層。durable な中心。
- `150_易経_資料`
  - `六十四卦一覧`、`序卦伝`、`文言伝`、`繋辞伝` などの基礎資料。durable。
- `170_易経_書籍`
  - 安岡正篤や本田濟など、二次的な読解層。durable。

## 強み

- 個人史と参照資料が同居しているため、後で history-derived knowledge を掘り起こしやすい。
- 高島系資料と十翼系資料がすでに markdown 化されており、概念ページや比較ページの下敷きにしやすい。
- 研究ノートの一部には、複数占断を連ねてパターンを見る方法が明示されている。

## 限界

- vault 全体の多数派は個別セッション記録で、そのまま durable claim にすると一般化しすぎる。
- `source:` 欄が空欄のノートがあり、原出典の追跡がノート単位で必要になる。
- clip と現代語訳ノートは便利だが、版・底本・転記元の確定が弱いものがある。

## 初回 foundation での使いどころ

- source note と provenance 方針の整理。
- `序卦伝` や `六十四卦一覧` のような補助導線の把握。
- 高島系資料が markdown 化されていることの確認。
- 個人履歴は「後で pattern を抽出できる source layer」として位置づけ、今回は一般化を控える。

## 要確認

- `140_高島易断` 配下の各現代語訳ノートの底本関係。
- `190_易サイトclip` 配下の元 URL と再利用条件。
- `130_易研究` のどこまでを methodology として durable 化できるか。

## Provenance

- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/110_易占/高島に寄せる？.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/110_易占/テンプレート改善：本卦と変爻.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/130_易研究/3月と4月の易占について.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/140_高島易断/周易占筮法秘伝_現代語訳.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/150_易経_資料/六十四卦一覧.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/150_易経_資料/序卦伝.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/170_易経_書籍/本田濟_易.md`
