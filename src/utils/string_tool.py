def contain_chinese(word: str) -> bool:
    for char in word:
        if u'\u4e00' <= char <= u'\u9fa5':
            return True
    return False