"""Small Windows settings window for button assignments and access settings."""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from config_store import BUTTON_COUNT, load_auth, load_settings, save_settings, set_password


class SettingsWindow:
    def __init__(self, root):
        self.root = root
        root.title("FirePanel 設定")
        root.resizable(False, False)
        frame = ttk.Frame(root, padding=18)
        frame.grid()
        current = load_settings()

        ttk.Label(frame, text="PCの待受IP").grid(row=0, column=0, sticky="w")
        self.host = tk.StringVar(value=current["host"])
        ttk.Entry(frame, textvariable=self.host, width=20).grid(row=0, column=1, sticky="w")
        ttk.Label(frame, text="ポート").grid(row=0, column=2, padx=(18, 4))
        self.port = tk.StringVar(value=str(current["port"]))
        ttk.Entry(frame, textvariable=self.port, width=8).grid(row=0, column=3, sticky="w")

        ttk.Label(frame, text="ボタン名").grid(row=1, column=0, pady=(18, 4), sticky="w")
        ttk.Label(frame, text="起動先（.exe / .lnk）").grid(row=1, column=1, columnspan=2, sticky="w")
        self.rows = []
        self.legacy_buttons = current["buttons"][BUTTON_COUNT:]
        for index, button in enumerate(current["buttons"][:BUTTON_COUNT], 1):
            label = tk.StringVar(value=button["label"])
            path = tk.StringVar(value=button["path"])
            ttk.Entry(frame, textvariable=label, width=18).grid(row=index + 1, column=0, pady=4)
            ttk.Entry(frame, textvariable=path, width=54).grid(row=index + 1, column=1, columnspan=2, padx=8)
            ttk.Button(frame, text="参照…", command=lambda p=path: self.browse(p)).grid(
                row=index + 1, column=3
            )
            self.rows.append((label, path))

        feed_row = len(self.rows) + 3
        ttk.Label(frame, text="TodoistカレンダーURL").grid(row=feed_row, column=0, pady=(14, 4), sticky="w")
        self.todoist_feed_url = tk.StringVar(value=current["todoist_feed_url"])
        ttk.Entry(frame, textvariable=self.todoist_feed_url, width=54, show="*").grid(
            row=feed_row, column=1, columnspan=2, padx=8, sticky="w"
        )
        ttk.Label(frame, text="Todoistの設定 → 連携 → カレンダー購読URL。PC内だけに保存します。").grid(
            row=feed_row + 1, column=0, columnspan=4, pady=(2, 0), sticky="w"
        )

        auth_row = feed_row + 2
        self.auth_state = tk.StringVar()
        self.refresh_auth_state()
        ttk.Label(frame, textvariable=self.auth_state).grid(row=auth_row, column=0, columnspan=2, pady=(18, 0), sticky="w")
        ttk.Button(frame, text="合言葉を設定・変更", command=self.change_password).grid(
            row=auth_row, column=2, columnspan=2, pady=(18, 0), sticky="e"
        )
        ttk.Button(frame, text="設定を保存", command=self.save).grid(
            row=auth_row + 1, column=3, pady=(18, 0), sticky="e"
        )
        ttk.Label(
            frame,
            text="変更後はサーバーを再起動してください。未登録のボタンは起動できません。",
        ).grid(row=auth_row + 2, column=0, columnspan=4, pady=(12, 0), sticky="w")

    def browse(self, path):
        chosen = filedialog.askopenfilename(
            title="起動するアプリまたはショートカットを選択",
            filetypes=[("アプリとショートカット", "*.exe *.lnk")],
        )
        if chosen:
            path.set(chosen)

    def refresh_auth_state(self):
        self.auth_state.set("認証: 設定済み" if load_auth() else "認証: 未設定")

    def change_password(self):
        first = simpledialog.askstring("合言葉", "8文字以上の合言葉を入力してください", show="*", parent=self.root)
        if first is None:
            return
        second = simpledialog.askstring("確認", "同じ合言葉をもう一度入力してください", show="*", parent=self.root)
        if second is None:
            return
        if first != second:
            messagebox.showerror("確認エラー", "合言葉が一致しません。")
            return
        try:
            set_password(first)
        except (ValueError, OSError) as exc:
            messagebox.showerror("設定エラー", str(exc))
            return
        self.refresh_auth_state()
        messagebox.showinfo("保存しました", "合言葉を保存しました。サーバー起動中なら再起動してください。")

    def save(self):
        try:
            settings = {
                "host": self.host.get().strip(),
                "port": int(self.port.get()),
                "todoist_feed_url": self.todoist_feed_url.get().strip(),
                "buttons": [
                    {"label": label.get().strip(), "path": path.get().strip()}
                    for label, path in self.rows
                ] + self.legacy_buttons,
            }
            save_settings(settings)
        except (ValueError, OSError) as exc:
            messagebox.showerror("設定エラー", str(exc))
            return
        messagebox.showinfo("保存しました", "設定を保存しました。サーバー起動中なら再起動してください。")


def main():
    root = tk.Tk()
    try:
        SettingsWindow(root)
    except ValueError as exc:
        messagebox.showerror("設定エラー", str(exc))
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
