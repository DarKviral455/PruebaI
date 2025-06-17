
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

import os

if __name__ == '__main__':
    if not os.path.exists(app.config ['UPLOAD_FOLDER']):
        os.makedirs(app.config [ 'UPLOAD_FOLDER'])
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", default=5000))


app = Flask(__name__)
app.secret_key = 'supersecretkey'

def database():
        connect = sqlite3.connect('bdexamen.db')  
        cursor = connect.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                usser TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tipocartera (
                codtipcar INTEGER PRIMARY KEY AUTOINCREMENT,
                nombtipcar TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cartera (
                codcar INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcar TEXT NOT NULL,
                codtipcar INTEGER,
                preciocar REAL,
                fechacar TEXT,
                FOREIGN KEY (codtipcar) REFERENCES tipocartera(codtipcar)
            )
        ''')

        cursor.execute('SELECT * FROM usuario')
        if not cursor.fetchall():
            cursor.execute("INSERT INTO usuario (usser, password) VALUES (?, ?)", ("krisdein", "1234"))

        cursor.execute('SELECT * FROM tipocartera')
        if not cursor.fetchall():
            tipos = [('ANDINO',), ('COSTEÑO',), ('SELVÁTICO',), ('TRADICIONAL',)]
            cursor.executemany("INSERT INTO tipocartera (nombtipcar) VALUES (?)", tipos)

        connect.commit()
        connect.close()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        with sqlite3.connect('bdexamen.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario WHERE usser=? AND password=?", (usuario, clave))
            user = cursor.fetchone()
            if user:
                session['usuario'] = usuario
                return redirect(url_for('principal'))
            else:
                error = '¡Credenciales Incorrectas!'
    return render_template('login.html', error=error)

@app.route('/principal')
def principal():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('principal.html')

@app.route('/GrabarCartera', methods=['GET', 'POST'])
def InsertarCartera():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect('bdexamen.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tipocartera")
        tipos = cursor.fetchall()
    mensaje = None
    if request.method == 'POST':
        descripcion = request.form['txtdescription']
        tipo = request.form['txttipocartera']
        precio = request.form['txtprecio']
        fecha = request.form['fecha']
        with sqlite3.connect('bdexamen.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cartera (descripcar, codtipcar, preciocar, fechacar) VALUES (?, ?, ?, ?)",
                           (descripcion, tipo, precio, fecha))
            conn.commit()
        mensaje = "¡Se grabó el registro satisfactoriamente!"
    return render_template('RegistrarCartera.html', tipos=tipos, mensaje=mensaje)

@app.route('/BuscarCartera', methods=['GET', 'POST'])
def ConsultarCartera():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    cartera = []
    with sqlite3.connect('bdexamen.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tipocartera")
        tipos = cursor.fetchall()
        if request.method == 'POST':
            tipo = request.form['txttipocartera']
            cursor.execute('''
                SELECT c.codcar, c.descripcar, t.nombtipcar, c.preciocar, c.fechacar
                FROM cartera c JOIN tipocartera t ON c.codtipcar = t.codtipcar
                WHERE c.codtipcar=?
            ''', (tipo,))
            cartera = cursor.fetchall()
    return render_template('ConsultarCartera.html', tipos=tipos, cartera=cartera)

if __name__ == '__main__':
    database()
    app.run(debug=True)
