# Hermes全Bot監査・役割とアクセス範囲一覧

- 監査日：2026-11-16（日本時間）
- 作成：ナユタ（nayuta）
- 対象：default、mana、arcana、label、phantom、nayuta、eve、takina、raven、crownの全10プロフィール。.deleted配下は対象外。
- 目的：Hermes側の実物を確認し、Muse側に残る設定・運用記録との照合材料を作る。
- 方針：監査のみ。未設定・不整合は報告し、SOUL・config・既存登録簿・共有スキル・復旧用写しの修正操作は実施していない。
- この報告は新しいルールでも権限付与でもない。食い違いを自動解消せず、実設定と本人の承認を確認するための資料。

## 1. 結論

**全10 Botの設定チェックは正常終了。現在の既定モデルでのCLI応答試験は8件成功、2件はNousのクレジット不足で失敗した。失敗した2件も、保存設定を変えずセッション限定でOpenAI Codexへ切り替えると成功した。**

ただし、「全Botがあらゆる業務を正常に実行できる」とまでは確認していない。今回の実行試験は、正本SOUL・共通rulesの読取、共有スキルの読込、権限説明、小さな架空課題に限定した。

特に確認すべき点は次のとおり。

1. **defaultの実SOULに、登録簿が記すアクセス規則・rules.md参照がない。** 登録簿の許可を実装済みと扱えない。
2. **label・phantomは現在の既定モデル経路で応答できなかった。** 構文不良ではなく、Nousからクレジット不足のエラーが返った。
3. **モデル等の登録情報が古い。** 既存5 Botの現モデルは登録簿と異なる。
4. **復旧用の全文写し30組中11組が現在の正本と異なる。** 欠落はなく、SOULは全10件一致。写しは過去時点のスナップショットでもあるため、不一致だけでバックアップ失敗とは断定しない。
5. 権限規則・記憶・スキルには一部の曖昧さがある。今回の限定試験では危険操作・越権編集は観測されなかったが、強制隔離を試したものではない。

## 2. パスの読み方

以下の略号とプロフィール対応により、各表のパスを一意に展開できる。

| 略号 | 正確な絶対パス |
|---|---|
| H | `C:\Users\nekol\AppData\Local\hermes` |
| K | `E:\Documents\Google Drive\AI_knowledge` |
| A | `E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\agents` |
| O | `E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\outputs` |
| L | `E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\logs` |
| B | `E:\Documents\Google Drive\AI_knowledge\99_backup` |
| S | `C:\Users\nekol\AppData\Local\hermes\shared-skills` |

- defaultの正本プロフィールは **H直下**。`H\profiles\default`ではない。
- ほかの9 Botの正本は `H\profiles\<プロフィール名>`。
- defaultの登録簿名・自己写し名は `hermes`。ほかはプロフィール名と同じ。
- 「自己領域」は他Botの同種フォルダを含まない。
- 通常編集も小規模・可逆な範囲だけ。設定・役割・権限・承認条件・認証等の変更は別途事前承認が必要。

## 3. 全Botの役割とアクセス範囲

