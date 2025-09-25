import ipfshttpclient
import os
import pathlib
from datetime import datetime

# Ruta al repositorio de IPFS en Windows
IPFS_REPO = pathlib.Path.home() / ".ipfs" / "blocks"
LOG_FILE = "cids_eliminados.txt"

def folder_size(path):
    """Calcula el tamaño total de una carpeta en MB"""
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total / (1024 * 1024)  # convertir a MB

def limpiar_ipfs():
    try:
        client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
        print("✅ Conectado a IPFS")

        # Tamaño inicial
        print(f"📦 Tamaño inicial de 'blocks': {folder_size(IPFS_REPO):.2f} MB")

        # Listar pines correctamente
        pinned = client.pin.ls(type="all")
        pinned_cids = list(pinned["Keys"].keys()) if "Keys" in pinned else []
        print(f"📌 Archivos pinneados encontrados: {len(pinned_cids)}")

        # Abrir log para guardar los eliminados
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "="*40 + "\n")
            f.write(f"🗑️ Limpieza ejecutada: {datetime.now()}\n")

            # Eliminar cada pin
            for cid in pinned_cids:
                try:
                    client.pin.rm(cid)
                    print(f"❌ Pin eliminado: {cid}")
                    f.write(f"Pin eliminado: {cid}\n")
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar {cid}: {e}")
                    f.write(f"Error eliminando pin {cid}: {e}\n")

            # ✅ Eliminar archivos en MFS
            print("🗂️ Eliminando archivos en MFS...")
            try:
                mfs_ls = client.files.ls("/")
                for entry in mfs_ls["Entries"]:
                    path = f"/{entry['Name']}"
                    try:
                        client.files.rm(path, recursive=True)
                        print(f"❌ Archivo MFS eliminado: {path}")
                        f.write(f"MFS eliminado: {path}\n")
                    except Exception as e:
                        print(f"⚠️ No se pudo eliminar MFS {path}: {e}")
                        f.write(f"Error MFS {path}: {e}\n")
            except Exception as e:
                print(f"⚠️ Error listando MFS: {e}")
                f.write(f"Error listando MFS: {e}\n")

        # Garbage collection
        print("🧹 Ejecutando garbage collection...")
        client.repo.gc()

        # Tamaño final
        print(f"📦 Tamaño final de 'blocks': {folder_size(IPFS_REPO):.2f} MB")
        print(f"📑 Log guardado en: {LOG_FILE}")

    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    limpiar_ipfs()
