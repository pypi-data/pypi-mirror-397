
import tokenize
import io

TRANSLATIONS = {
    "çıkart": "print",
    "giriş": "input",
    "eğer": "if",
    "yoksa_eğer": "elif",
    "değilse": "else",
    "iken": "while",
    "döngü": "for",
    "içinde": "in",
    "aralık": "range",
    "fonk": "def",
    "dön": "return",
    "Doğru": "True",
    "Yanlış": "False",
    "ve": "and",
    "veya": "or",
    "değil": "not",
}

def turkce_kodu_cevir(kod: str) -> str:
    tokens = []
    g = tokenize.tokenize(io.BytesIO(kod.encode("utf-8")).readline)

    for token in g:
        if token.type == tokenize.NAME and token.string in TRANSLATIONS:
            token = token._replace(string=TRANSLATIONS[token.string])
        tokens.append(token)

    return tokenize.untokenize(tokens).decode("utf-8")
