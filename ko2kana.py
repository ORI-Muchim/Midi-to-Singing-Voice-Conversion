import re
import jaconv
import pyopenjtalk

from jamo import h2j, j2hcj
from g2pk2 import G2p
from unidecode import unidecode


# Regular expression matching Japanese without punctuation marks:
_japanese_characters = re.compile(
    r'[A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# Regular expression matching non-Japanese characters or punctuation marks:
_japanese_marks = re.compile(
    r'[^A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# List of (symbol, Japanese) pairs for marks:
_symbols_to_japanese = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('％', 'パーセント')
]]


def symbols_to_japanese(text):
    for regex, replacement in _symbols_to_japanese:
        text = re.sub(regex, replacement, text)
    return text


def japanese_to_romaji_with_accent(text):
    '''Reference https://r9y9.github.io/ttslearn/latest/notebooks/ch10_Recipe-Tacotron.html'''
    text = symbols_to_japanese(text)
    sentences = re.split(_japanese_marks, text)
    marks = re.findall(_japanese_marks, text)
    text = ''
    for i, sentence in enumerate(sentences):
        if re.match(_japanese_characters, sentence):
            if text != '':
                text += ' '
            labels = pyopenjtalk.extract_fullcontext(sentence)
            for n, label in enumerate(labels):
                phoneme = re.search(r'\-([^\+]*)\+', label).group(1)
                if phoneme not in ['sil', 'pau']:
                    text += phoneme.replace('ch', 'ʧ').replace('sh',
                                                               'ʃ').replace('cl', 'Q')
                else:
                    continue
                # n_moras = int(re.search(r'/F:(\d+)_', label).group(1))
                a1 = int(re.search(r"/A:(\-?[0-9]+)\+", label).group(1))
                a2 = int(re.search(r"\+(\d+)\+", label).group(1))
                a3 = int(re.search(r"\+(\d+)/", label).group(1))
                if re.search(r'\-([^\+]*)\+', labels[n + 1]).group(1) in ['sil', 'pau']:
                    a2_next = -1
                else:
                    a2_next = int(
                        re.search(r"\+(\d+)\+", labels[n + 1]).group(1))
                # Accent phrase boundary
                if a3 == 1 and a2_next == 1:
                    text += ' '
                # Falling
                elif a1 == 0 and a2_next == a2 + 1:
                    text += '↓'
                # Rising
                elif a2 == 1 and a2_next == 2:
                    text += '↑'
        if i < len(marks):
            text += unidecode(marks[i]).replace(' ', '')
    return text


g2pk = G2p()


# This is a list of Korean classifiers preceded by pure Korean numerals.
_korean_classifiers = '군데 권 개 그루 닢 대 두 마리 모 모금 뭇 발 발짝 방 번 벌 보루 살 수 술 시 쌈 움큼 정 짝 채 척 첩 축 켤레 톨 통'

# List of (hangul, hangul divided) pairs:
_hangul_divided = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('ㄳ', 'ㄱㅅ'),
    ('ㄵ', 'ㄴㅈ'),
    ('ㄶ', 'ㄴㅎ'),
    ('ㄺ', 'ㄹㄱ'),
    ('ㄻ', 'ㄹㅁ'),
    ('ㄼ', 'ㄹㅂ'),
    ('ㄽ', 'ㄹㅅ'),
    ('ㄾ', 'ㄹㅌ'),
    ('ㄿ', 'ㄹㅍ'),
    ('ㅀ', 'ㄹㅎ'),
    ('ㅄ', 'ㅂㅅ'),
    ('ㅘ', 'ㅗㅏ'),
    ('ㅙ', 'ㅗㅐ'),
    ('ㅚ', 'ㅗㅣ'),
    ('ㅝ', 'ㅜㅓ'),
    ('ㅞ', 'ㅜㅔ'),
    ('ㅟ', 'ㅜㅣ'),
    ('ㅢ', 'ㅡㅣ'),
    ('ㅑ', 'ㅣㅏ'),
    ('ㅒ', 'ㅣㅐ'),
    ('ㅕ', 'ㅣㅓ'),
    ('ㅖ', 'ㅣㅔ'),
    ('ㅛ', 'ㅣㅗ'),
    ('ㅠ', 'ㅣㅜ')
]]

