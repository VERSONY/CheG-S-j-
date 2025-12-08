import re
import sqlite3
from pathlib import Path
from flask import Flask, render_template_string, request

app = Flask(__name__)

# 🔧 CONFIGURE AQUI SEU NÚMERO DE WHATSAPP
WHATSAPP_NUMBER = "5512996677213"  
WHATSAPP_MESSAGE = "Olá, quero pedir gás com a cheGÁS Já!"

DB_PATH = Path("clientes.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefone TEXT UNIQUE NOT NULL,
            criado_em TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


init_db()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>cheGÁS Já</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Manifest do PWA -->
  <link rel="manifest" href="/static/manifest.json">
  <!-- Cor da barra do navegador / app -->
  <meta name="theme-color" content="#FF6B00">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }

    body {
      background: #f5f5f5;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 20px;
    }
    .card {
      background: #ffffff;
      max-width: 420px;
      width: 100%;
      border-radius: 16px;
      padding: 24px 20px 28px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.08);
      text-align: center;
    }
    .logo {
      font-size: 28px;
      font-weight: 700;
      color: #FF6B00;
      margin-bottom: 8px;
    }
    .subtitle {
      font-size: 14px;
      color: #555;
      margin-bottom: 18px;
    }
    .highlight {
      background: #FFF3BD;
      padding: 8px 12px;
      border-radius: 10px;
      font-size: 13px;
      color: #8a5a00;
      margin-bottom: 18px;
      display: inline-block;
    }
    form {
      margin-bottom: 16px;
    }
    input[type="tel"] {
      width: 100%;
      padding: 10px 12px;
      margin-bottom: 10px;
      border-radius: 8px;
      border: 1px solid #ccc;
      font-size: 14px;
    }
    button[type="submit"] {
      width: 100%;
      padding: 10px 12px;
      border-radius: 8px;
      border: none;
      background: #FF6B00;
      color: #fff;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      margin-bottom: 8px;
    }
    button[type="submit"]:hover {
      opacity: 0.95;
    }
    .msg {
      font-size: 13px;
      margin-bottom: 12px;
    }
    .msg-ok { color: #0a7a20; }
    .msg-erro { color: #b00020; }
    .whatsapp-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      text-decoration: none;
      background: #25D366;
      color: #ffffff;
      font-weight: 600;
      font-size: 16px;
      padding: 14px 20px;
      border-radius: 999px;
      box-shadow: 0 6px 14px rgba(37,211,102,0.4);
      margin-bottom: 14px;
    }
    .whatsapp-btn:hover {
      opacity: 0.9;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">cheGÁS Já</div>
    <div class="subtitle">Cadastre seu WhatsApp e faça seu pedido</div>

    <div class="highlight">
      📲 Digite seu número para liberar o atendimento.
    </div>

    <form method="post">
      <input
        type="tel"
        name="telefone"
        placeholder="Ex: 55 12 99999-9999"
        value="{{ phone_value }}"
        required
      >
      <button type="submit">Cadastrar número</button>
    </form>

    {% if message %}
      <div class="msg {{ 'msg-ok' if success else 'msg-erro' }}">
        {{ message }}
      </div>
    {% endif %}

       {% if show_button %}
      <a
        class="whatsapp-btn"
        href="{{ whatsapp_url }}"
        target="_blank"
        rel="noopener noreferrer"
      >
        📱 Pedir gás agora
      </a>
    {% endif %}
  </div>

  <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function () {
        navigator.serviceWorker.register('/static/service-worker.js')
          .then(function (reg) {
            console.log('Service worker registrado com sucesso:', reg.scope);
          })
          .catch(function (err) {
            console.log('Erro ao registrar service worker:', err);
          });
      });
    }
  </script>
</body>
</html>

"""


@app.route("/", methods=["GET", "POST"])
def index():
    import urllib.parse
    message = None
    success = False
    show_button = False
    phone_value = ""

    if request.method == "POST":
        raw_phone = request.form.get("telefone", "")
        phone_value = raw_phone
        telefone = re.sub(r"\D", "", raw_phone)

        if len(telefone) < 8:
            message = "Número inválido. Inclua DDI + DDD."
        else:
            conn = get_db()
            conn.execute(
                "INSERT OR IGNORE INTO clientes (telefone, criado_em) VALUES (?, datetime('now'))",
                (telefone,),
            )
            conn.commit()
            conn.close()

            message = "Número registrado com sucesso! Agora você pode pedir seu gás."
            success = True
            show_button = True

    encoded_msg = urllib.parse.quote(WHATSAPP_MESSAGE)
    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}"

    return render_template_string(
        HTML_PAGE,
        message=message,
        success=success,
        show_button=show_button,
        whatsapp_url=whatsapp_url,
        phone_value=phone_value,
    )


if __name__ == "__main__":
    app.run(debug=True)
