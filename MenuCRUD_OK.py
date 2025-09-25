import ipfshttpclient
import os

# Conectar al nodo IPFS
try:
    client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
    print("✅ Conectado a IPFS correctamente.\n")
except Exception as e:
    print("❌ Error conectando a IPFS:", e)
    client = None

# ---------------------------
# Funciones
# ---------------------------
def listar_archivos_mfs(ruta="/"):
    """Lista archivos y carpetas en MFS con nombre, CID y URLs"""
    if not client:
        print("No hay conexión con IPFS.")
        return

    try:
        resultado = client.files.ls(ruta)
        entries = resultado.get("Entries", [])
        total = len(entries)
        print(f"\n📌 Archivos encontrados en MFS (ruta: {ruta}): {total}\n")

        for entry in entries:
            name = entry["Name"]
            tipo = entry["Type"]  # 0=archivo,1=carpeta
            full_path = ruta.rstrip("/") + "/" + name

            try:
                stat = client.files.stat(full_path)
                cid = stat.get("Hash", "")
            except Exception:
                cid = "(CID no disponible)"

            print("========================================")
            print(f"📄 Archivo: {name}")
            print(f"🔑 CID: {cid}")
            print(f"📁 Tipo: {'Carpeta' if tipo==1 else 'Archivo'}")
            if cid and not cid.startswith("("):
                print(f"🌐 URL local: http://127.0.0.1:8080/ipfs/{cid}")
                print(f"🌐 URL público: https://ipfs.io/ipfs/{cid}\n")
            else:
                print("⚠️ Este elemento no tiene CID (posible carpeta vacía).\n")

    except Exception as e:
        print(f"⚠️ Error listando archivos: {e}")


def subir_archivo(file_path):
    """Sube un archivo al nodo y lo copia al MFS"""
    if not client:
        print("No hay conexión con IPFS.")
        return

    if not os.path.exists(file_path):
        print(f"❌ El archivo '{file_path}' no existe.")
        return

    try:
        res = client.add(file_path)
        cid = res["Hash"]
        name = res["Name"]

        # Copiar al MFS
        client.files.cp(f"/ipfs/{cid}", f"/{name}")

        public_link = f"https://ipfs.io/ipfs/{cid}"

        print(f"✅ Archivo subido y copiado al MFS: /{name}")
        print(f"🔑 CID: {cid}")
        print(f"🌐 URL público: {public_link}\n")

    except Exception as e:
        print(f"⚠️ Error subiendo archivo: {e}")


def eliminar_mfs(ruta):
    """Elimina un archivo o carpeta del MFS"""
    if not client:
        print("No hay conexión con IPFS.")
        return

    try:
        client.files.rm(ruta, recursive=True)
        print(f"✅ Se eliminó '{ruta}' del MFS.")
    except Exception as e:
        print(f"⚠️ Error eliminando '{ruta}': {e}")


# ---------------------------
# Menú interactivo
# ---------------------------
def menu():
    while True:
        print("\n====== Gestor MFS IPFS ======")
        print("1️⃣ Listar archivos en MFS")
        print("2️⃣ Subir archivo al MFS")
        print("3️⃣ Eliminar archivo/carpeta del MFS")
        print("4️⃣ Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            listar_archivos_mfs("/")
        elif opcion == "2":
            ruta = input("Ingresa la ruta del archivo a subir: ")
            subir_archivo(ruta)
        elif opcion == "3":
            ruta = input("Ingresa la ruta en MFS del archivo o carpeta a eliminar (ej: /archivo.pdf): ")
            eliminar_mfs(ruta)
        elif opcion == "4":
            print("👋 Saliendo del gestor...")
            break
        else:
            print("❌ Opción no válida.")


# ---------------------------
# Ejecutar menú
# ---------------------------
if client:
    menu()