# List of (Latin alphabet, hangul) pairs:
_latin_to_hangul = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('a', '에이'),
    ('b', '비'),
    ('c', '시'),
    ('d', '디'),
    ('e', '이'),
    ('f', '에프'),
    ('g', '지'),
    ('h', '에이치'),
    ('i', '아이'),
    ('j', '제이'),
    ('k', '케이'),
    ('l', '엘'),
    ('m', '엠'),
    ('n', '엔'),
    ('o', '오'),
    ('p', '피'),
    ('q', '큐'),
    ('r', '아르'),
    ('s', '에스'),
    ('t', '티'),
    ('u', '유'),
    ('v', '브이'),
    ('w', '더블유'),
    ('x', '엑스'),
    ('y', '와이'),
    ('z', '제트')
]]


def latin_to_hangul(text):
    for regex, replacement in _latin_to_hangul:
        text = re.sub(regex, replacement, text)
    return text


def divide_hangul(text):
    text = j2hcj(h2j(text))
    for regex, replacement in _hangul_divided:
        text = re.sub(regex, replacement, text)
    return text


def hangul_number(num, sino=True):
    '''Reference https://github.com/Kyubyong/g2pK'''
    num = re.sub(',', '', num)

    if num == '0':
        return '영'
    if not sino and num == '20':
        return '스무'

    digits = '123456789'
    names = '일이삼사오육칠팔구'
    digit2name = {d: n for d, n in zip(digits, names)}

    modifiers = '한 두 세 네 다섯 여섯 일곱 여덟 아홉'
    decimals = '열 스물 서른 마흔 쉰 예순 일흔 여든 아흔'
    digit2mod = {d: mod for d, mod in zip(digits, modifiers.split())}
    digit2dec = {d: dec for d, dec in zip(digits, decimals.split())}

    spelledout = []
    for i, digit in enumerate(num):
        i = len(num) - i - 1
        if sino:
            if i == 0:
                name = digit2name.get(digit, '')
            elif i == 1:
                name = digit2name.get(digit, '') + '십'
                name = name.replace('일십', '십')
        else:
            if i == 0:
                name = digit2mod.get(digit, '')
            elif i == 1:
                name = digit2dec.get(digit, '')
        if digit == '0':
            if i % 4 == 0:
                last_three = spelledout[-min(3, len(spelledout)):]
                if ''.join(last_three) == '':
                    spelledout.append('')
                    continue
            else:
                spelledout.append('')
                continue
        if i == 2:
            name = digit2name.get(digit, '') + '백'
            name = name.replace('일백', '백')
        elif i == 3:
            name = digit2name.get(digit, '') + '천'
            name = name.replace('일천', '천')
        elif i == 4:
            name = digit2name.get(digit, '') + '만'
            name = name.replace('일만', '만')
        elif i == 5:
            name = digit2name.get(digit, '') + '십'
            name = name.replace('일십', '십')
        elif i == 6:
            name = digit2name.get(digit, '') + '백'
            name = name.replace('일백', '백')
        elif i == 7:
            name = digit2name.get(digit, '') + '천'
            name = name.replace('일천', '천')
        elif i == 8:
            name = digit2name.get(digit, '') + '억'
        elif i == 9:
            name = digit2name.get(digit, '') + '십'
        elif i == 10:
            name = digit2name.get(digit, '') + '백'
        elif i == 11:
            name = digit2name.get(digit, '') + '천'
        elif i == 12:
            name = digit2name.get(digit, '') + '조'
        elif i == 13:
            name = digit2name.get(digit, '') + '십'
        elif i == 14:
            name = digit2name.get(digit, '') + '백'
        elif i == 15:
            name = digit2name.get(digit, '') + '천'
        spelledout.append(name)
    return ''.join(elem for elem in spelledout)


