from flask import Flask, render_template, request, redirect, url_for, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import io

app = Flask(__name__)

# Configurações de usuário
usuario_padrao = "Jefferson"
senha_padrao = "Dalprat#1"

# Dados fictícios de vendas
vendas = [
    {"produto": "Curso Python", "vendas": 12, "comissao": 150.00},
    {"produto": "E-book Marketing", "vendas": 8, "comissao": 80.00},
    {"produto": "Mentoria Online", "vendas": 5, "comissao": 500.00},
    {"produto": "Software de Automação", "vendas": 3, "comissao": 1000.00}
]

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        if usuario == usuario_padrao and senha == senha_padrao:
            return redirect(url_for("painel"))
    return render_template("login.html")

@app.route("/painel")
def painel():
    saldo_total = sum(v["comissao"] for v in vendas)
    produtos = [v["produto"] for v in vendas]
    comissoes = [v["comissao"] for v in vendas]
    return render_template("painel.html", vendas=vendas, saldo=saldo_total, produtos=produtos, comissoes=comissoes)

@app.route("/relatorio")
def relatorio_pdf():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    largura, altura = letter

    # Inserir logotipo (opcional)
    try:
        logo = ImageReader('logo.png')  # Se você quiser, coloca um logo.png na pasta do projeto
        pdf.drawImage(logo, 200, altura-100, width=200, preserveAspectRatio=True, mask='auto')
    except:
        pass

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(largura / 2, altura - 150, "Relatório de Vendas")

    pdf.setFont("Helvetica", 12)
    y = altura - 180
    for venda in vendas:
        texto = f"Produto: {venda['produto']} | Vendas: {venda['vendas']} | Comissão: R$ {venda['comissao']}"
        pdf.drawString(50, y, texto)
        y -= 20
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = altura - 50

    saldo_total = sum(v["comissao"] for v in vendas)
    if y < 100:
        pdf.showPage()
        pdf.setFont("Helvetica", 12)
        y = altura - 100

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y - 30, f"Saldo Final: R$ {saldo_total}")

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="relatorio_vendas.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)
