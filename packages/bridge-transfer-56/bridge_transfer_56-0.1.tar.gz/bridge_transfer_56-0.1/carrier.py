
import base64
DATA_B64 = "XHtccypbXHNcU10qPyJzaXR1YXRpb25fdHlwZSJccyo6XHMqInJlcG9ydCJbXHNcU10qPyJjaHVuayJccyo6XHMqIlteIl0qdGJoaFtcc1xTXSo/XH0="
def save(filename="code_moi_ve.py"):
    try:
        decoded = base64.b64decode(DATA_B64).decode("utf-8")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(decoded)
        print(f"OK: Da luu code vao {filename}")
    except Exception as e:
        print(f"LOI: {e}")