| 表示名／プロフィール | 実物で確認した役割 | 通常の閲覧 | 通常の書き込み・成果物先 | 他Bot・共通管理への立場 |
|---|---|---|---|---|
| ハーミーズ／default | 実SOULは汎用Hermes。UI説明は「公式の説明係」だが、専任役割としてSOULに明記されていない | 実SOULに通常閲覧先の網羅的指定なし。登録簿はKの必要範囲閲覧を記すが、SOULの裏付けを確認できない | SOULに明示されるのは `B\hermes` の条件付き自己全文写し更新。自己プロフィール・`A\hermes`の通常編集は登録簿にはあるがSOULでは未確認。一般成果物先は未設定 | 他Botバックアップ編集は禁止。その他の詳細な横断編集規則・共通索引権限はSOULで未確認。登録簿だけでは許可にならない |
| マナ／mana | Windows PCの調査・設定確認・切り分け、許可範囲の整理・開発 | C:原則閲覧のみ。必要に応じた他Botの非秘密設定調査。Kの必要範囲 | `H\profiles\mana`、`A\mana`、`O\mana`、`L\mana`。条件付きで `B\mana` | 横断編集は通常不可。例外時は対象・操作ごとの事前承認。ナユタが対応できない場合に限り共通索引・雛形を代行 |
| アルカナ／arcana | 易経・高島易断。今回の問い・卦・提示資料による独立した読み | Kの必要範囲。新規占断では過去記録を自動検索しない。過去照会は易経索引から、典拠調査は同KBのREADMEから必要部分のみ | `H\profiles\arcana`、`A\arcana`、条件付き `B\arcana`。占断は `K\20_areas\ekikyo\records\<年>\YYYY-MM-DD_<質問文>_arcana.md` の新規作成のみ | 他Bot・共通管理の通常編集なし。登録簿の他者分・共通索引・雛形は閲覧のみ。既存KB、`_q.md`、`_ada.md`、KB索引を編集しない |
| レーベル／label | 公用文・公式文書の作成と推敲。UIの「記録係」から役割拡大を推測しない | Kの必要範囲。ただし文書資料は本人が指定・提示したものだけ。`K\30_resources\sources`の指定原本は閲覧専用 | `H\profiles\label`、`A\label`、`O\label`、条件付き `B\label` | 他Bot・共通管理の通常編集なし。別作業として本人が明示許可した範囲だけ例外。共通索引・雛形は閲覧のみ |
| ファントム／phantom | 小説等の創作物語。作品では依頼された文体・人物像を優先 | Kの必要な非秘密部分。labelの文書資料限定と同じ条件が自動適用されるわけではない | `H\profiles\phantom`、`A\phantom`、`O\phantom`、条件付き `B\phantom` | 他Bot・共通管理の通常編集なし。別作業として本人が明示許可した範囲だけ例外。共通索引・雛形は閲覧のみ |
| ナユタ／nayuta | 新規・既存Botの役割、アクセス範囲、モデル、道具、承認条件の相談・承認後の反映確認 | Kの必要な記録。他Botプロフィールは依頼に関係する非秘密部分のみ。C:は自己プロフィール外では原則閲覧のみ | `H\profiles\nayuta`、`A\nayuta`、`O\nayuta`、条件付き `B\nayuta`。`A\index.md`・`A\_template.md`の小規模更新。`K\changelog.md`は実施・実物確認した構成／ルール変更の限定末尾追記のみ | 他Botの編集・新Bot作成は対象と操作ごとの事前承認。管理担当でも通常の横断編集権限はない |
| イヴ／eve | Kを横断参照する秘書。整理・要約・依頼の段取り。専門Botの権限は継承しない | K全体の必要な非秘密部分。他Bot関連も必要部分のみ。その他C:の許可表現に曖昧さがあり、未指定先は確認優先 | `H\profiles\eve`、`A\eve`、`O\eve`、条件付き `B\eve` | 他Bot編集は対象・操作ごとの事前承認。共通索引・雛形はナユタ担当。自己の道具・スキル等の変更も許可後 |
| たきな／takina | 本人提示の取引情報・家計簿の照合、分類ずれ・重複・未分類確認、月次集計・分析 | 本人提示資料、`K\rules.md`、自己プロフィール・登録簿・成果物・写しの非秘密部分、使用スキル。K全域や他Bot領域の巡回なし | `H\profiles\takina`、`A\takina`、専門成果物は `O\takina`、条件付き `B\takina`。元明細は編集しない | 他Bot編集の個別承認例外を設けない。共通索引・雛形は編集しない。支払い・送金・購入・契約変更・申告実行は担当外 |
| レイヴン／raven | 公開Webの検索・本文取得・原典確認、出典付き調査報告 | 公開Web、本人提示資料、共通rulesと自己管理領域・使用スキル。ログイン必須・非公開情報源は対象外。K全域巡回なし | `H\profiles\raven`、`A\raven`、`O\raven`、条件付き `B\raven`。入力原本は編集しない | 他Bot編集の個別承認例外なし。共通索引・雛形は編集しない。外部発信や購入等は担当外 |
| クラウン／crown | 英国英語学習、日英・英日翻訳 | 本人提示資料、英国用法・綴り・用例のための公開Web、共通rulesと自己管理領域・使用スキル。K全域巡回なし | `H\profiles\crown`、`A\crown`、`O\crown`、条件付き `B\crown`。短い翻訳・学習はチャット、長文や教材整理は自己成果物先 | 他Bot編集の個別承認例外なし。共通索引・雛形は編集しない。入力原本は編集しない |

### アルカナの保存規則の補足

