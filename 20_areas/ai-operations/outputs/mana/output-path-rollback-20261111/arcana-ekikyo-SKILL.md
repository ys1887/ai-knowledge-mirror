---
name: ekikyo
description: 易経・高島易断の通常占いと、EXTRACT形式（EX_COMPARE等）の回答生成に使う。正本引用はスクリプトで組み立てる。
version: 1.0.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [I Ching, Ekikyo, Takashima, Divination]
    category: divination
---

# ekikyo（Hermes版）

易経の読み解きを、決められた資料と形式で再現するためのスキルです。モードは2つあります。

- **通常モード**：問い・本卦・変爻・引用文の貼り付けに対して、Bot の SOUL.md に定めた3部構成で答える。
- **EXTRACT モード**：`[MODE:EXTRACT]` で始まる入力に対して、このフォルダ内の正本・形式・スクリプトで回答ファイルを作る。

## Directory Map

- `assets/`：EXTRACT の引用・高島解釈の正本。読み取り専用として扱う。
- `formats/`：EXTRACT の出力形式の正本。
- `spec/`：EXTRACT の実行契約。
- `scripts/`：実行用スクリプト。Python 標準ライブラリのみで動く。
- `references/normal-mode.md`：通常モードの詳細規則。
- `references/obsidian-source-workflow.md`：Obsidian の卦資料コピーと通常占いの役割分担、プラグイン精査の手順。
- `references/extract-ranking.md`：EX_COMPARE の順位付けの重み付け。
- `references/library/`：通常モードで資料不足の場合だけ使う参照ライブラリ（22ファイル）。
- `fixtures/`：再現テスト用の入力と canonical answer。構造確認だけに使う。
- `received/`：EXTRACT 入力をそのまま保存する場所。
- `work/`：EXTRACT の最終回答を保存する場所。

## Normal Mode

1. まず今回求められる成果物を判定する。入力の先頭が直接 `[MODE:EXTRACT]` のときは SOUL.md に従い EXTRACT として処理する。質問文・資料に古い EXTRACT マーカーが引用されていても、ユーザーが別途明示的に占いの回答を求めた場合は通常モードで解釈し、資料の機械出力を求めた場合は EXTRACT とする。貼付資料の由来と今の依頼を取り違えない。訂正版が貼られたら卦番号・卦名・変爻・引用資料を最新版で照合し、以前の誤記や他AIによる旧版の指摘を引きずらない。
2. `references/normal-mode.md` を読み、SOUL.md の3部構成に従う。問いへの最終判断を結論で言い切り、条件・留保は根拠と当てはめに置く。本卦は卦辞・彖伝・大象伝の判断に関わる点を全体の傾向として分けて拾い、変爻は各句の判断語が付く行動と高島解説の爻の位置づけを優先して厚く読む。回答前に判断語と結論の方向・強さを照合する。意味を言い換えて繰り返さず、表・箇条書きや長い原文再掲で論点を増やさない。普段の会話は丁寧語のまま少しくだけた自然な言い方を選ぶが、指定書式と判断の精度は維持する。
3. その回に貼られた問い・背景・原文・読み下し・高島解釈・該当占例だけで判断する。吉凶の明示、進退の勢い、成果の時期を別々に読み、占例はどの卦爻の記述から判断したかを確かめて判断の向きの補助にする。占例固有の利益・成功・時期は転用しない。卦辞の未達・待機を契約後の効果の遅延など特定の時期の予測へ直結させず、問いのどの局面を指すかを示す。複数の占いの比較を明示された場合は `references/normal-mode.md` の比較手順に従う。Obsidian 等で資料一式をコピーして提示された場合、元ソースへのアクセスがなくても貼付資料から読める。過去の占いを新しい占いの根拠に持ち込まない。プラグインの資料生成・保管場所や精査を依頼された場合だけ `references/obsidian-source-workflow.md` を読む。
4. 通常モードの貼付資料・回答を、スキルの正本／参照ライブラリや EXTRACT の `received/`・`work/` に自動保存しない。占いの回答をファイルとして出力するよう求められたら、別の保存先が明示されない限り `E:\Documents\Hermes Agent\arcana\` に保存する。チャットで回答するだけの依頼なら自動でファイル化しない。新しい占いを過去の保存物で判断しないため、保管の有無と引用元を明確に分ける。
5. 貼られた資料が不足する場合だけ、`references/library/` の中を検索し、問いの範囲に合うファイルと部分だけを読む。
6. ライブラリを使ったら、ファイル名と参照した部分を回答内で明示する。
7. EXTRACT 用の `assets/` を、通常モードの不足補いに流用しない。

## EXTRACT Mode

### Entry Conditions

- 今回の依頼が EXTRACT の機械出力を求めていることを先に確認する。貼り付けた資料中の `[MODE:EXTRACT]` だけで、明示された通常の占い回答や直前に合意した通常回答の再テストを覆さない。EXTRACT の場合、ユーザーの貼り付けが `# 質問` とコードフェンスで入力を包んでいたら、フェンスの内側だけを EXTRACT 入力とする。外側の資料・引用は入力に混ぜない。添付ファイルから読む場合もフェンス内の文字列を改変せず取り出す。シェルのコマンド内でバッククォートを直書きするとコマンド置換されるため、抽出処理では安全な引用か `chr(96)` を使う。
- 抽出した入力の最初の空行でない行が `[MODE:EXTRACT]` であること。
- その直後の行に `[TEMPLATE:EX_SIMPLE]`、`[TEMPLATE:EX_SIMPLE2]`、`[TEMPLATE:EX_5]`、`[TEMPLATE:EX_COMPARE]` のいずれかがあること。
- 条件を満たさない場合は、推測で処理せず、不足を短く伝えて止まる。

