from flask import Flask, render_template, request
from blockchain import Blockchain
import os
import qrcode
from xhtml2pdf import pisa

app = Flask(__name__)

QR_FOLDER = 'static/qrs'
PDF_FOLDER = 'certificados/certs_generados'
JSON_FILE = 'registros.json'

os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

blockchain = Blockchain(file_path=JSON_FILE)

def generar_pdf(html_string, pdf_path):
    with open(pdf_path, "w+b") as f:
        pisa.CreatePDF(html_string, dest=f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    cedula = request.form['cedula']

    datos = {'nombre': nombre, 'apellido': apellido, 'cedula': cedula}
    bloque = blockchain.add_block(datos)

    hash_code = bloque.hash

    qr_path = f"{QR_FOLDER}/{hash_code}.png"
    qr = qrcode.make(hash_code)
    qr.save(qr_path)

    rendered_html = render_template('certificado.html', data=datos, hash=hash_code, qr_path=qr_path)

    pdf_path = f"{PDF_FOLDER}/{hash_code}.pdf"
    generar_pdf(rendered_html, pdf_path)

    return render_template('certificado.html', data=datos, hash=hash_code, qr_path=qr_path)

@app.route('/verificar/<hash_code>')
def verificar(hash_code):
    chain = blockchain.chain
    certificado = None
    for block in chain:
        if block.hash == hash_code:
            certificado = block
            break
    return render_template("verificar.html", certificado=certificado, hash_code=hash_code)

if __name__ == '__main__':
    app.run(debug=True)
