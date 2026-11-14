# メール移行（Proton Mail → Gmail）とセキュリティアプリ構成の現況

- 日時：2026-11-08
- 種別：環境の現況
- 注意：これは現況の要約であり、📧メール移行チャットで 2026-11-08 に作られたマナ向けまとめの代わりではない。種として置く下書き。

## 決定済み

- Proton Mail Plus をやめ、Gmail 無料版へ切り替える。今月（2026年11月）中に移行予定。独自ドメインは SimpleLogin 側に受信専用で置くため、Mail Plus の解約は転送に影響しない（SimpleLogin は年 ¥3,200 の単独契約）。
- 移行先アカウントは eniacpod で確定。名義の持ち方（ログイン名義のまま表の顔を独自ドメインにする案／Gmail は受信専用にする案）は検討中。
- 振り分けの主軸は SimpleLogin 側の独自ドメインのアドレス単位。Gmail 側の転送先メールボックスは eniacpod+sl の想定。本格移行時に、Proton のメールボックスが付いた200件超のエイリアスへ Gmail のメールボックスを API で一括追加する計画。

## 実施済み

- パスワードと2FAの移行はメールより先に完了した（2026-11-08 本人報告）：Proton Pass → Bitwarden、Proton Authenticator → Ente。復旧キーは相互に保管する形。Proton Pass には Bitwarden、Ente、SimpleLogin、Proton Mail の4件の認証だけを残し、併用期間の終了後に他を削除する方針。Proton Authenticator には Proton アカウント、Bitwarden、SimpleLogin の認証のみを残す。
- Proton Mail のバックアップを取得済み（2026-11-08 未明、本人実施。Proton Mail Export Tool、復号済みの EML＋JSON、約200 MB）。
- Gmail への取り込み経路はテスト用 Gmail アカウントで動作確認済み（Betterbird＋ImportExportTools NG 経由の IMAP 取り込み）。テストは予行演習で全量は入っていない。本格移行の時はエクスポートを取り直す。
- Proton Mail は他サービスの回復用メールアドレスとして登録があるため、移行後も回復の受け皿として残る。

## 補足

- Mail Plus を解約すると Proton Mail Bridge は使えなくなる（有料プラン限定なのは Bridge のみ。Proton Pass と Proton Drive は無料プランでも PC で使える）。