def number_to_hangul(text):
    '''Reference https://github.com/Kyubyong/g2pK'''
    tokens = set(re.findall(r'(\d[\d,]*)([\uac00-\ud71f]+)', text))
    for token in tokens:
        num, classifier = token
        if classifier[:2] in _korean_classifiers or classifier[0] in _korean_classifiers:
            spelledout = hangul_number(num, sino=False)
        else:
            spelledout = hangul_number(num, sino=True)
        text = text.replace(f'{num}{classifier}', f'{spelledout}{classifier}')
    # digit by digit for remaining digits
    digits = '0123456789'
    names = '영일이삼사오육칠팔구'
    for d, n in zip(digits, names):
        text = text.replace(d, n)
    return text




import itertools

INITIAL = 0x001
MEDIAL = 0x010
FINAL = 0x100
CHAR_LISTS = {
    INITIAL: list(map(chr, [
        0x3131, 0x3132, 0x3134, 0x3137, 0x3138, 0x3139,
        0x3141, 0x3142, 0x3143, 0x3145, 0x3146, 0x3147,
        0x3148, 0x3149, 0x314a, 0x314b, 0x314c, 0x314d,
        0x314e
    ])),
    MEDIAL: list(map(chr, [
        0x314f, 0x3150, 0x3151, 0x3152, 0x3153, 0x3154,
        0x3155, 0x3156, 0x3157, 0x3158, 0x3159, 0x315a,
        0x315b, 0x315c, 0x315d, 0x315e, 0x315f, 0x3160,
        0x3161, 0x3162, 0x3163
    ])),
    FINAL: list(map(chr, [
        0x3131, 0x3132, 0x3133, 0x3134, 0x3135, 0x3136,
        0x3137, 0x3139, 0x313a, 0x313b, 0x313c, 0x313d,
        0x313e, 0x313f, 0x3140, 0x3141, 0x3142, 0x3144,
        0x3145, 0x3146, 0x3147, 0x3148, 0x314a, 0x314b,
        0x314c, 0x314d, 0x314e
    ]))
}
CHAR_INITIALS = CHAR_LISTS[INITIAL]
CHAR_MEDIALS = CHAR_LISTS[MEDIAL]
CHAR_FINALS = CHAR_LISTS[FINAL]
CHAR_SETS = {k: set(v) for k, v in CHAR_LISTS.items()}
CHARSET = set(itertools.chain(*CHAR_SETS.values()))
CHAR_INDICES = {k: {c: i for i, c in enumerate(v)}
                for k, v in CHAR_LISTS.items()}


def is_hangul_syllable(c):
    return 0xac00 <= ord(c) <= 0xd7a3  # Hangul Syllables


def is_hangul_jamo(c):
    return 0x1100 <= ord(c) <= 0x11ff  # Hangul Jamo


def is_hangul_compat_jamo(c):
    return 0x3130 <= ord(c) <= 0x318f  # Hangul Compatibility Jamo


def is_hangul_jamo_exta(c):
    return 0xa960 <= ord(c) <= 0xa97f  # Hangul Jamo Extended-A


def is_hangul_jamo_extb(c):
    return 0xd7b0 <= ord(c) <= 0xd7ff  # Hangul Jamo Extended-B


def is_hangul(c):
    return (is_hangul_syllable(c) or
            is_hangul_jamo(c) or
            is_hangul_compat_jamo(c) or
            is_hangul_jamo_exta(c) or
            is_hangul_jamo_extb(c))


def is_supported_hangul(c):
    return is_hangul_syllable(c) or is_hangul_compat_jamo(c)


def check_hangul(c, jamo_only=False):
    if not ((jamo_only or is_hangul_compat_jamo(c)) or is_supported_hangul(c)):
        raise ValueError(f"'{c}' is not a supported hangul character. "
                         f"'Hangul Syllables' (0xac00 ~ 0xd7a3) and "
                         f"'Hangul Compatibility Jamos' (0x3130 ~ 0x318f) are "
                         f"supported at the moment.")


def get_jamo_type(c):
    check_hangul(c)
    assert is_hangul_compat_jamo(c), f"not a jamo: {ord(c):x}"
    return sum(t for t, s in CHAR_SETS.items() if c in s)


