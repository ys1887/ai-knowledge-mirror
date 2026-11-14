import customtkinter as ctk
import duanyi
import pyperclip


class App(ctk.CTk):
    """易経 卦計算アプリ — 墨色ダークモード × 和テイスト"""

    # ─── カラーパレット ───
    BG_DARK = "#0F1923"
    PANEL_BG = "#162032"
    PANEL_BORDER = "#1E3050"
    CARD_BG = "#1A2940"
    CARD_BORDER = "#243B5C"
    CARD_HOVER = "#1F3350"

    ACCENT_GOLD = "#D4A574"
    ACCENT_GOLD_DIM = "#A07B50"
    ACCENT_RED = "#C0392B"
    ACCENT_TEAL = "#2A9D8F"
    ACCENT_TEAL_HOVER = "#238A7E"

    TEXT_PRIMARY = "#E2E8F0"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_DIM = "#64748B"

    BTN_PRIMARY = "#2563EB"
    BTN_PRIMARY_HOVER = "#1D4ED8"
    BTN_DANGER = "#7A8794"
    BTN_DANGER_HOVER = "#68727D"
    BTN_COPY = "#2A9D8F"
    BTN_COPY_HOVER = "#238A7E"

    ERROR_BG = "#3B1A1A"
    ERROR_BORDER = "#7F1D1D"
    ERROR_TEXT = "#FCA5A5"

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("易経 卦計算")
        self.geometry("720x540")
        self.minsize(680, 500)
        self.configure(fg_color=self.BG_DARK)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # header
        self.grid_rowconfigure(1, weight=0)  # input
        self.grid_rowconfigure(2, weight=0)  # error
        self.grid_rowconfigure(3, weight=1)  # results

        # データのロード
        self.base_data = duanyi.load_data(duanyi.JSON_FILE_NAME)

        # フォント定義
        self._font_family = "Noto Sans CJK JP"
        self._font_fallback = "Yu Gothic UI"
        self.title_font = ctk.CTkFont(family=self._font_family, size=24, weight="bold")
        self.subtitle_font = ctk.CTkFont(family=self._font_family, size=12)
        self.label_font = ctk.CTkFont(family=self._font_family, size=14, weight="bold")
        self.input_font = (self._font_family, 14)
        self.btn_font = ctk.CTkFont(family=self._font_family, size=13, weight="bold")
        self.result_label_font = ctk.CTkFont(family=self._font_family, size=11)
        self.result_value_font = ctk.CTkFont(family=self._font_family, size=16, weight="bold")
        self.error_font = ctk.CTkFont(family=self._font_family, size=13)

        self._build_header()
        self._build_input_panel()
        self._build_error_banner()
        self._build_result_panel()

        self.after(100, self.honka_entry.focus_set)

    # ──────────────────────── UI Builder ────────────────────────

    def _build_header(self):
        """ヘッダー: タイトル + サブタイトル"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 4))
        header.grid_columnconfigure(1, weight=1)

        # 八卦シンボル
        symbol = ctk.CTkLabel(
            header, text="☰", font=ctk.CTkFont(size=32),
            text_color=self.ACCENT_GOLD,
        )
        symbol.grid(row=0, column=0, rowspan=2, padx=(0, 12), sticky="w")

        title = ctk.CTkLabel(
            header, text="易経 卦計算",
            font=self.title_font, text_color=self.TEXT_PRIMARY, anchor="w",
        )
        title.grid(row=0, column=1, sticky="w")

        subtitle = ctk.CTkLabel(
            header, text="本卦より各卦を算出します",
            font=self.subtitle_font, text_color=self.TEXT_DIM, anchor="w",
        )
        subtitle.grid(row=1, column=1, sticky="w", pady=(0, 2))

        # 区切り線
        sep = ctk.CTkFrame(header, height=1, fg_color=self.PANEL_BORDER)
        sep.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def _build_input_panel(self):
        """入力パネル: 本卦 / 変爻 + 横並びボタン"""
        panel = ctk.CTkFrame(
            self, fg_color=self.PANEL_BG,
            corner_radius=12, border_width=1, border_color=self.PANEL_BORDER,
        )
        panel.grid(row=1, column=0, sticky="ew", padx=28, pady=(16, 0))
        panel.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.grid(row=0, column=0, sticky="ew", padx=20, pady=18)
        inner.grid_columnconfigure(1, weight=1)
        inner.grid_columnconfigure(3, weight=1)

        # ── 本卦 ──
        lbl_honka = ctk.CTkLabel(
            inner, text="本卦", font=self.label_font,
            text_color=self.ACCENT_GOLD,
        )
        lbl_honka.grid(row=0, column=0, padx=(0, 8), sticky="e")

        self.honka_entry = ctk.CTkEntry(
            inner, font=self.input_font, width=160, height=36,
            placeholder_text="例: 111111",
            fg_color=self.CARD_BG, border_color=self.CARD_BORDER,
            text_color=self.TEXT_PRIMARY, border_width=1, corner_radius=8,
        )
        self.honka_entry.grid(row=0, column=1, padx=(0, 24), sticky="w")
        self.honka_entry.bind("<Return>", self._focus_bianyao)

        # ── 変爻 ──
        lbl_bianyao = ctk.CTkLabel(
            inner, text="変爻", font=self.label_font,
            text_color=self.ACCENT_GOLD,
        )
        lbl_bianyao.grid(row=0, column=2, padx=(0, 8), sticky="e")

        self.bianyao_entry = ctk.CTkEntry(
            inner, font=self.input_font, width=160, height=36,
            placeholder_text="例: 2 5",
            fg_color=self.CARD_BG, border_color=self.CARD_BORDER,
            text_color=self.TEXT_PRIMARY, border_width=1, corner_radius=8,
        )
        self.bianyao_entry.grid(row=0, column=3, sticky="w")
        self.bianyao_entry.bind("<Return>", lambda e: self.calculate())

        # ── ボタン行 ──
        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 18))

        btn_specs = [
            ("⚡  計算", self.calculate, self.BTN_PRIMARY, self.BTN_PRIMARY_HOVER),
            ("✕  クリア", self.clear_input, self.BTN_DANGER, self.BTN_DANGER_HOVER),
            ("📋  本卦と変爻をコピー", self._copy_honka_bianyao_feedback, self.BTN_COPY, self.BTN_COPY_HOVER),
            ("📋  全てをコピー", self._copy_all_feedback, self.BTN_COPY, self.BTN_COPY_HOVER),
        ]

        self._buttons = {}
        for i, (text, cmd, fg, hover) in enumerate(btn_specs):
            btn = ctk.CTkButton(
                btn_row, text=text, command=cmd,
                font=self.btn_font,
                fg_color=fg, hover_color=hover,
                corner_radius=8, height=34, width=0,
            )
            btn.grid(row=0, column=i, padx=(0, 8) if i < len(btn_specs) - 1 else 0, sticky="w")
            self._buttons[text] = btn

    def _build_error_banner(self):
        """エラーバナー（通常非表示）"""
        self.error_frame = ctk.CTkFrame(
            self, fg_color=self.ERROR_BG,
            corner_radius=10, border_width=1, border_color=self.ERROR_BORDER,
        )
        self.error_label = ctk.CTkLabel(
            self.error_frame, text="", font=self.error_font,
            text_color=self.ERROR_TEXT, anchor="w",
        )
        self.error_label.grid(row=0, column=0, padx=16, pady=10, sticky="w")
        # 非表示にしておく
        self.error_frame.grid(row=2, column=0, sticky="ew", padx=28, pady=(12, 0))
        self.error_frame.grid_remove()

    def _build_result_panel(self):
        """結果パネル: 2列×3行のカードグリッド"""
        self.result_outer = ctk.CTkFrame(self, fg_color="transparent")
        self.result_outer.grid(row=3, column=0, sticky="nsew", padx=28, pady=(16, 24))
        self.result_outer.grid_columnconfigure(0, weight=1)
        self.result_outer.grid_columnconfigure(1, weight=1)

        result_defs = ["本卦", "変爻", "之卦", "互卦", "錯卦", "綜卦"]
        # 各定義ごとに色テーマを設定
        card_accents = {
            "本卦": self.ACCENT_GOLD,
            "変爻": self.TEXT_SECONDARY,
            "之卦": "#60A5FA",   # blue
            "互卦": "#A78BFA",   # purple
            "錯卦": "#F472B6",   # pink
            "綜卦": "#34D399",   # green
        }

        self.result_cards = {}
        for idx, name in enumerate(result_defs):
            row, col = divmod(idx, 2)
            card = self._create_result_card(
                self.result_outer, name, card_accents.get(name, self.TEXT_SECONDARY)
            )
            px_l = 0 if col == 0 else 6
            px_r = 6 if col == 0 else 0
            card["frame"].grid(row=row, column=col, padx=(px_l, px_r), pady=6, sticky="nsew")
            card["frame"].grid_remove()
            self.result_cards[name] = card

        # 行の weight
        for r in range(3):
            self.result_outer.grid_rowconfigure(r, weight=0)

    def _create_result_card(self, parent, label_text: str, accent_color: str) -> dict:
        """個別の結果カードウィジェットを生成"""
        frame = ctk.CTkFrame(
            parent, fg_color=self.CARD_BG,
            corner_radius=10, border_width=1, border_color=self.CARD_BORDER,
        )
        frame.grid_columnconfigure(0, weight=1)

        # ラベル（卦の種類）
        lbl = ctk.CTkLabel(
            frame, text=label_text, font=self.result_label_font,
            text_color=accent_color, anchor="w",
        )
        lbl.grid(row=0, column=0, padx=16, pady=(12, 0), sticky="w")

        # 値
        val = ctk.CTkLabel(
            frame, text="", font=self.result_value_font,
            text_color=self.TEXT_PRIMARY, anchor="w",
        )
        val.grid(row=1, column=0, padx=16, pady=(2, 14), sticky="w")

        return {"frame": frame, "label": lbl, "value": val}

    # ──────────────────────── Actions ────────────────────────

    def _focus_bianyao(self, event=None):
        """honka_entry でエンターが押されたら bianyao_entry にフォーカスを移動"""
        self.bianyao_entry.focus_set()

    def clear_results(self):
        """結果カードをクリアして非表示にする"""
        for card in self.result_cards.values():
            card["value"].configure(text="")
            card["frame"].grid_remove()

    def clear_input(self):
        """入力欄と結果をクリアする"""
        self.honka_entry.delete(0, ctk.END)
        self.bianyao_entry.delete(0, ctk.END)
        self._hide_error()
        self.clear_results()

    def _show_error(self, message: str):
        """エラーバナーを表示"""
        self.error_label.configure(text=f"⚠  {message}")
        self.error_frame.grid()

    def _hide_error(self):
        """エラーバナーを非表示"""
        self.error_frame.grid_remove()
        self.error_label.configure(text="")

    def _copy_with_feedback(self, btn_key: str, copy_fn):
        """コピー実行後にボタンテキストを一時変更してフィードバック"""
        copy_fn()
        # ボタンを探す
        btn = self._buttons.get(btn_key)
        if btn:
            original = btn_key
            btn.configure(text="✓  コピーしました", fg_color="#166534")
            self.after(1200, lambda: btn.configure(text=original, fg_color=self.BTN_COPY))

    def _copy_honka_bianyao_feedback(self):
        self._copy_with_feedback("📋  本卦と変爻をコピー", self.copy_honka_bianyao)

    def _copy_all_feedback(self):
        self._copy_with_feedback("📋  全てをコピー", self.copy_all)

    def copy_all(self):
        """表示中の全卦をコピー"""
        lines = []
        for key in ["本卦", "変爻", "之卦", "互卦", "錯卦", "綜卦"]:
            card = self.result_cards[key]
            if card["frame"].winfo_ismapped():
                val = card["value"].cget("text")
                if val:
                    lines.append(f"{key}：{val}")
        pyperclip.copy("\n".join(lines))

    def copy_honka_bianyao(self):
        """本卦と変爻だけをコピー"""
        lines = []
        for key in ["本卦", "変爻"]:
            card = self.result_cards[key]
            if card["frame"].winfo_ismapped():
                val = card["value"].cget("text")
                if val:
                    lines.append(f"{key}：{val}")
        pyperclip.copy("\n".join(lines))

    def calculate(self):
        """計算ボタン: duanyi の関数で各卦を算出し、カードに表示"""
        self._hide_error()
        self.clear_results()

        honka_binary = self.honka_entry.get().strip()
        bianyao_str = self.bianyao_entry.get().strip()

        # 本卦バリデーション
        try:
            duanyi.validate_binary_input(honka_binary)
            if len(honka_binary) != duanyi.HEXAGRAM_LENGTH:
                raise ValueError("本卦の2進数表記は6桁で入力してください")
        except ValueError as e:
            self._show_error(str(e))
            return

        # 変爻バリデーション
        try:
            if bianyao_str:
                bian_yao_list = [int(yao) for yao in bianyao_str.split()]
                if not all(yao in duanyi.VALID_YAO_POSITIONS for yao in bian_yao_list):
                    raise ValueError("変爻の位置は1から6の範囲で入力してください")
            else:
                bian_yao_list = []
        except ValueError as e:
            self._show_error(str(e))
            return

        # 本卦取得
        honka_number, honka_name = duanyi.get_hexagram_info(
            self.base_data["hexagrams"], honka_binary
        )
        if honka_number is None:
            self._show_error("指定された本卦が見つかりません")
            return

        # 各卦計算
        zhi_binary = duanyi.calculate_zhi_gua(honka_binary, bian_yao_list)
        hu_binary = duanyi.calculate_hu_gua(honka_binary)
        cuo_binary = duanyi.calculate_cuo_gua(honka_binary)
        zong_binary = duanyi.calculate_zong_gua(honka_binary)

        zhi_num, zhi_name = duanyi.get_hexagram_info(self.base_data["hexagrams"], zhi_binary)
        hu_num, hu_name = duanyi.get_hexagram_info(self.base_data["hexagrams"], hu_binary)
        cuo_num, cuo_name = duanyi.get_hexagram_info(self.base_data["hexagrams"], cuo_binary)
        zong_num, zong_name = duanyi.get_hexagram_info(self.base_data["hexagrams"], zong_binary)

        bianyao_display = "なし" if not bian_yao_list else " ".join(map(str, bian_yao_list))

        # カードに表示
        self.result_cards["本卦"]["value"].configure(text=f"{honka_number}. {honka_name}")
        self.result_cards["変爻"]["value"].configure(text=bianyao_display)
        self.result_cards["之卦"]["value"].configure(text=f"{zhi_num}. {zhi_name}")
        self.result_cards["互卦"]["value"].configure(text=f"{hu_num}. {hu_name}")
        self.result_cards["錯卦"]["value"].configure(text=f"{cuo_num}. {cuo_name}")
        self.result_cards["綜卦"]["value"].configure(text=f"{zong_num}. {zong_name}")

        for card in self.result_cards.values():
            card["frame"].grid()


if __name__ == "__main__":
    app = App()
    app.mainloop()