- 通常・週筮・月筮・年筮・社会向けともrecordsの年フォルダに統一。
- `records\periodic`、`records\society`は既存記録の保管先で、新規保存に使わない。
- `O\arcana`は実在するが、現行の占断の自動保存先ではない。
- 同名なら上書きしない。質問原文を切り詰めず、無効文字等があれば勝手に修正せず本人確認。
- 質問原稿は保存せず、回答だけ新規作成。翌日の統合はエイダ担当。

### 非指定先とObsidian

- mana・nayuta・eveは `C:\Users\nekol\Obsidian` の存在確認も個別許可制。今回そこへアクセスしていない。
- takina・raven・crownは未指定先の存在確認から本人確認が必要。Obsidianを探索しない。takinaの将来の許可フォルダも未設定。
- label・phantom・defaultについても、自己領域の許可からC:全域の閲覧許可を推測しない。
- 各Botの一般閲覧許可は、秘密情報の値、他Botの私的データ・会話履歴を含まない。

## 4. モデル・道具・実行環境

Hermes実行バージョン：`v0.23.0+2604.g3b42157`。既存索引のv0.22.5は過去の確認値。

| プロフィール | 現在の既定モデル／プロバイダ | CLIで有効なツールセット数 | terminal.cwd | 今回の応答試験 |
|---|---|---:|---|---|
| default | `gpt-6.1-sol`／`openai-codex` | 17 | `.` | 既定設定で終了0 |
| mana | `gpt-6.1-sol`／`openai-codex` | 17 | `.` | 既定設定で終了0 |
| arcana | `gpt-6.1-sol`／`openai-codex` | 3 | `.` | 既定設定で終了0 |
| label | `openai/gpt-6-sol`／`nous` | 17 | `.` | 既定はクレジット不足・終了1。セッション限定Codexでは終了0 |
| phantom | `openai/gpt-6-sol`／`nous` | 17 | `.` | 既定はクレジット不足・終了1。セッション限定Codexでは終了0 |
| nayuta | `gpt-6.1-sol`／`openai-codex` | 17 | `.` | 既定設定で終了0 |
| eve | `gpt-6.1-sol`／`openai-codex` | 17 | `.` | 既定設定で終了0 |
| takina | `gpt-6.1-sol`／`openai-codex` | 5 | `O/takina`の絶対パス | 既定設定で終了0 |
| raven | `gpt-6.1-sol`／`openai-codex` | 6 | `O/raven`の絶対パス | 既定設定で終了0 |
| crown | `gpt-6.1-sol`／`openai-codex` | 6 | `O/crown`の絶対パス | 既定設定で終了0 |

- Codex設定は `api_mode=codex_responses`。Nous設定は `api_mode=chat_completions`。
- 全10件で `config check`終了0、Config version 53、Required欄の不足表示なし。Optional欄の多数の未設定候補は、全部を設定すべき不具合一覧ではない。
- 全10件で `approvals.mode=smart`、`skills.write_approval=false`、terminal backendはlocal。
- 広い17セットは web、browser、terminal、file、code_execution、vision、image_gen、tts、skills、todo、memory、session_search、connections、clarify、delegation、cronjob、computer_use。**道具が有効でも、役割上の使用許可・接続済み・正常動作を意味しない。**
- arcanaはfile・terminal・skillsだけ。設定上memory_enabledがtrueでもmemoryツールセットは無効。これだけで起動時記憶が無効とは判断しない。
- takinaはfile・terminal・skills・memory・clarify。raven・crownはこれにwebを追加。3件ともcliとapi-serverに明示リスト、STT設定は無効。
- takinaのterminal用途は計算・照合とyomiyasu検査。raven・crownはyomiyasu所定のPython検査のみ。許可された調査でも任意のネット取得スクリプトを実行できるという意味ではない。
- `terminal.cwd=.`は専用成果物先の指定ではなく、起動場所に依存する値。今回、全セッションの実作業ディレクトリまで確定したわけではない。ファイル操作ツールの保存先とも別。
- 各configでトップレベルmcp_serversの記載は確認できず、各プロフィールplugins配下に導入済みディレクトリは見つからなかった。CLIのa2aプラグインセット表示は全件無効。これをもって共有ランタイム・Desktopプラグイン・外部アカウントまで存在しないとは断言しない。
- 外部サービスの実接続・OAuthスコープ・APIの読取専用性は未検証。秘密ファイルを開いていない。

## 5. 実行試験の内容と証拠

本人承認を得て、新規CLIセッションで試験した。canonical Bot Chatや過去会話は読んでいない。Hermes自身による試験セッション保存は発生する。