def split_syllable_char(c):
    """
    Splits a given korean syllable into its components. Each component is
    represented by Unicode in 'Hangul Compatibility Jamo' range.

    Arguments:
        c: A Korean character.

    Returns:
        A triple (initial, medial, final) of Hangul Compatibility Jamos.
        If no jamo corresponds to a position, `None` is returned there.

    Example:
        >>> split_syllable_char("안")
        ("ㅇ", "ㅏ", "ㄴ")
        >>> split_syllable_char("고")
        ("ㄱ", "ㅗ", None)
        >>> split_syllable_char("ㅗ")
        (None, "ㅗ", None)
        >>> split_syllable_char("ㅇ")
        ("ㅇ", None, None)
    """
    check_hangul(c)
    if len(c) != 1:
        raise ValueError("Input string must have exactly one character.")

    init, med, final = None, None, None
    if is_hangul_syllable(c):
        offset = ord(c) - 0xac00
        x = (offset - offset % 28) // 28
        init, med, final = x // 21, x % 21, offset % 28
        if not final:
            final = None
        else:
            final -= 1
    else:
        pos = get_jamo_type(c)
        if pos & INITIAL == INITIAL:
            pos = INITIAL
        elif pos & MEDIAL == MEDIAL:
            pos = MEDIAL
        elif pos & FINAL == FINAL:
            pos = FINAL
        idx = CHAR_INDICES[pos][c]
        if pos == INITIAL:
            init = idx
        elif pos == MEDIAL:
            med = idx
        else:
            final = idx
    return tuple(CHAR_LISTS[pos][idx] if idx is not None else None
                 for pos, idx in
                 zip([INITIAL, MEDIAL, FINAL], [init, med, final]))


def split_syllables(s, ignore_err=True, pad=None):
    """
    Performs syllable-split on a string.

    Arguments:
        s (str): A string (possibly mixed with non-Hangul characters).
        ignore_err (bool): If set False, it ensures that all characters in
            the string are Hangul-splittable and throws a ValueError otherwise.
            (default: True)
        pad (str): Pad empty jamo positions (initial, medial, or final) with
            `pad` character. This is useful for cases where fixed-length
            strings are needed. (default: None)

    Returns:
        Hangul-split string

    Example:
        >>> split_syllables("안녕하세요")
        "ㅇㅏㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ"
        >>> split_syllables("안녕하세요~~", ignore_err=False)
        ValueError: encountered an unsupported character: ~ (0x7e)
        >>> split_syllables("안녕하세요ㅛ", pad="x")
        'ㅇㅏㄴㄴㅕㅇㅎㅏxㅅㅔxㅇㅛxxㅛx'
    """

    def try_split(c):
        try:
            return split_syllable_char(c)
        except ValueError:
            if ignore_err:
                return (c,)
            raise ValueError(f"encountered an unsupported character: "
                             f"{c} (0x{ord(c):x})")

    s = map(try_split, s)
    if pad is not None:
        tuples = map(lambda x: tuple(pad if y is None else y for y in x), s)
    else:
        tuples = map(lambda x: filter(None, x), s)
    return "".join(itertools.chain(*tuples))


def join_jamos_char(init, med, final=None):
    """
    Combines jamos into a single syllable.

    Arguments:
        init (str): Initial jao.
        med (str): Medial jamo.
        final (str): Final jamo. If not supplied, the final syllable is made
            without the final. (default: None)

    Returns:
        A Korean syllable.
    """
    chars = (init, med, final)
    for c in filter(None, chars):
        check_hangul(c, jamo_only=True)

    idx = tuple(CHAR_INDICES[pos][c] if c is not None else c
                for pos, c in zip((INITIAL, MEDIAL, FINAL), chars))
    init_idx, med_idx, final_idx = idx
    # final index must be shifted once as
    # final index with 0 points to syllables without final
    final_idx = 0 if final_idx is None else final_idx + 1
    return chr(0xac00 + 28 * 21 * init_idx + 28 * med_idx + final_idx)