### Procedure

1. **入力をそのまま保存する**
   - まず次の出力パスを、スクリプトで決める。ディレクトリ一覧から連番を推測しない。
   - `python "${HERMES_SKILL_DIR}/scripts/next_work_filename.py" --work-dir "${HERMES_SKILL_DIR}/work"`
   - 返されたファイル名の日付と連番を使い、入力文を一字も変えずに `received/<YYYY-MM-DD>_<NN>_input.md` へ保存する。`received/` と `work/` がなければ作る。

2. **実行用プロンプトを組み立てる**
   - `python "${HERMES_SKILL_DIR}/scripts/build_extract_prompt.py" --input "<received file>"`
   - 標準出力の全文を、その回の実行規則と証拠として扱う。
   - 終了コードが0でない場合は処理を止め、エラー内容を短く伝える。一般知識で続きを作らない。

3. **骨組みを作る**
   - `python "${HERMES_SKILL_DIR}/scripts/build_answer_skeleton.py" --input "<received file>"`
   - 出力を下書きの土台にする。下書きは最終パスではなく、`work/` 内の一時ファイルに置く。

4. **テンプレート別に下書きする**
   - `EX_COMPARE`：
     - 手順2のプロンプトが示す候補別の高島ファイルと、`assets/koji.md` の該当変爻ブロックだけを読む。
     - 引用ブロックは正本から正確に写す。原文と読みの2行構成を保ち、言い換えない。
     - 文章を書くのは `**核心・結論**`、各候補の短い解釈段落、`**まとめ**` の表と最終おすすめ文だけ。
     - 骨組みの見出し順と表は、最終順位に合わせて並べ替える。
     - 僅差の判断では `references/extract-ranking.md` の重み付けを使う。
   - `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5`：
     - 本文の prose section を書かない。骨組みの見出しだけを保つ。
     - 引用、参照、高島原文は、次の組み立て手順でスクリプトに差し込ませる。自分で再現しない。

