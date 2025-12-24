#!/usr/bin/env python3
import argparse
import hashlib
import base64
import uuid
import getpass
from pathlib import Path
import sys
import hmac

SHOPIER_URL = "https://www.shopier.com/ShowProduct/api_pay4.php"
CONFIG_FILE = "shopier_config.py"

# =========================
# SDK
# =========================
class Shopier:
    def __init__(self, api_key, api_secret, account_id):
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.account_id = account_id

    def create_payment(self, product_name, price, buyer_email, success_url, fail_url):
        return self._build_form(product_name, price, buyer_email, success_url, fail_url)

    def create_donation(self, price, buyer_email, success_url, fail_url):
        return self._build_form(
            product_name="Bağış",
            price=price,
            buyer_email=buyer_email,
            success_url=success_url,
            fail_url=fail_url
        )

    def _build_form(self, product_name, price, buyer_email, success_url, fail_url):
        order_id = str(uuid.uuid4())
        data = {
            "API_key": self.api_key,
            "website_index": self.account_id,
            "platform_order_id": order_id,
            "product_name": product_name,
            "buyer_email": buyer_email,
            "total_order_value": f"{price:.2f}",
            "currency": "TRY",
            "success_url": success_url,
            "fail_url": fail_url,
            "payment_type": "card",
            "installment": 0,
            "current_language": 0
        }
        data["signature"] = self._sign(data)
        return data

    def _sign(self, data):
        raw = "".join(str(data[k]) for k in sorted(data)).encode()
        digest = hmac.new(self.api_secret, raw, hashlib.sha256).digest()
        return base64.b64encode(digest).decode()

    def verify_webhook(self, payload: bytes, received_signature: str) -> bool:
        expected = hmac.new(self.api_secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, received_signature)

# =========================
# HTML OTOMATİK FORM
# =========================
def generate_auto_form(form_data: dict) -> str:
    inputs = ""
    for k, v in form_data.items():
        inputs += f'<input type="hidden" name="{k}" value="{v}">\n'

    return f"""<!DOCTYPE html>
<html lang="tr">
<head><meta charset="utf-8"><title>Shopier</title></head>
<body onload="document.forms[0].submit()">
<form method="POST" action="{SHOPIER_URL}">
{inputs}
<noscript><button>Devam Et</button></noscript>
</form>
</body>
</html>"""

# =========================
# CONFIG
# =========================
def save_config(api_key, api_secret, account_id):
    Path(CONFIG_FILE).write_text(
        f'API_KEY="{api_key}"\nAPI_SECRET="{api_secret}"\nACCOUNT_ID="{account_id}"\n',
        encoding="utf-8"
    )

def load_config():
    if not Path(CONFIG_FILE).exists():
        print("❌ Önce: shopier init")
        sys.exit(1)
    cfg = {}
    exec(Path(CONFIG_FILE).read_text(), cfg)
    return cfg

# =========================
# TALİMAT
# =========================
TALIMAT = """
SHOPIER PYTHON SDK

Komutlar:
- shopier init
- shopier pay
- shopier donate
- shopier talimat

Bağış:
shopier donate --price 50 --email a@b.com --success OK --fail FAIL

Webhook:
Python içinde:
shopier.verify_webhook(payload, signature)
"""

# =========================
# CLI
# =========================
def cmd_init():
    api_key = input("API KEY: ")
    api_secret = getpass.getpass("API SECRET: ")
    account_id = input("ACCOUNT ID: ")
    save_config(api_key, api_secret, account_id)
    print("✅ Ayarlar kaydedildi")

def cmd_pay(args, donate=False):
    cfg = load_config()
    s = Shopier(cfg["API_KEY"], cfg["API_SECRET"], cfg["ACCOUNT_ID"])
    if donate:
        data = s.create_donation(args.price, args.email, args.success, args.fail)
    else:
        data = s.create_payment(args.product, args.price, args.email, args.success, args.fail)
    html = generate_auto_form(data)
    Path(args.output).write_text(html, encoding="utf-8")
    print(f"✅ {args.output} oluşturuldu")

def cmd_talimat():
    print(TALIMAT)

def main():
    parser = argparse.ArgumentParser(prog="shopier")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init")
    sub.add_parser("talimat")

    pay = sub.add_parser("pay")
    donate = sub.add_parser("donate")

    for p in (pay, donate):
        p.add_argument("--price", type=float, required=True)
        p.add_argument("--email", required=True)
        p.add_argument("--success", required=True)
        p.add_argument("--fail", required=True)
        p.add_argument("--output", default="pay.html")

    pay.add_argument("--product", required=True)

    args = parser.parse_args()

    if args.cmd == "init":
        cmd_init()
    elif args.cmd == "pay":
        cmd_pay(args, donate=False)
    elif args.cmd == "donate":
        cmd_pay(args, donate=True)
    elif args.cmd == "talimat":
        cmd_talimat()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()