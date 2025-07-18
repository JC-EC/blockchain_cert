from flask import Flask, render_template, request, send_file
from blockchain import Blockchain
import os

app = Flask(__name__)
bc = Blockchain()

@app.route('/')
def formulario():
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    cedula = request.form['cedula']
    
    data = {'nombre': nombre, 'apellido': apellido, 'cedula': cedula}
    bloque = bc.add_block(data)

    return render_template('certificado.html', data=data, hash=bloque.hash)

if __name__ == '__main__':
    app.run(debug=True)
