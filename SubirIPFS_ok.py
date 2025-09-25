#Sube el archivo a IPFS local y lo pinea, además de copiarlo a MFS para que aparezca en IPFS Desktop
# nos devuelve la url pública en ipfs.io
# ==========================
# 📌 Script: subir_a_ipfs.py
# ==========================

import ipfshttpclient
import os

# 1. Conectar al nodo IPFS local
client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')

# 2. Ruta del archivo a subir
file_path = "certificados/certs_generados/JEFFSTA_CABARA.pdf"  # Cambia esto por tu archivo modifcrlo por una variable

try:
    # 3. Subir archivo a IPFS
    res = client.add(file_path)
    cid = res["Hash"]
    file_name = res["Name"]

    # 4. Copiar al MFS (para que aparezca en Archivos de IPFS Desktop)
    mfs_path = f"/{file_name}"
    client.files.cp(f"/ipfs/{cid}", mfs_path)

    # 5. Generar link público
    public_link = f"https://ipfs.io/ipfs/{cid}"

    # 6. Mostrar resultados
    print("✅ Archivo subido con éxito")
    print(f"   📂 Nombre: {file_name}")
    print(f"   🔗 CID: {cid}")
    print(f"   🌍 Link público: {public_link}")
    print(f"   📁 Disponible en MFS: {mfs_path}")

    # 7. Guardar link en un archivo de texto
    with open("ipfs_links.txt", "a") as f:
        f.write(f"{file_name}: {public_link}\n")

    print("📝 Link guardado en 'ipfs_links.txt'")

except FileNotFoundError:
    print(f"❌ Error: El archivo '{file_path}' no se encontró.")
except Exception as e:
    print(f"⚠️ Ocurrió un error: {e}")
