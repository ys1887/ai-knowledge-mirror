import json
import sys

# 定数の定義
HEXAGRAM_LENGTH = 6
VALID_YAO_POSITIONS = range(1, 7)
JSON_FILE_NAME = "base_hexagrams.json"


def load_data(filename):
    """
    JSONファイルを読み込み、データを返す

    Args:
        filename (str): 読み込むJSONファイルの名前

    Returns:
        dict: JSONファイルから読み込まれたデータ

    Raises:
        FileNotFoundError: ファイルが見つからない場合に発生
        json.JSONDecodeError: JSONの形式が不正な場合に発生
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"エラー: {filename} が見つかりません。ファイルが存在し、正しい場所にあることを確認してください。")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"エラー: {filename} の形式が不正です。正しいJSON形式であることを確認してください。")
        sys.exit(1)


def get_hexagram_info(hexagrams, binary_code, key="binary", number_key="number", name_key="name"):
    """
    2進数表記 (binary_code) に一致する卦の情報を取得

    Args:
        hexagrams (list): 卦のリスト
        binary_code (str): 検索する2進数表記
        key (str, optional): 検索に使用するキー. Defaults to "binary".
        number_key (str, optional): 卦番号のキー. Defaults to "number".
        name_key (str, optional): 卦名のキー. Defaults to "name".

    Returns:
        tuple: (卦番号, 卦名) のタプル。見つからない場合は (None, None) を返す。
    """
    for hexagram in hexagrams:
        if hexagram[key] == binary_code:
            return hexagram[number_key], hexagram[name_key]
    return None, None


def calculate_zhi_gua(honka_binary, bian_yao_list):
    """
    之卦の2進数表記を計算する

    Args:
        honka_binary (str): 本卦の2進数表記
        bian_yao_list (list): 変爻の位置のリスト

    Returns:
        str: 之卦の2進数表記
    """
    zhi_gua_binary = list(honka_binary)
    for yao in bian_yao_list:
        index = yao - 1
        zhi_gua_binary[index] = '1' if zhi_gua_binary[index] == '0' else '0'
    return "".join(zhi_gua_binary)


def calculate_hu_gua(binary_code):
    """
    互卦の2進数表記を計算する

    Args:
        binary_code (str): 本卦の2進数表記

    Returns:
        str: 互卦の2進数表記
    """
    return binary_code[1:4] + binary_code[2:5]


def calculate_cuo_gua(binary_code):
    """
    錯卦の2進数表記を計算する

    Args:
        binary_code (str): 本卦の2進数表記

    Returns:
        str: 錯卦の2進数表記
    """
    return "".join(['1' if bit == '0' else '0' for bit in binary_code])


def calculate_zong_gua(binary_code):
    """
    綜卦の2進数表記を計算する

    Args:
        binary_code (str): 本卦の2進数表記

    Returns:
        str: 綜卦の2進数表記
    """
    if binary_code == binary_code[::-1]:
        return binary_code
    else:
        return binary_code[::-1]


def validate_binary_input(binary_code):
    """
    2進数表記が正しいか検証する

    Args:
        binary_code (str): 検証する2進数表記

    Raises:
        ValueError: 2進数表記が不正な場合に発生
    """
    if not all(bit in '01' for bit in binary_code):
        raise ValueError("エラー: 2進数表記は0と1のみで入力してください。")


def main():
    """
    メイン関数：易経の卦計算プログラム

    ユーザーから本卦の2進数表記と変爻の位置を入力させ、
    本卦、之卦、互卦、錯卦、綜卦を計算して表示する。
    """
    base_data = load_data(JSON_FILE_NAME)

    honka_binary = input("本卦の2進数表記（6桁）を入力してください: ")
    try:
        validate_binary_input(honka_binary)
        if len(honka_binary) != HEXAGRAM_LENGTH:
            raise ValueError("エラー：本卦の2進数表記は6桁で入力してください")
    except ValueError as e:
        print(e)
        return

    bian_yao_str = input("変爻の位置をスペース区切りで入力してください（例: 2 5）: ")
    try:
        bian_yao_list = [int(yao) for yao in bian_yao_str.split()]
        if not all(yao in VALID_YAO_POSITIONS for yao in bian_yao_list):
            raise ValueError("エラー: 変爻の位置は1から6の範囲で入力してください。")
    except ValueError as e:
        print(e)
        return

    honka_number, honka_name = get_hexagram_info(base_data["hexagrams"], honka_binary)
    if honka_number is None:
        print("指定された本卦が見つかりません。")
        return

    hu_binary = calculate_hu_gua(honka_binary)
    cuo_binary = calculate_cuo_gua(honka_binary)  # 裏卦から錯卦へ
    zong_binary = calculate_zong_gua(honka_binary)

    hu_number, hu_name = get_hexagram_info(base_data["hexagrams"], hu_binary)
    cuo_number, cuo_name = get_hexagram_info(base_data["hexagrams"], cuo_binary)  # 裏卦から錯卦へ
    zong_number, zong_name = get_hexagram_info(base_data["hexagrams"], zong_binary)

    print(f"本卦：{honka_number}.{honka_name}")

    if bian_yao_list:
        zhi_gua_binary = calculate_zhi_gua(honka_binary, bian_yao_list)
        zhi_gua_number, zhi_gua_name = get_hexagram_info(base_data["hexagrams"], zhi_gua_binary)
        if zhi_gua_number is None:
            print("之卦の情報が見つかりません。")
            return
        print(f"之卦：{zhi_gua_number}.{zhi_gua_name}")

    print(f"互卦：{hu_number}.{hu_name}")
    print(f"錯卦：{cuo_number}.{cuo_name}")  # 裏卦から錯卦へ
    print(f"綜卦：{zong_number}.{zong_name}")


def test_calculations():
    """
    各卦の計算関数のテスト
    """
    test_binary = "101010"
    assert calculate_hu_gua(test_binary) == "0101", "互卦のテスト失敗"
    assert calculate_cuo_gua(test_binary) == "010101", "錯卦のテスト失敗"  # 裏卦から錯卦へ
    assert calculate_zong_gua(test_binary) == "010101", "綜卦のテスト失敗"
    assert calculate_zhi_gua(test_binary, [2, 5]) == "111000", "之卦のテスト失敗"
    print("すべてのテストに成功しました！")


if __name__ == "__main__":
    # test_calculations()  # テストを実行する場合はコメントを外す
    main()