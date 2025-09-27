import os
import subprocess

# Ruta de tu proyecto
ruta_proyecto = r"C:\Users\jefferson.cabrera\Documents\blockchain_cert"

# Convertir todos los archivos .py de tu proyecto a UTF-8
for root, dirs, files in os.walk(ruta_proyecto):
    # Ignorar entorno virtual
    if "pruebaUEES" in dirs:
        dirs.remove("pruebaUEES")
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="cp1252") as f:
                    contenido = f.read()
                with open(path, "w", encoding="utf-8") as f:
                    f.write(contenido)
                print(f"Convertido a UTF-8: {path}")
            except Exception as e:
                print(f"Error en {path}: {e}")

# Ejecutar pipreqs ignorando el entorno virtual
pipreqs_exe = os.path.join(ruta_proyecto, "pruebaUEES", "Scripts", "pipreqs.exe")
if os.path.exists(pipreqs_exe):
    try:
        subprocess.run([pipreqs_exe, ruta_proyecto, "--force", "--ignore", "pruebaUEES"], check=True)
        print("requirements.txt generado correctamente")
    except subprocess.CalledProcessError as e:
        print("Error generando requirements.txt:", e)
else:
    print(f"No se encontrÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â³ pipreqs.exe en: {pipreqs_exe}")

# Renombrar a necesito.txt
original = os.path.join(ruta_proyecto, "requirements.txt")
nuevo = os.path.join(ruta_proyecto, "necesito_instalar.txt")
if os.path.exists(original):
    os.rename(original, nuevo)
    print(f"Archivo renombrado a: {nuevo}")
else:
    print("No se encontrÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â³ requirements.txt para renombrar")
