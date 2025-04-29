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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import schedule
import time

def enviar_email_relatorio():
    remetente = "jrdalpratusa@gmail.com"
    senha = "ebfqoppyuxeodoeh"  # Sem espaços
    destinatario = "jrdalpratusa@gmail.com"

    # Criar o e-mail
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = "Relatório de Vendas - Dashboard Jefferson"
    corpo = "Segue em anexo o relatório de vendas do dia."
    msg.attach(MIMEText(corpo, 'plain'))

    # Gerar PDF na hora
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    largura, altura = letter
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(largura / 2, altura - 50, "Relatório de Vendas Diário")
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

    # Anexar o PDF no email
    anexo = MIMEApplication(buffer.read(), _subtype="pdf")
    anexo.add_header('Content-Disposition', 'attachment', filename="relatorio_vendas.pdf")
    msg.attach(anexo)

    # Enviar o e-mail
    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.send_message(msg)
        servidor.quit()
        print("Relatório enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# Para testar agora:
# enviar_email_relatorio()
# Agendar para enviar todo dia às 8h da manhã
schedule.every().day.at("08:00").do(enviar_email_relatorio)

# Rodar o agendador
while True:
    schedule.run_pending()
    time.sleep(60)
