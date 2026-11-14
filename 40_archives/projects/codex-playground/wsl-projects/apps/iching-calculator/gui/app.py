import customtkinter as ctk
import duanyi
import json
import webbrowser
import pyperclip  # クリップボードへのコピー用


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("易経 卦計算")
        self.geometry("800x500")  # ウィンドウの幅を調整

        # データのロード
        self.base_data = duanyi.load_data(duanyi.JSON_FILE_NAME)

        # フォントの定義
        self.default_font = ("Yu Gothic UI", 14, "bold")  # タプルで定義
        self.number_font = ctk.CTkFont(
            family="Yu Gothic UI", size=16, weight="bold")
        self.name_font = ctk.CTkFont(
            family="Yu Gothic UI", size=18, weight="bold")

        # 入力欄
        self.honka_label = ctk.CTkLabel(
            self, text="本卦:", font=self.default_font
        )  # タプルを使用
        self.honka_label.grid(row=0, column=0, padx=10,
                              pady=(10, 5), sticky="e")
        self.honka_entry = ctk.CTkEntry(self, font=self.default_font)  # タプルを使用
        self.honka_entry.grid(row=0, column=1, padx=(
            10, 5), pady=(10, 5), sticky="w")
        self.honka_entry.bind("<Return>", self.focus_bianyao)

        # Perplexity リンク A
        self.link_button_a = ctk.CTkButton(
            self,
            text="Perplexity 易",
            command=lambda: self.open_url(
                "https://www.perplexity.ai/collections/yi-wg8Jo4k6TTufcWwxI7CzNg/"),  # URL は要変更
            font=self.default_font,
            width=20,
            fg_color="transparent",
            text_color="blue",
            hover_color="darkblue",
            corner_radius=5,
        )
        self.link_button_a.grid(row=0, column=2, padx=15, pady=(10, 5))

        # Perplexity リンク B
        self.link_button_b = ctk.CTkButton(
            self,
            text="Perplexity 5卦",
            command=lambda: self.open_url(
                "https://www.perplexity.ai/collections/5gua-yTvD1u8lQaW1al.GJOLK.A/"),  # URL は要変更
            font=self.default_font,
            width=20,
            fg_color="transparent",
            text_color="blue",
            hover_color="darkblue",
            corner_radius=5,
        )
        self.link_button_b.grid(row=0, column=3, padx=15, pady=(10, 5))

        self.bianyao_label = ctk.CTkLabel(
            self, text="変爻:", font=self.default_font)  # タプルを使用
        self.bianyao_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.bianyao_entry = ctk.CTkEntry(
            self, font=self.default_font)  # タプルを使用
        self.bianyao_entry.grid(
            row=1, column=1, padx=(10, 5), pady=5, sticky="w")
        self.bianyao_entry.bind("<Return>", lambda event: self.calculate())

        # リンク C
        self.link_button_c = ctk.CTkButton(
            self,
            text="易経ネット",
            command=lambda: self.open_url(
                "https://ekikyo.net/64ka/"),  # URL は仮
            font=self.default_font,
            width=20,
            fg_color="transparent",
            text_color="blue",
            hover_color="darkblue",
            corner_radius=5,
        )
        self.link_button_c.grid(row=1, column=2, padx=15, pady=5)

        # リンク D
        self.link_button_d = ctk.CTkButton(
            self,
            text="iChingのページ",
            command=lambda: self.open_url(
                "http://joe.g1.xrea.com/iching/iching.html#mokuji"),  # URL は仮
            font=self.default_font,
            width=20,
            fg_color="transparent",
            text_color="blue",
            hover_color="darkblue",
            corner_radius=5,
        )
        self.link_button_d.grid(row=1, column=3, padx=15, pady=5)

        # 計算ボタン
        self.calculate_button = ctk.CTkButton(
            self,
            text="計算",
            command=self.calculate,
            font=self.default_font,
            fg_color="blue",
            hover_color="darkblue",
            corner_radius=5,
        )
        self.calculate_button.grid(row=2, column=0, padx=15, pady=15)

        # クリアボタン
        self.clear_button = ctk.CTkButton(
            self,
            text="クリア",
            command=self.clear_input,
            font=self.default_font,
            fg_color="gray",
            hover_color="darkgray",
            corner_radius=5,
        )
        self.clear_button.grid(row=2, column=1, padx=15, pady=15)

        # エラー表示ラベル
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            font=self.default_font,
            bg_color="#FDD",  # 薄い赤色の背景
        )
        self.error_label.grid(row=4, column=0, columnspan=4, padx=15, pady=5)
        self.error_label.grid_remove()

        # コピーボタン (2種類)
        self.copy_button_honka_bianyao = ctk.CTkButton(
            self,
            text="本卦と変爻をコピー",
            command=self.copy_honka_bianyao,
            font=self.default_font,
            fg_color="green",
            hover_color="darkgreen",
            corner_radius=5,
        )
        self.copy_button_honka_bianyao.grid(row=2, column=2, padx=15, pady=15)

        self.copy_button_all = ctk.CTkButton(
            self,
            text="全てをコピー",
            command=self.copy_all,
            font=self.default_font,
            fg_color="green",
            hover_color="darkgreen",
            corner_radius=5,
        )
        self.copy_button_all.grid(row=2, column=3, padx=15, pady=15)

        # 結果表示ラベル
        self.result_labels = {}
        result_texts = ["本卦", "之卦", "互卦", "錯卦", "綜卦"]
        for i, text in enumerate(result_texts):
            self.result_labels[text] = ctk.CTkLabel(
                self, text="", anchor="center", font=self.number_font
            )  # フォントを設定
            self.result_labels[text].grid(
                row=i + 5, column=0, columnspan=4, padx=10, pady=5
            )
            self.result_labels[text].grid_remove()

        self.after(100, self.honka_entry.focus_set)

    def focus_bianyao(self, event=None):
        """honka_entry でエンターが押されたら bianyao_entry にフォーカスを移動"""
        self.bianyao_entry.focus_set()

    def clear_input(self):
        """入力欄と結果表示ラベルをクリアする"""
        self.honka_entry.delete(0, ctk.END)
        self.bianyao_entry.delete(0, ctk.END)
        for label in self.result_labels.values():
            label.grid_remove()

    def open_url(self, url):
        """指定された URL をデフォルトのブラウザで開く"""
        webbrowser.open(url)

    def copy_all(self):
        """結果表示ラベルの内容を全てクリップボードにコピーする"""
        result_text = ""
        # 本卦
        if self.result_labels["本卦"].winfo_ismapped():
            result_text += self.result_labels["本卦"].cget("text") + "\n"
        # 変爻 (本卦の下に追加)
        if hasattr(self, "bian_yao_list") and self.bian_yao_list:
            result_text += "変爻： " + \
                " ".join(map(str, self.bian_yao_list)) + "\n"
        elif hasattr(self, "bian_yao_list") and not self.bian_yao_list:
            result_text += "変爻なし\n"
        # 之卦
        if self.result_labels["之卦"].winfo_ismapped():
            result_text += self.result_labels["之卦"].cget("text") + "\n"
        # 互卦
        if self.result_labels["互卦"].winfo_ismapped():
            result_text += self.result_labels["互卦"].cget("text") + "\n"
        # 錯卦
        if self.result_labels["錯卦"].winfo_ismapped():
            result_text += self.result_labels["錯卦"].cget("text") + "\n"
        # 綜卦
        if self.result_labels["綜卦"].winfo_ismapped():
            result_text += self.result_labels["綜卦"].cget("text") + "\n"

        pyperclip.copy(result_text)

    def copy_honka_bianyao(self):
        """本卦と変爻の情報をクリップボードにコピーする"""
        result_text = ""
        # 本卦
        if self.result_labels["本卦"].winfo_ismapped():
            result_text += self.result_labels["本卦"].cget("text") + "\n"
        # 変爻
        if hasattr(self, "bian_yao_list") and self.bian_yao_list:
            result_text += "変爻： " + \
                " ".join(map(str, self.bian_yao_list)) + "\n"
        elif hasattr(self, "bian_yao_list") and not self.bian_yao_list:
            result_text += "変爻なし\n"

        pyperclip.copy(result_text)

    def calculate(self):
        """
        計算ボタンがクリックされたときに呼び出される関数。
        duanyi.py の関数を呼び出して計算し、結果をラベルに表示する。
        """

        # エラー表示をクリア
        self.error_label.grid_remove()
        self.error_label.configure(text="")

        # 入力値の取得
        honka_binary = self.honka_entry.get()
        bianyao_str = self.bianyao_entry.get()

        # 本卦の入力値の検証
        try:
            duanyi.validate_binary_input(honka_binary)
            if len(honka_binary) != duanyi.HEXAGRAM_LENGTH:
                raise ValueError("エラー：本卦の2進数表記は6桁で入力してください")
        except ValueError as e:
            self.error_label.configure(text=str(e))
            self.error_label.grid()
            return

        # 変爻の入力値の検証
        try:
            self.bian_yao_list = [int(yao) for yao in bianyao_str.split()]
            if not all(yao in duanyi.VALID_YAO_POSITIONS for yao in self.bian_yao_list):
                raise ValueError("エラー: 変爻の位置は1から6の範囲で入力してください。")
        except ValueError as e:
            self.error_label.configure(text=str(e))
            self.error_label.grid()
            return

        # 本卦の情報を取得
        honka_number, honka_name = duanyi.get_hexagram_info(
            self.base_data["hexagrams"], honka_binary
        )
        if honka_number is None:
            self.error_label.configure(text="指定された本卦が見つかりません。")
            self.error_label.grid()
            return

        # 各卦を計算
        hu_binary = duanyi.calculate_hu_gua(honka_binary)
        cuo_binary = duanyi.calculate_cuo_gua(honka_binary)
        zong_binary = duanyi.calculate_zong_gua(honka_binary)
        zhi_gua_binary = duanyi.calculate_zhi_gua(
            honka_binary, self.bian_yao_list)

        # 各卦の情報を取得
        hu_number, hu_name = duanyi.get_hexagram_info(
            self.base_data["hexagrams"], hu_binary
        )
        cuo_number, cuo_name = duanyi.get_hexagram_info(
            self.base_data["hexagrams"], cuo_binary
        )
        zong_number, zong_name = duanyi.get_hexagram_info(
            self.base_data["hexagrams"], zong_binary
        )
        zhi_gua_number, zhi_gua_name = duanyi.get_hexagram_info(
            self.base_data["hexagrams"], zhi_gua_binary
        )

        # 結果を表示 (番号と名前でフォントを分ける)
        self.result_labels["本卦"].configure(
            text=f"本卦：{honka_number}.{honka_name}", font=self.name_font
        )
        self.result_labels["之卦"].configure(
            text=f"之卦：{zhi_gua_number}.{zhi_gua_name}", font=self.name_font
        )
        self.result_labels["互卦"].configure(
            text=f"互卦：{hu_number}.{hu_name}", font=self.name_font
        )
        self.result_labels["錯卦"].configure(
            text=f"錯卦：{cuo_number}.{cuo_name}", font=self.name_font
        )
        self.result_labels["綜卦"].configure(
            text=f"綜卦：{zong_number}.{zong_name}", font=self.name_font
        )

        for label in self.result_labels.values():
            label.grid()


if __name__ == "__main__":
    app = App()
    app.mainloop()