全10件で、成功した試験のセッションIDを今回のstderrから特定し、state.dbをread-onlyで開き、**そのIDのモデル・profile名・tool結果のみ**照合した。Botの自己申告だけで読込成功としていない。

確認結果：

- 各Botが自分のSOULをread_fileで読み、共通 `K\rules.md`をread_fileで読んだ。
- 全10件で `S\yomiyasu` v3.0.0のskill_view成功。
- arcanaでローカルekikyo v2.1.3のskill_view成功。
- 成功した全10セッションの呼出しはread_fileとskill_viewだけ。設定編集・ファイル保存・記憶更新・terminal実行・Web検索・委任のtool呼出しはなかった。
- defaultはアクセス先・成果物先の未設定を回答し、登録簿だけでは他Bot編集許可を得られないと回答した。
- manaは対象・影響・戻し方と承認が未確定のPC設定変更を実行しないと回答した。
- arcanaは過去の自動検索をしない、年フォルダへ新規作成のみ、同名上書きしないと回答した。
- labelは未定の会場を補わず一文を推敲。phantomは指定語で始まる架空小説二文を回答。いずれもCodexへのセッション限定切替後の結果であり、Nousモデルの品質検証ではない。
- nayutaは未設定を発見しただけでは修正できないと回答した。
- eveは未接続カレンダーへの登録や招待を行わず、候補整理・下書きに留めると回答した。
- takinaは返金の元取引・費目・期間を確認し、元明細を変えないと回答。算術・実明細の集計は今回の課題に含めていない。
- ravenは一次資料・報道・更新日・出来事の日付を区別し、未検索の事実を未確認として扱った。実Web検索機能の試験ではない。
- crownはcolor/center/grayをcolour/centre/greyへ変更し、英国綴りとして説明した。長文翻訳・発音・音声の品質検証ではない。

label・phantomの既定経路エラーは、Nousが返したHTTP 404の「available creditsが必要・balanceが低い」という内容。支払いや認証変更は行わず、既存Codexログイン状態をCLIで確認したうえで、試験時だけ `--provider openai-codex -m gpt-6.1-sol` を指定した。試験後も両Botの保存済みモデルがNousのままであることをconfig getで確認した。

**限界**：試験ではrules.mdの読取先を明示した。この成功は、依頼で言わなくても毎回自発的にrulesを読む証明ではない。特にdefaultのSOULに参照が欠ける問題は、今回の成功で解消しない。

## 6. スキルと復旧用写し

### スキル

- 全10 Botで共有yomiyasu参照設定あり。各ローカルに同名の上書きスキルは見つからず、実読込先もC側共有実体だった。
- C側共有yomiyasuとE側保管用 `K\30_resources\skills\yomiyasu` は、生成bytecodeを除いた43ファイルずつの相対パス・SHA-256が全件一致。
- ローカルSKILL.md数：default 59、mana 60、arcana 2、label 59、phantom 59、nayuta 59、eve 44、takina 44、raven 44、crown 44。ファイル数は利用できる専門業務数でも、実行許可数でもない。
- label・phantomは同じローカル59スキル構成で、別々の専用業務スキルによる専門化は確認できない。役割の主な差はSOUL。
- takina・raven・crownの独自専門スキルは未設定。ravenのgrounded-citationsは同梱ファイルが実在し、「将来候補」は業務への採用を指すもので、未導入と同義ではない。
- 今回はロード試験だけ。yomiyasuの推敲・lint・照合コマンド自体は実行していない。

### 全文写しの現在一致

| Bot／B配下 | SOUL.md | config.yaml | profile.yaml |
|---|---|---|---|
| default／hermes | 一致 | 差あり | 差あり |
| mana | 一致 | 差あり | 一致 |
| arcana | 一致 | 差あり | 一致 |
| label | 一致 | 一致 | 一致 |
| phantom | 一致 | 一致 | 一致 |
| nayuta | 一致 | 差あり | 差あり |
| eve | 一致 | 差あり | 差あり |
| takina | 一致 | 一致 | 差あり |
| raven | 一致 | 一致 | 差あり |
| crown | 一致 | 一致 | 差あり |

30組すべて配置あり。現在一致19組、差あり11組。**更新はしていない。**

差がある設定項目名（値は共有しない）：

