
from turkcepy.translator import turkce_kodu_cevir

def test_print():
    assert turkce_kodu_cevir('çıkart("a")').strip() == 'print("a")'
