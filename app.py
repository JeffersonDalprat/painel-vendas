from flask import Flask, render_template, request, redirect, url_for, send_file, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import pandas as pd

app = Flask(__name__)
app.secret_key = 'super-key-segura'

usuario_padrao = "Jefferson"
senha_padrao = "Dalprat#1"

vendas = [
    {"produto": "Curso Python", "vendas": 12, "comissao": 150.00, "data": "2025-04-25"},
    {"produto": "E-book Marketing", "vendas": 8, "comissao": 80.00, "data": "2025-04-24"},
    {"produto": "Mentoria Online", "vendas": 5, "comissao": 500.00, "data": "2025-04-23"},
    {"produto": "Software de Automação", "vendas": 3, "comissao": 1000.00, "data": "2025-04-22"}
]

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        if usuario == usuario_padrao and senha == senha_padrao:
            session['usuario'] = usuario
            return redirect(url_for("painel"))
    return render_template("login.html")

@app.route("/painel")
def painel():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    saldo_total = sum(v["comissao"] for v in vendas)
    return render_template("painel.html", vendas=vendas, saldo=saldo_total, usuario=session['usuario'])

@app.route("/logout")
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route("/relatorio")
def relatorio_pdf():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    largura, altura = letter

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(largura / 2, altura - 50, "Relatório de Vendas")

    pdf.setFont("Helvetica", 12)
    y = altura - 100
    for venda in vendas:
        texto = f"Produto: {venda['produto']} | Vendas: {venda['vendas']} | Comissão: R$ {venda['comissao']} | Data: {venda['data']}"
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

@app.route("/exportar_excel")
def exportar_excel():
    df = pd.DataFrame(vendas)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Vendas')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="relatorio_vendas.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run()
