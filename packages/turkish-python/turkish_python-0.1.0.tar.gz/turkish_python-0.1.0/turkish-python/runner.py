
import subprocess
import sys
import tempfile
import argparse
import os
from .translator import turkce_kodu_cevir

def trpy_calistir(dosya_yolu: str):
    with open(dosya_yolu, "r", encoding="utf-8") as f:
        turkce_kod = f.read()

    py_kod = turkce_kodu_cevir(turkce_kod)

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(py_kod)
        tmp_path = tmp.name

    try:
        subprocess.run([sys.executable, tmp_path], check=True)
    finally:
        os.unlink(tmp_path)

def cli_main():
    parser = argparse.ArgumentParser(description="Türkçe Python (.trpy) dosyasını çalıştır")
    parser.add_argument("dosya", help=".trpy dosyası")
    args = parser.parse_args()
    trpy_calistir(args.dosya)
