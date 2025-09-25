import ipfshttpclient

# Conectar al nodo IPFS
try:
    client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
    print("✅ Conectado a IPFS correctamente.\n")
except Exception as e:
    print("❌ Error conectando a IPFS:", e)
    client = None


def listar_archivos_mfs(ruta="/"):
    """
    Lista los archivos en el MFS (IPFS Desktop → Archivos),
    mostrando Nombre, CID y URLs de acceso.
    """
    if not client:
        print("No hay conexión con IPFS.")
        return

    try:
        resultado = client.files.ls(ruta)

        if "Entries" not in resultado or len(resultado["Entries"]) == 0:
            print("📂 No hay archivos en el MFS.")
            return

        total = len(resultado["Entries"])
        print(f"📌 {total} Archivos encontrados en MFS dentro de la ruta: '{ruta}'\n")


        for entry in resultado["Entries"]:
            name = entry["Name"]
            tipo = entry["Type"]  # 0 = archivo, 1 = directorio

            # Construir la ruta completa en el MFS
            full_path = ruta.rstrip("/") + "/" + name

            try:
                # Obtener el CID con files.stat
                stat = client.files.stat(full_path)
                cid = stat.get("Hash", "")
            except Exception:
                cid = "(CID no disponible)"

            print("========================================")
            print(f"📄 Archivo: {name}")
            print(f"🔑 CID: {cid}")
            print(f"📁 Tipo: {'Carpeta' if tipo == 1 else 'Archivo'}")
            if cid and not cid.startswith("("):  # Solo si hay un CID válido
                print(f"🌐 URL local: http://127.0.0.1:8080/ipfs/{cid}")
                print(f"🌐 URL público: https://ipfs.io/ipfs/{cid}\n")
            else:
                print("⚠️ Este elemento no tiene CID (posible carpeta vacía).\n")

    except Exception as e:
        print(f"⚠️ Error listando archivos en MFS: {e}")


# Ejecutar
listar_archivos_mfs("/")