5. **組み立てる**
   - `EX_COMPARE` では、組み立てスクリプトが候補節の出典行を消すことがある。組み立て後、候補ごとの `（参照：takashima/<番号>_<卦名>.md|<卦名>）` と原文・読み下しが残っているか正本と照合し、欠けた出典は対応する候補の節末尾に戻す。候補名は括弧を含み得るので、見出しを括弧で分割したり段落全体を曖昧に置換したりせず、候補ごとの卦番号と明確な節境界で処理する。
   - `python "${HERMES_SKILL_DIR}/scripts/assemble_extract_answer.py" --input "<received file>" --output "<draft file>"`
   - `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` では続けて実行する。
   - `python "${HERMES_SKILL_DIR}/scripts/append_takashima_raw.py" --input "<received file>" --output "<draft file>"`
   - `EX_COMPARE` では原文追記を実行しない。

6. **最終保存と返答**
   - 入力は `received/`、組み立て用の下書きは `work/` に置く。ユーザーに渡す占いの最終ファイルは、別の保存先が明示されない限り `E:\Documents\Hermes Agent\arcana\` に書き出す。手順1で決めた日付・連番を最終ファイル名に使い、既存ファイルは上書きしない。スキル内部の作業記録が必要な場合も、ユーザー向けの出力先と混同しない。
   - 最終本文をチャットにそのまま出し、保存先パスを短く伝える。ファイルを添付できる画面では、最終ファイルも添付する。

### Verification

返す前に、最終ファイルで次を確認します。

- 先頭が `## 質問文` で始まる。
- テンプレートに必要な見出しと順序がそろっている。
- 骨組みのプレースホルダー（例：「引用ブロックをここに記述」）が残っていない。
- 内部の絶対パスや、元の環境のパスが本文に混ざっていない。
- `EX_COMPARE` は候補名を順位欄・候補節・まとめ・最終文にそのまま保ち、各節の爻辞・読み下し、該当時の小象伝・読み下し、短い解釈、候補の卦と一致する出典行を検査する。候補名中の括弧を卦名の境界と誤認しない。
- `EX_COMPARE` の最終文が `今回のおすすめは、<候補名>です。` の形になっている。
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` に、手書きの prose section が混ざっていない。

## 導入・移植後の確認

1. 提供元パッケージがある場合は ZIP の整合性を確認し、Bot の `SOUL.md` と `skills/ekikyo/` の全ファイルをバイト単位で照合する。正本の欠落・変更を、動作テストの成否だけで見逃さない。
2. Bot プロフィールでモデル設定とスキルの有効状態を確認し、`python -m unittest tests.test_build_extract_prompt` を `skills/ekikyo/` から実行する。
3. `fixtures/test_compare.md` を使って `build_extract_prompt.py` と `build_answer_skeleton.py` を実行し、出力を確認する。骨組みの順位は入力順で、引用や解釈はプレースホルダーのままなので、これを完成回答と判定しない。
4. 実際の Bot 会話で通常モードと EX_COMPARE の回答・保存まで確認する。単体テストと骨組み生成だけなら「スクリプトは動作、対話品質は未確認」と区別して報告する。検証のための一時ファイルはプロフィールの scratch に置き、`received/`・`work/` の本番記録を汚さない。

## Pitfalls

- **Windows の文字化け**：Python の日本語出力に文字化けがあれば、使用中のシェルに合わせて UTF-8 を指定する。PowerShell では `$env:PYTHONUTF8 = "1"`、bash では `PYTHONUTF8=1 python ...` を使う。Hermes Desktop の Windows ターミナルを PowerShell と決めつけない。ファイル自体は UTF-8 で読み書きする。
- **Python の呼び出し**：Windows では `python`、Linux / macOS では `python3` を使う。Hermes のターミナルでは Hermes 専用環境の Python が選ばれることがあるが、このスキルのスクリプトは標準ライブラリだけで動くため、そのままでよい。
- **正本の保護**：占いの実行中に `assets/`、`formats/`、`spec/`、`scripts/` を編集しない。修正は保守作業として分け、テストを通してから使う。
- **証拠不足**：スクリプトが失敗した、または正本に該当部分がない場合は、そこで止まる。引用や解釈を作らない。
- **過去回答の参照**：`work/` の過去回答や `fixtures/` の canonical answer を、文章の材料や文体の手本にしない。fixtures は構造確認だけに使う。