def join_jamos(s, ignore_err=True):
    """
    Combines a sequence of jamos to produce a sequence of syllables.

    Arguments:
        s (str): A string (possible mixed with non-jamo characters).
        ignore_err (bool): If set False, it will ensure that all characters
            will be consumed for the making of syllables. It will throw a
            ValueError when it fails to do so. (default: True)

    Returns:
        A string

    Example:
        >>> join_jamos("ㅇㅏㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ")
        "안녕하세요"
        >>> join_jamos("ㅇㅏㄴㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ")
        "안ㄴ녕하세요"
        >>> join_jamos()
    """
    last_t = 0
    queue = []
    new_string = ""

    def flush(n=0):
        new_queue = []
        while len(queue) > n:
            new_queue.append(queue.pop())
        if len(new_queue) == 1:
            if not ignore_err:
                raise ValueError(f"invalid jamo character: {new_queue[0]}")
            result = new_queue[0]
        elif len(new_queue) >= 2:
            try:
                result = join_jamos_char(*new_queue)
            except (ValueError, KeyError):
                # Invalid jamo combination
                if not ignore_err:
                    raise ValueError(f"invalid jamo characters: {new_queue}")
                result = "".join(new_queue)
        else:
            result = None
        return result

    for c in s:
        if c not in CHARSET:
            if queue:
                new_c = flush() + c
            else:
                new_c = c
            last_t = 0
        else:
            t = get_jamo_type(c)
            new_c = None
            if t & FINAL == FINAL:
                if not (last_t == MEDIAL):
                    new_c = flush()
            elif t == INITIAL:
                new_c = flush()
            elif t == MEDIAL:
                if last_t & INITIAL == INITIAL:
                    new_c = flush(1)
                else:
                    new_c = flush()
            last_t = t
            queue.insert(0, c)
        if new_c:
            new_string += new_c
    if queue:
        new_string += flush()
    return new_string



repl_lst = {
    'ㄲ': 'ㅋ',
    'ㄸ': 'ㅌ',
    'ㅃ': 'ㅍ',
    'ㅆ': 'ㅅ',
    'ㅉ': 'ㅊ',
    
    'ㅙ': 'ㅗ/ㅔ',
    'ㅚ': 'ㅗ/ㅣ',
    'ㅘ': 'ㅜㅏ',
    'ㅝ': 'ㅜ/ㅓ',
    'ㅞ': 'ㅜ/ㅔ',
    'ㅟ': 'ㅜㅣ',
    'ㅢ': 'ㅜㅣ',

    'ㅒ': 'ㅣㅔ',
    'ㅕ': 'ㅛ',
    'ㅖ': 'ㅣㅔ',

    'ㅓ': 'ㅗ',
    'ㅐ': 'ㅔ',
    'ㅡ': 'ㅜ',

    '||//ㅎ': 'ㄹ',
}


def get_word_list(text):
    text = g2pk(text)
    text = j2hcj(h2j(text))
    text = re.sub(r'([\u3131-\u3163])$', r'\1.', text)
    return list(join_jamos(text.replace('  ', ' ')[:-1]))


def korean2katakana(text):
    word_lst = get_word_list(text)
    text = '/' + text.replace('/', ' ').replace('|', ' ').replace('^', ' ').replace('  ', ' ').replace(' ', '^')
    new_lst = []

    for i, s in enumerate(word_lst):
        dh = list(j2hcj(h2j(s)))
        if len(dh) == 3:
            if dh[-1] == 'ㄴ':
                dh[-1] = 'ㄴ'
                
            elif dh[-1] == 'ㅁ' or dh[-1] == 'ㅇ':
                dh[-1] = 'ㄴ|'
            
            elif dh[-1] == 'ㄹ':
                dh[-1] = '||/'

            else: # ㄱ ㄷ ㅂ
                dh[-1] = dh[-1]

        
        dh.append('/')
        new_lst.extend(dh)

    kr = ''.join(new_lst)
    
    for k, v in repl_lst.items():
        kr = kr.replace(k, v)
        
    kr2ro = japanese_to_romaji_with_accent(kr).replace('si', 'shi').replace('c', 'ts') \
                                              .replace('ti', 'ティ').replace('tu', 'トゥ') \
                                              .replace('di', 'ディ').replace('du', 'ドゥ') \

    result = jaconv.alphabet2kata(kr2ro)
    result = result.replace('/', '').replace('|', 'ー').replace('^', '')
    return result


if __name__ == '__main__': 
    print(korean2katakana("안녕하세요."))