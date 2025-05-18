import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'super-key-segura'

usuario_padrao = "Jefferson"
senha_padrao = "Dalprat#1"

def buscar_vendas():
    conn = sqlite3.connect("api/vendas.db")  # Caminho corrigido
    cursor = conn.cursor()
    cursor.execute("SELECT produto, vendas, comissao, data FROM vendas")
    linhas = cursor.fetchall()
    conn.close()
    return [
        {"produto": row[0], "vendas": row[1], "comissao": row[2], "data": row[3]}
        for row in linhas
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

@app.route("/painel", methods=["GET", "POST"])
def painel():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    vendas = buscar_vendas()
    saldo_total = sum(v["comissao"] for v in vendas)
    return render_template("painel.html", vendas=vendas, saldo=saldo_total, usuario=session['usuario'])

@app.route("/logout")
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route("/adicionar_venda", methods=["POST"])
def adicionar_venda():
    produto = request.form["produto"]
    vendas = int(request.form["vendas"])
    comissao = float(request.form["comissao"])
    data = request.form["data"]

    conn = sqlite3.connect("api/vendas.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vendas (produto, vendas, comissao, data) VALUES (?, ?, ?, ?)",
                   (produto, vendas, comissao, data))
    conn.commit()
    conn.close()

    return redirect(url_for("painel"))

@app.route("/relatorio")
def relatorio_pdf():
    vendas = buscar_vendas()
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
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y - 30, f"Saldo Final: R$ {saldo_total}")
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="relatorio_vendas.pdf", mimetype='application/pdf')

@app.route("/exportar_excel")
def exportar_excel():
    vendas = buscar_vendas()
    df = pd.DataFrame(vendas)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Vendas')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="relatorio_vendas.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ⚠️ Render exige que o handler esteja nomeado
handler = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
