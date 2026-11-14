import json

# 卦の並び順に注意：
# 入力される2進数（6桁）は、左から右へ向かって初爻（爻1）→上爻（爻6）です。
# 例：101100 は、初爻=1、二爻=0、三爻=1、四爻=1、五爻=0、上爻=0 という構成です。


def load_hexagrams(path="64ka.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["hexagrams"]


def get_hexagram_by_binary(binary, hexagrams):
    for h in hexagrams:
        if h["binary"] == binary:
            return h
    return {"number": None, "name": None}


def compute_zhi(binary, bian_list):
    zhi = list(binary)
    for idx in bian_list:
        i = idx - 1  # 爻番号は1〜6、インデックスは0〜5
        zhi[i] = '1' if zhi[i] == '0' else '0'
    return "".join(zhi)


def compute_hu(binary):
    # 爻2〜爻5（インデックス1〜4）を用いる
    return binary[1:4] + binary[2:5]


def compute_cuo(binary):
    return "".join(['1' if b == '0' else '0' for b in binary])


def compute_zong(binary):
    return binary[::-1]


def format_markdown_output(honka, bian_yao, zhi, hu, cuo, zong):
    return f"""
本卦：{honka['number']}.{honka['name']}
変爻：{', '.join(str(i) for i in bian_yao)}
之卦：{zhi['number']}.{zhi['name']}
互卦：{hu['number']}.{hu['name']}
錯卦：{cuo['number']}.{cuo['name']}
綜卦：{zong['number']}.{zong['name']}
"""


def main(honka_binary, bian_yao_str, hexagrams):
    bian_yao_list = [int(x) for x in bian_yao_str.strip(
    ).split()] if bian_yao_str.strip() else []

    honka = get_hexagram_by_binary(honka_binary, hexagrams)
    zhi_binary = compute_zhi(
        honka_binary, bian_yao_list) if bian_yao_list else None
    hu_binary = compute_hu(honka_binary)
    cuo_binary = compute_cuo(honka_binary)
    zong_binary = compute_zong(honka_binary)

    zhi = get_hexagram_by_binary(zhi_binary, hexagrams) if zhi_binary else {
        "number": None, "name": None}
    hu = get_hexagram_by_binary(hu_binary, hexagrams)
    cuo = get_hexagram_by_binary(cuo_binary, hexagrams)
    zong = get_hexagram_by_binary(zong_binary, hexagrams)

    markdown = format_markdown_output(honka, bian_yao_list, zhi, hu, cuo, zong)

    return {
        "structured": {
            "本卦": honka,
            "変爻": bian_yao_list,
            "之卦": zhi,
            "互卦": hu,
            "錯卦": cuo,
            "綜卦": zong
        },
        "markdown": markdown
    }


# 実行例
if __name__ == "__main__":
    hexagrams = load_hexagrams()
    result = main("101100", "2", hexagrams)
    print(result["markdown"])