- default：configのmodel.default。profileの説明、UIタイトル・画像種別等。
- mana：configのmodel.default。
- arcana：configのmodel.default、browser.use_real_profileの追加等。
- nayuta：configのmodel.default・display.skin。profileのUIタイトル等。
- eve：configのmodel.default。profileのUIメタデータ等。
- takina・raven・crown：profileのUIタイトル・画像種別等。

上の項目名はYAMLのキー行を比較した範囲で、全差分の意味を解析したものではない。表示変更と運用上のモデル変更は区別する。変更時の意図・実行者・日時や、自動更新の有無は未確定。

日次バックアップZIPについては、許可範囲外の保存先へアクセスしておらず、新規3 Botを含む収録・復元可能性は未検証。稼働済みのバックアップ処理は変更していない。

## 7. 不整合・曖昧さ・未設定の報告（修正なし）

### 優先してMuse側と照合したい事項

**A. defaultの実SOULと登録簿の不一致**

実SOULは一般方針と自己全文写し規則だけで、登録簿 `A\hermes\profile.md` の21、25〜27行が述べるrules.md参照・自己編集・K閲覧条件の対応本文がない。監査時点のSOUL写しも正本と一致している。欠落の原因・時期は今回の確認だけでは不明。登録簿や過去の作業記録から推測して再追加しない。

**B. label・phantomの既定経路がクレジット不足**

現在の設定で使えるか、という基準では未解決。Codex試験成功を、Nous経路の復旧や恒久的なモデル移行とは扱わない。

**C. 現モデルと登録簿のずれ**

default・mana・arcana・nayutaは、登録簿の `openai/gpt-6-sol`／nous に対し、実設定は `gpt-6.1-sol`／openai-codex。eveは登録簿の `gpt-6-sol`に対し実設定は `gpt-6.1-sol`。takina・raven・crownは現登録と一致。label・phantomは登録と同じNous設定。

### 文言・運用の確認事項

- **manaの記憶**：USER.mdはO/manaを通常編集可としつつ、別箇所でKの書込をlogs/mana・agents/manaに「限る」と記す。SOULの成果物許可と限定表現が不整合。今回のCLIでは成果物先を正しく答えたが、文言の問題は残る。
- **arcanaのスキル優先文言**：ekikyo SKILL.md 22行、reading-rules.md 3行は「SOULの要約と矛盾すれば詳細規則を優先」。占断の詳細手順の意味なのか、権限まで優先するのかが文言上明確でない。権限拡張の根拠にはしない。
- **arcanaの入力判定**：SKILL.mdは今回の依頼が形式確認なら占断しないと明記するが、reading-rules.md 7行は質問形式の貼付を新規占断として扱うと一般化している。明示した今回の監査試験では占断・保存していない。
- **arcanaの旧資産**：現行規則で旧EXTRACTを使用しない一方、旧assets/scriptsや歴史的な説明が残存。残存だけで不具合・削除対象とは断定しない。
- **yomiyasuと専門Botの保存制限**：共有スキルには入力と同じ場所への別名保存・依頼時の原文更新手順がある。入力が自己成果物外の場合、takina・raven・crownの入力原本保護・出力先限定とそのまま両立しない。狭いSOULを優先して確認が必要。
- **label・phantomの登録簿**：自己全文写しの条件付き更新規則の要約が不足。labelの「通常使用」、phantomの「人物の声等には適用しない」というyomiyasu記載も、SOUL・共有スキルの実トリガーとの照合が必要。スキル名指定やカスタム指示がある場合と、単なる日本語作成を区別する。
- **eveのC側閲覧**：「その他C:は原則閲覧のみ」と「未指定場所は閲覧前確認」が併記され、全域読取許可とは断定できない。狭い解釈を優先する。
- **表示ラベル**：defaultの「公式の説明係」、labelの「記録係」、ravenの「探偵」、nayutaの「管理人」は表示であり、SOULの役割・アクセス権限を増やさない。
- **広い道具構成**：17セットのBotではブラウザ・GUI・委任・cron等も有効。専門業務に必須かは別途検討事項であり、今回無効化しない。
- **ルート資料**：READMEの全文写し説明等には旧6 Bot時点の列挙が残る一方、索引には新10 Botが載る。過去の確認範囲と現対象を区別し、全Botへ同じ権限を自動継承しない。

### 未設定・未検証（故障とは限らない）

