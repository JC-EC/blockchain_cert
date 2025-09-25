from flask import Flask, render_template, request, url_for
from blockchain import Blockchain
import os
import qrcode
from xhtml2pdf import pisa
import re
from unidecode import unidecode  # Para eliminar tildes y caracteres especiales
import ipfshttpclient  # Librería para IPFS
from datetime import datetime , timezone
import pytz  # Librería para manejo de zonas horarias

app = Flask(__name__)

#fecha y hora de Ecuador 

# 🔽 Aquí agregamos el filtro
@app.template_filter("ecuador_time")
def ecuador_time(value):
    """Convierte un timestamp UNIX (float o int) a hora de Ecuador."""
    if value is None:
        return ""

    # Convertir a datetime consciente de UTC
    dt_utc = datetime.fromtimestamp(value, tz=timezone.utc)

    # Convertir a zona horaria de Ecuador
    ecuador_tz = pytz.timezone("America/Guayaquil")
    dt_ecuador = dt_utc.astimezone(ecuador_tz)

    return dt_ecuador.strftime("%d/%m/%Y %H:%M:%S")

#fin 

QR_FOLDER = 'static/qrs'
PDF_FOLDER = 'certificados/certs_generados'
JSON_FILE = 'registros.json'

os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

blockchain = Blockchain(file_path=JSON_FILE)
ipfs_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')  # Conectar a IPFS

def generar_pdf(html_string, pdf_path):
    with open(pdf_path, "w+b") as f:
        pisa.CreatePDF(html_string, dest=f)

def normalizar_texto(texto):
    texto = unidecode(texto)  # Eliminar tildes
    texto = texto.upper()      # Convertir a mayúsculas
    texto = re.sub(r'[^A-Z0-9]', '', texto)  # Solo letras y números
    return texto

def subir_pdf_a_ipfs(file_path):
    """
    Sube solo el PDF a IPFS local, lo pinea y lo copia al MFS.
    Devuelve la URL pública en ipfs.io
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: El archivo '{file_path}' no existe.")
        return None

    try:
        # Subir archivo PDF a IPFS
        res = ipfs_client.add(file_path)
        cid = res['Hash']
        file_name = res['Name']

        # Copiar al MFS para IPFS Desktop
        mfs_path = f"/{file_name}"
        ipfs_client.files.cp(f"/ipfs/{cid}", mfs_path)

        # Pin para asegurar que no se borre del nodo
        ipfs_client.pin.add(cid)

        # Link público
        public_link = f"https://ipfs.io/ipfs/{cid}"

        # Guardar link en archivo
        with open("ipfs_links.txt", "a") as f:
            f.write(f"{file_name}: {public_link}\n")

        print(f"✅ '{file_name}' subido a IPFS y disponible en MFS: {mfs_path}")
        return public_link

    except Exception as e:
        print(f"⚠️ Error subiendo '{file_path}' a IPFS: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

## REGISTRAR LOS CAMBIOS PARA ABAJO
@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    cedula = request.form['cedula']

    # Diccionario de datos
    datos = {
        'nombre': nombre,
        'apellido': apellido,
        'cedula': cedula,
        'ipfs_pdf': None
    }

    # 1️⃣ Crear bloque en blockchain
    bloque = blockchain.add_block(datos)
    hash_code = bloque.hash

    # Obtener timestamp del bloque
    timestamp = getattr(bloque, "timestamp", None)

    # Normalizar nombre y apellido para PDF y QR
    nombre_pdf = normalizar_texto(nombre)
    apellido_pdf = normalizar_texto(apellido)
    archivo_base = f"{nombre_pdf}_{apellido_pdf}"

    # === 2️⃣ Generar PDF temporal ===
    rendered_html_temp = render_template(
        'certificado.html',
        data=datos,
        hash=hash_code,
        qr_path=None,
        ipfs_pdf_url=None,
        verificar_url=url_for("verificar", hash_code=hash_code, _external=True),
        timestamp=timestamp,
        archivo_base=archivo_base  # 🔽 Pasamos archivo_base al template
    )
    pdf_path = f"{PDF_FOLDER}/{archivo_base}.pdf"
    generar_pdf(rendered_html_temp, pdf_path)

    # === 3️⃣ Subir PDF a IPFS ===
    ipfs_pdf_url = subir_pdf_a_ipfs(pdf_path)
    datos['ipfs_pdf'] = ipfs_pdf_url

    # === 4️⃣ Generar QR ===
    qr_path = f"{QR_FOLDER}/{archivo_base}.png"
    qr_content = ipfs_pdf_url if ipfs_pdf_url else url_for("verificar", hash_code=hash_code, _external=True)
    qr = qrcode.make(qr_content)
    qr.save(qr_path)

    # === 5️⃣ Generar PDF final incluyendo IPFS y QR ===
    rendered_html_final = render_template(
        'certificado.html',
        data=datos,
        hash=hash_code,
        qr_path=qr_path,
        ipfs_pdf_url=ipfs_pdf_url,
        verificar_url=url_for("verificar", hash_code=hash_code, _external=True),
        timestamp=timestamp,
        archivo_base=archivo_base
    )
    generar_pdf(rendered_html_final, pdf_path)

    # === 6️⃣ Render final al navegador ===
    return render_template(
        'certificado.html',
        data=datos,
        hash=hash_code,
        qr_path=qr_path,
        ipfs_pdf_url=ipfs_pdf_url,
        verificar_url=url_for("verificar", hash_code=hash_code, _external=True),
        timestamp=timestamp,
        archivo_base=archivo_base
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