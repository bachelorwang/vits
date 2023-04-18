import re
from unidecode import unidecode
from text.symbols import symbols
import pyopenjtalk

SYMBOL_TO_JAPANESE = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('％', 'パーセント'),
    ('%', 'パーセント'),
]]

OJT_PHONEME_TO_IPA = {
    'ch': 'ʧ',
    'sh': 'ʃ',
    'cl': 'Q'
}

JAPANESE_CHARACTERS = re.compile(
    r'[A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

JAPANESE_EXLUSION_CHARACTERS = re.compile(
    r'[^A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# ref https://r9y9.github.io/ttslearn/latest/notebooks/ch10_Recipe-Tacotron.html


def numeric_feature_by_regex(regex, s):
    match = re.search(regex, s)
    if match is None:
        return -50
    return int(match.group(1))


def pp_symbols(labels, drop_unvoiced_vowels=True):
    text = ''
    n = len(labels)

    # 各音素毎に順番に処理
    for i in range(n):
        lab_curr = labels[i]

        # 当該音素
        p3 = re.search(r"\-(.*?)\+", lab_curr).group(1)
        if p3 in ['sil', 'pau'] and (i == n - 1 or i == 0):
            continue

        # 先頭と末尾の sil のみ例外対応
        if p3 in ['sil', 'pau']:
            text += " "
        else:
            if p3 in OJT_PHONEME_TO_IPA:
                p3 = OJT_PHONEME_TO_IPA[p3]
            elif drop_unvoiced_vowels and p3 in "AEIOU":
                # 無声化母音を通常の母音として扱う
                p3 = p3.lower()
            text += p3

        # アクセント型および位置情報（前方または後方）
        a1 = numeric_feature_by_regex(r"/A:([0-9\-]+)\+", lab_curr)
        a2 = numeric_feature_by_regex(r"\+(\d+)\+", lab_curr)
        a3 = numeric_feature_by_regex(r"\+(\d+)/", lab_curr)
        # アクセント句におけるモーラ数
        f1 = numeric_feature_by_regex(r"/F:(\d+)_", lab_curr)

        a2_next = numeric_feature_by_regex(r"\+(\d+)\+", labels[i + 1])

        # アクセント句境界
        if a3 == 1 and a2_next == 1:
            text += " "
        # ピッチの立ち下がり（アクセント核）
        elif a1 == 0 and a2_next == a2 + 1 and a2 != f1:
            text += "↓"
        # ピッチの立ち上がり
        elif a2 == 1 and a2_next == 2:
            text += "↑"

    return text.strip()


def normalize_japanese_text(text):
    for regex, replacement in SYMBOL_TO_JAPANESE:
        text = re.sub(regex, replacement, text)
    return text

SYMBOLS = set(symbols)

def remove_invalid_characters(text):
    cleaned = ''
    for c in text:
        if c not in SYMBOLS:
            continue
        cleaned += c
    return cleaned

def japanese_cleaners(text):
    text = normalize_japanese_text(text)
    parts = re.split(JAPANESE_EXLUSION_CHARACTERS, text)
    marks = re.findall(JAPANESE_EXLUSION_CHARACTERS, text)
    text = ''
    for i, part in enumerate(parts):
        if re.match(JAPANESE_CHARACTERS, part):
            if text:
                text += ' '
            symbols = pyopenjtalk.extract_fullcontext(part)
            symbols = pp_symbols(symbols)
            text += symbols
        if i < len(marks):
            if marks[i] in SYMBOLS:
                text += marks[i]
            else:
                text += unidecode(marks[i]).strip()
    if re.match('[A-Za-z]', text[-1]):
        text += '.'
    text = remove_invalid_characters(text)
    return text
