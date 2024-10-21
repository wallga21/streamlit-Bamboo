import re
import random
from gliner import GLiNER
model = GLiNER.from_pretrained("urchade/gliner_mediumv2.1")

# Mapping from Compatibility Jamo to Hangul Jamo (Choseong)
compat_to_standard_initials = {
    'ㄱ': 'ᄀ',
    'ㄲ': 'ᄁ',
    'ㄴ': 'ᄂ',
    'ㄷ': 'ᄃ',
    'ㄸ': 'ᄄ',
    'ㄹ': 'ᄅ',
    'ㅁ': 'ᄆ',
    'ㅂ': 'ᄇ',
    'ㅃ': 'ᄈ',
    'ㅅ': 'ᄉ',
    'ㅆ': 'ᄊ',
    'ㅇ': 'ᄋ',
    'ㅈ': 'ᄌ',
    'ㅉ': 'ᄍ',
    'ㅊ': 'ᄎ',
    'ㅋ': 'ᄏ',
    'ㅌ': 'ᄐ',
    'ㅍ': 'ᄑ',
    'ㅎ': 'ᄒ',
}

# Predefined lists of common Hangul name syllables
initial_names = {
    'ㄱ': ['김', '가', '강', '건', '경', '규', '기', '근', '광'],
    'ㄲ': ['꽉', '끝'],
    'ㄴ': ['나', '남', '노', '누', '니'],
    'ㄷ': ['다', '동', '대', '두', '도', '덕', '단'],
    'ㄸ': ['땡', '떵'],
    'ㄹ': ['라', '로', '리', '림', '래', '란'],
    'ㅁ': ['마', '민', '명', '무', '문', '미', '모'],
    'ㅂ': ['바', '박', '병', '범', '보', '봉', '배'],
    'ㅃ': ['빵', '삐'],
    'ㅅ': ['사', '선', '서', '성', '수', '시', '세', '소'],
    'ㅆ': ['싼', '쌍'],
    'ㅇ': ['아', '영', '연', '오', '운', '우', '윤', '예'],
    'ㅈ': ['자', '재', '지', '준', '정', '진', '제', '종'],
    'ㅉ': ['짱', '찌'],
    'ㅊ': ['차', '찬', '천', '청', '초', '춘', '치', '최'],
    'ㅋ': ['카', '코', '크', '키'],
    'ㅌ': ['타', '태', '테', '토', '택'],
    'ㅍ': ['파', '편', '포', '표', '판'],
    'ㅎ': ['하', '한', '현', '희', '해', '혜', '혁'],
}

# Function to create a meaningful syllable by selecting from predefined names
def create_syllable(initial):
    return random.choice(initial_names.get(initial, initial))

# Function to expand initials in a text to meaningful syllables
def expand_initials(text):
    # Pattern for detecting initials in the Compatibility Jamo block (2-3 consecutive consonants)
    initial_pattern = re.compile(r'[ㄱ-ㅎ]{2,3}')

    def replace_initial(match):
        initials = match.group()
        # Map compatibility Jamo to standard Jamo
        standard_initials = ''.join([compat_to_standard_initials.get(char, char) for char in initials])

        # Debug: Print matched initials and their standard equivalents
        print(f"Matched initials: {initials} -> Standard Jamo: {standard_initials}")

        # Expand each initial to a full syllable using predefined syllables
        expanded = ''.join([create_syllable(char) for char in initials])

        # Debug: Print the expanded syllables
        print(f"Expanded syllables: {expanded}")

        return expanded

    # Replace all initial patterns in the text with expanded names
    return re.sub(initial_pattern, replace_initial, text)

def nametest(text):
    # Fix the text by expanding initials
    text_fixed = expand_initials(text)  # Expected to replace

    # Display the fixed text
    print("Fixed Text:", text_fixed)

    # Labels for entity prediction
    labels = ["Person"]

    # Perform entity prediction using the updated text
    entities = model.predict_entities(text_fixed, labels, threshold=0.5)
    if entities:
        return True
    else: return False
print(nametest('ㅈㅈㅎ 귀여움'))