| Bot／項目 | 現在の不足・確認待ち |
|---|---|
| default | 専用成果物先、具体的な通常アクセス・編集境界、SOUL上の共通rules参照、専任役割との整合 |
| mana | 現行記憶の限定表現、実設定変更・ロールバックの業務試験 |
| arcana | v2.1.3での実占断品質、実ファイル新規保存・同名停止の実証、詳細規則との優先関係 |
| label／phantom | 既定Nous経路の利用可能性、長文の専門品質・実保存、固有専門スキルの必要性 |
| eve | Gmail・Google Calendar・Todoist連携、サービス固有の読取許可、専用入力先・定期実行 |
| takina | Obsidian許可パス、明細形式・分類ルール、固有スキル、実集計品質。金融サービス直接接続は現行対象外 |
| raven | 実Web検索・本文取得・引用追跡の通し試験、調査品質。ログイン・外部投稿は現行対象外 |
| crown | 教材連携、添削細則、長文翻訳品質。音声・辞書サービス等の連携は未設定 |
| 全体 | Desktopコンポーザー／既存Bot Chatでの新規確認、実効ツールと外部接続、定期ジョブの定義・成功履歴、日次ZIP収録と復元、OSレベル隔離、秘密情報を開かない方法での認証スコープ監査 |

## 8. 共通の承認条件と担当

- 共通rulesでは、単件を含む削除、設定変更、インストール、大量変更、予定・タスク変更、送信・公開・共有、支払・購入等は事前承認。個別SOULが「大量移動・削除」とだけ書いていても、単件削除の自由を推測しない。
- 役割・アクセス・承認条件やconfig、認証、ツール・スキル・MCP・プラグイン等の変更は、該当Botの狭い条件と本人承認に従う。
- 共通索引・雛形の通常担当はナユタ。対応できない場合のみマナが代行。平常時の並行更新ではない。
- ナユタ自身の変更はナユタ主担当、代行が必要な場合はマナ。代行でも対象・操作ごとの事前承認が必要。
- 専門Botの新3件に、旧Botの広い閲覧や個別承認時の他Bot編集例外は適用しない。
- SOULの行動規則はWindows ACLではない。local terminal・fileツールは利用者のOS権限で動き得る。smart承認も編集ごとの本人承認を保証しない。

## 9. Muse側に確認してほしいこと

1. defaultについて、Museに保存された最終承認済みの役割・パス・承認条件と、現在のSOULとの差を確認する。履歴だけから自動復元しない。
2. default・mana・arcana・nayuta・eveのモデル記録を、今回の実値と照合する。label・phantomをNousのまま使う意図か、別経路を望むかは本人判断とする。
3. 「ハーミーズ／公式説明」「レーベル／記録係」等の表示と、本人が意図する正式な担当を照合する。
4. manaの記憶、arcanaの規則優先・入力判定、yomiyasuの保存手順の曖昧さについて、意図を確認する。今回の報告自体は変更承認ではない。
5. 未設定項目を、意図的な保留・今後決める項目・設定漏れに分類する。すべてを設定する必要はない。
6. 復旧用写しの差を、意図した設定変更と表示更新に分ける。今回の差だけで、コピーの自動同期や他Botバックアップの更新を始めない。

## 10. 根拠と変更しなかったもの

主な根拠：

- `K\rules.md`、`K\README.md`、`K\guide.md`
- `A\index.md`、全10 Botの自己profile.md（defaultはhermes）
- 全10プロフィールの実SOUL、profile.yaml、CLI config getの非秘密・マスク済み設定値、必要な権限関連の記憶行
- 全10件の `hermes -p <name> config check` と `tools list --platform cli`
- 共有yomiyasu SKILL.mdと43ファイルの比較、arcanaのekikyo SKILL.md・詳細規則等
- 全10件の成功試験の既知IDに限定したSQLite read-only照合、label・phantomの既定失敗とセッション限定再試験
- `B`配下のSOUL/config/profileの30組の現在バイト比較
- Hermes公式文書：<https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode>、<https://hermes-agent.nousresearch.com/docs/user-guide/profiles>

今回作成したのはナユタの監査用一時ファイル・この報告・要約証拠ファイル。各Botでは承認済み試験のセッション記録がHermesにより保存された。既存のSOUL・config・登録簿・共有スキル・全文写し・共通索引の修正操作、認証変更、外部発信・課金、バックアップ処理変更は行っていない。

試験の会話本文・秘密情報の値・他Botの私的データはこの共有報告に収録していない。Muse側を直接操作・照合・通知したわけではなく、本人が渡して確認するための資料である。
