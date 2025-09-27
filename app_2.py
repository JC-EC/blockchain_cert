from flask import Flask, render_template, request
from blockchain import Blockchain
import os
import qrcode
from xhtml2pdf import pisa
import re
from unidecode import unidecode  # Para eliminar tildes y caracteres especiales
import ipfshttpclient #agrega la libreria de ipfs

app = Flask(__name__)

QR_FOLDER = 'static/qrs'
PDF_FOLDER = 'certificados/certs_generados'
JSON_FILE = 'registros.json'

os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

blockchain = Blockchain(file_path=JSON_FILE)
ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http') # Conectar a IPFS

def generar_pdf(html_string, pdf_path):
    with open(pdf_path, "w+b") as f:
        pisa.CreatePDF(html_string, dest=f)

def normalizar_texto(texto):
    # Eliminar tildes
    texto = unidecode(texto)
    # Convertir a mayÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¾Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Âºsculas
    texto = texto.upper()
    # Eliminar caracteres que no sean letras o nÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¾Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Âºmeros
    texto = re.sub(r'[^A-Z0-9]', '', texto)
    return texto

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    cedula = request.form['cedula']

# Diccionario de datos:
    ipfs_pdf_url = None
    ipfs_qr_url = None

    datos = {
        'nombre': nombre,
        'apellido': apellido,
        'cedula': cedula,
        'ipfs_pdf': ipfs_pdf_url,
        'ipfs_qr': ipfs_qr_url
    }

    # datos = {'nombre': nombre, 'apellido': apellido, 'cedula': cedula}
    bloque = blockchain.add_block(datos)


    hash_code = bloque.hash

    # Normalizar nombre y apellido para PDF y QR
    nombre_pdf = normalizar_texto(nombre)
    apellido_pdf = normalizar_texto(apellido)
    archivo_base = f"{nombre_pdf}_{apellido_pdf}"

    # Generar QR con el mismo nombre
    qr_path = f"{QR_FOLDER}/{archivo_base}.png"
    qr = qrcode.make(hash_code)
    qr.save(qr_path)

    rendered_html = render_template('certificado.html', data=datos, hash=hash_code, qr_path=qr_path)
    # Generar PDF
    pdf_path = f"{PDF_FOLDER}/{archivo_base}.pdf"
    generar_pdf(rendered_html, pdf_path)

   #SE Carga el PDF y el QR a IPFS
    # Subir PDF a IPFS
    import os

    if os.path.exists(pdf_path):
        res_pdf = ipfs_client.add(pdf_path)
        ipfs_pdf_url = f"https://ipfs.io/ipfs/{res_pdf['Hash']}"
    else:
        print(f"El archivo PDF no existe: {pdf_path}")

    if os.path.exists(qr_path):
        res_qr = ipfs_client.add(qr_path)
        ipfs_qr_url = f"https://ipfs.io/ipfs/{res_qr['Hash']}"
    else:
        print(f"El archivo QR no existe: {qr_path}")

    
    
    return render_template(
        'certificado.html',
        data=datos,
        hash=hash_code,
        qr_path=qr_path,
        ipfs_pdf_url=ipfs_pdf_url,
        ipfs_qr_url=ipfs_qr_url
    )

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
