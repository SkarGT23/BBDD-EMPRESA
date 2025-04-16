from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from flask_migrate import Migrate
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comparativa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ---------- MODELOS ----------

class UsuarioEliminado(db.Model):
    __tablename__ = 'usuarios_eliminados'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    localidad = db.Column(db.String(255), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    telefono = db.Column(db.String(15), nullable=True)
    dni = db.Column(db.String(9), nullable=True)
    cuenta_bancaria = db.Column(db.String(20), nullable=True)
    fecha_eliminacion = db.Column(db.DateTime, nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    localidad = db.Column(db.String(255), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    telefono = db.Column(db.String(15), nullable=True)
    dni = db.Column(db.String(9), nullable=True)
    cuenta_bancaria = db.Column(db.String(20), nullable=True)
    pedidos = db.relationship('Pedido', backref='usuario', lazy=True, cascade='all, delete-orphan')

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    documento_identidad = db.Column(db.String(255))
    productos = db.relationship('Producto', backref='pedido', lazy=True, cascade='all, delete-orphan')

class Producto(db.Model):
    __tablename__ = 'productos'
    id_productos = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nombre_producto = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, nullable=False)

class ProductoInventario(db.Model):
    __tablename__ = 'productos_inventario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_agregado = db.Column(db.Date, nullable=True)

# Tabla intermedia para promociones y productos
promocion_producto = db.Table('promocion_producto',
    db.Column('promocion_id', db.Integer, db.ForeignKey('promociones.id')),
    db.Column('producto_id', db.Integer, db.ForeignKey('productos_inventario.id'))
)

class Promocion(db.Model):
    __tablename__ = 'promociones'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_promocion = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    productos = db.relationship('ProductoInventario', secondary=promocion_producto, backref='promociones')

# ---------- RUTAS PRINCIPALES ----------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/usuarios')
def mostrar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios_eliminados')
def usuarios_eliminados():
    usuarios = UsuarioEliminado.query.order_by(UsuarioEliminado.fecha_eliminacion.desc()).all()
    return render_template('usuarios_eliminados.html', usuarios=usuarios)

@app.route('/vaciar_papelera', methods=['POST'])
def vaciar_papelera():
    UsuarioEliminado.query.delete()
    db.session.commit()
    flash('Papelera vaciada correctamente.', 'success')
    return redirect(url_for('usuarios_eliminados'))

@app.route('/eliminar_usuarios_masivo', methods=['POST'])
def eliminar_usuarios_masivo():
    ids = request.form.getlist('usuario_ids')
    if ids:
        for id in ids:
            usuario = Usuario.query.get(id)
            if usuario:
                # Copiar datos a papelera antes de eliminar
                from datetime import datetime
                eliminado = UsuarioEliminado(
                    nombre=usuario.nombre,
                    edad=usuario.edad,
                    email=usuario.email,
                    localidad=usuario.localidad,
                    direccion=usuario.direccion,
                    telefono=usuario.telefono,
                    dni=usuario.dni,
                    cuenta_bancaria=usuario.cuenta_bancaria,
                    fecha_eliminacion=datetime.now()
                )
                db.session.add(eliminado)
                db.session.delete(usuario)
        db.session.commit()
        flash('Usuarios eliminados correctamente', 'success')
    else:
        flash('No seleccionaste ningún usuario.', 'warning')
    return redirect(url_for('mostrar_usuarios'))

@app.route('/eliminar_todos_usuarios')
def eliminar_todos_usuarios():
    usuarios = Usuario.query.all()
    for usuario in usuarios:
        # Copiar datos a papelera antes de eliminar
        from datetime import datetime
        eliminado = UsuarioEliminado(
            nombre=usuario.nombre,
            edad=usuario.edad,
            email=usuario.email,
            localidad=usuario.localidad,
            direccion=usuario.direccion,
            telefono=usuario.telefono,
            dni=usuario.dni,
            cuenta_bancaria=usuario.cuenta_bancaria,
            fecha_eliminacion=datetime.now()
        )
        db.session.add(eliminado)
        db.session.delete(usuario)
    db.session.commit()
    flash('¡Todos los usuarios han sido eliminados!', 'danger')
    return redirect(url_for('mostrar_usuarios'))

@app.route('/buscar_usuario', methods=['GET', 'POST'])
def buscar_usuario():
    from sqlalchemy.orm import joinedload
    nombre = apellidos = dni = localidad = articulo = edad = telefono = email = None
    usuarios = None
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        dni = request.form.get('dni')
        localidad = request.form.get('localidad')
        codigo_postal = request.form.get('codigo_postal')
        articulo = request.form.get('articulo')
        edad = request.form.get('edad')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        query = Usuario.query
        if nombre:
            query = query.filter(Usuario.nombre.ilike(f'%{nombre}%'))
        if apellidos and hasattr(Usuario, 'apellidos'):
            query = query.filter(Usuario.apellidos.ilike(f'%{apellidos}%'))
        if dni:
            query = query.filter(Usuario.dni.ilike(f'%{dni}%'))
        if localidad:
            query = query.filter(Usuario.localidad.ilike(f'%{localidad}%'))
        if codigo_postal and hasattr(Usuario, 'codigo_postal'):
            query = query.filter(Usuario.codigo_postal.ilike(f'%{codigo_postal}%'))
        if edad:
            try:
                query = query.filter(Usuario.edad==int(edad))
            except ValueError:
                pass
        if telefono:
            query = query.filter(Usuario.telefono.ilike(f'%{telefono}%'))
        if email:
            query = query.filter(Usuario.email.ilike(f'%{email}%'))
        if articulo:
            query = query.join(Usuario.pedidos).join(Pedido.productos).filter(Producto.nombre_producto.ilike(f'%{articulo}%'))
        usuarios = query.options(joinedload(Usuario.pedidos)).all()
        return render_template('buscar_usuario.html', usuarios=usuarios)
    return render_template('buscar_usuario.html', usuarios=None)


@app.route('/insertar_usuario', methods=['GET', 'POST'])
def insertar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = request.form['edad']
        email = request.form['email']
        localidad = request.form.get('localidad')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        dni = request.form.get('dni')
        cuenta_bancaria = request.form.get('cuenta_bancaria')

        nuevo_usuario = Usuario(
            nombre=nombre, edad=edad, email=email,
            localidad=localidad, direccion=direccion,
            telefono=telefono, dni=dni, cuenta_bancaria=cuenta_bancaria
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Usuario insertado correctamente', 'success')
        return redirect(url_for('mostrar_usuarios'))

    return render_template('insertar_usuario.html')

@app.route('/actualizar_usuario/<int:id>', methods=['GET', 'POST'])
def actualizar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.edad = request.form['edad']
        usuario.email = request.form['email']
        usuario.localidad = request.form.get('localidad')
        usuario.direccion = request.form.get('direccion')
        usuario.telefono = request.form.get('telefono')
        usuario.dni = request.form.get('dni')
        usuario.cuenta_bancaria = request.form.get('cuenta_bancaria')

        db.session.commit()
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('mostrar_usuarios'))

    return render_template('actualizar_usuario.html', usuario=usuario)

@app.route('/eliminar_usuario/<int:id>', methods=['GET', 'POST'])
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado correctamente', 'success')
        return redirect(url_for('mostrar_usuarios'))

    return render_template('confirmar_eliminacion.html', usuario=usuario)

@app.route('/insertar_datos')
def insertar_datos():
    usuario1 = Usuario(nombre='María González', edad=28, email='maria.gonzalez@example.com')
    usuario2 = Usuario(nombre='Juan Pérez', edad=35, email='juan.perez@example.com')
    db.session.add_all([usuario1, usuario2])
    db.session.commit()

    pedido1 = Pedido(usuario_id=usuario1.id, total=120.50, fecha=date(2025, 4, 5), documento_identidad='DOC12345678')
    db.session.add(pedido1)
    db.session.commit()

    producto1 = Producto(pedido_id=pedido1.id, usuario_id=usuario1.id, nombre_producto='Laptop', cantidad=1, precio=120.50, fecha=date(2025, 4, 5))
    db.session.add(producto1)
    db.session.commit()

    return redirect(url_for('mostrar_usuarios'))

# ---------- PRODUCTOS INVENTARIO ----------

@app.route('/agregar_a_promocion/<int:id>')
def agregar_a_promocion(id):
    producto = ProductoInventario.query.get_or_404(id)
    # Buscar una promoción activa (por simplicidad, la más reciente)
    promocion = Promocion.query.order_by(Promocion.fecha_inicio.desc()).first()
    if not promocion:
        # Si no hay promociones, crear una de ejemplo temporal
        from datetime import date, timedelta
        hoy = date.today()
        promocion = Promocion(
            tipo_promocion='Temporal',
            valor=0,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=30)
        )
        db.session.add(promocion)
        db.session.commit()
    # Añadir el producto a la promoción
    if producto not in promocion.productos:
        promocion.productos.append(producto)
        db.session.commit()
        flash('Producto añadido a la promoción', 'success')
    else:
        flash('El producto ya está en la promoción', 'info')
    return redirect(url_for('ver_productos'))

@app.route('/productos', methods=['GET'])
def ver_productos():
    query = ProductoInventario.query
    nombre = request.args.get('nombre', '').strip()
    proveedor = request.args.get('proveedor', '').strip()
    importe_min = request.args.get('importe_min', '').strip()
    importe_max = request.args.get('importe_max', '').strip()
    if nombre:
        query = query.filter(ProductoInventario.nombre.ilike(f'%{nombre}%'))
    if proveedor and hasattr(ProductoInventario, 'proveedor'):
        query = query.filter(ProductoInventario.proveedor.ilike(f'%{proveedor}%'))
    if importe_min:
        try:
            query = query.filter(ProductoInventario.precio >= float(importe_min))
        except ValueError:
            pass
    if importe_max:
        try:
            query = query.filter(ProductoInventario.precio <= float(importe_max))
        except ValueError:
            pass
    productos = query.all()
    return render_template('productos.html', productos=productos)

@app.route('/agregar_a_promocion_masivo', methods=['POST'])
def agregar_a_promocion_masivo():
    ids = request.form.getlist('producto_ids')
    if not ids:
        flash('No seleccionaste productos.', 'warning')
        return redirect(url_for('ver_productos'))
    # Buscar promoción activa (la más reciente)
    promocion = Promocion.query.order_by(Promocion.fecha_inicio.desc()).first()
    if not promocion:
        from datetime import date, timedelta
        hoy = date.today()
        promocion = Promocion(
            tipo_promocion='Temporal',
            valor=0,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=30)
        )
        db.session.add(promocion)
        db.session.commit()
    count = 0
    for id in ids:
        producto = ProductoInventario.query.get(id)
        if producto and producto not in promocion.productos:
            promocion.productos.append(producto)
            count += 1
    db.session.commit()
    if count:
        flash(f'{count} producto(s) añadidos a la promoción.', 'success')
    else:
        flash('Los productos seleccionados ya están en la promoción.', 'info')
    return redirect(url_for('ver_productos'))

@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        precio = request.form['precio']
        descripcion = request.form.get('descripcion')
        fecha_str = request.form.get('fecha')

        fecha = None
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Formato de fecha incorrecto. Usa YYYY-MM-DD', 'error')

        nuevo_producto = ProductoInventario(
            nombre=nombre,
            cantidad=int(cantidad),
            precio=float(precio),
            descripcion=descripcion,
            fecha_agregado=fecha
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        flash('Producto agregado correctamente', 'success')
        return redirect(url_for('ver_productos'))

    return render_template('agregar_producto.html')

@app.route('/eliminar_producto/<int:id>', methods=['GET', 'POST'])
def eliminar_producto(id):
    producto = ProductoInventario.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado correctamente', 'success')
        return redirect(url_for('ver_productos'))

    return render_template('confirmar_eliminacion_producto.html', producto=producto)

# ---------- PROMOCIONES ----------
@app.route('/crear_promocion', methods=['GET', 'POST'])
def crear_promocion():
    productos = ProductoInventario.query.all()
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        tipo_promocion = request.form['tipo_promocion']
        valor = float(request.form['valor'])
        from datetime import datetime
        fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date()
        productos_ids = request.form.getlist('productos')
        if not nombre:
            flash('El nombre de la promoción es obligatorio.', 'danger')
            return render_template('crear_promocion.html', productos=productos)
        nueva_promocion = Promocion(nombre=nombre, tipo_promocion=tipo_promocion, valor=valor, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        for pid in productos_ids:
            producto = ProductoInventario.query.get(int(pid))
            if producto:
                nueva_promocion.productos.append(producto)
        db.session.add(nueva_promocion)
        db.session.commit()
        flash('Promoción creada correctamente', 'success')
        return redirect(url_for('ver_promociones'))
    return render_template('crear_promocion.html', productos=productos)

@app.route('/promociones')
def ver_promociones():
    buscar = request.args.get('buscar', '').strip()
    query = Promocion.query
    if buscar:
        query = query.filter(
            (Promocion.tipo_promocion.ilike(f'%{buscar}%')) |
            (Promocion.valor.ilike(f'%{buscar}%'))
        )
    promociones = query.order_by(Promocion.fecha_inicio.desc()).all()
    return render_template('promociones.html', promociones=promociones)

@app.route('/promocion/<int:id>')
def ver_promocion(id):
    promo = Promocion.query.get_or_404(id)
    return render_template('ver_promocion.html', promo=promo)

@app.route('/editar_promocion/<int:id>', methods=['GET', 'POST'])
def editar_promocion(id):
    promo = Promocion.query.get_or_404(id)
    todos_los_productos = ProductoInventario.query.all()
    if request.method == 'POST':
        promo.tipo_promocion = request.form['tipo_promocion']
        promo.valor = float(request.form['valor'])
        promo.fecha_inicio = request.form['fecha_inicio']
        promo.fecha_fin = request.form['fecha_fin']
        productos_ids = request.form.getlist('productos')
        promo.productos.clear()
        for pid in productos_ids:
            producto = ProductoInventario.query.get(int(pid))
            if producto:
                promo.productos.append(producto)
        db.session.commit()
        flash('Promoción actualizada correctamente', 'success')
        return redirect(url_for('ver_promociones'))
    return render_template('editar_promocion.html', promo=promo, todos_los_productos=todos_los_productos)

@app.route('/eliminar_promocion/<int:id>', methods=['POST'])
def eliminar_promocion(id):
    promo = Promocion.query.get_or_404(id)
    db.session.delete(promo)
    db.session.commit()
    flash('Promoción eliminada correctamente', 'success')
    return redirect(url_for('ver_promociones'))

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefonos = db.Column(db.Text, nullable=True)  # Separados por coma
    correos = db.Column(db.Text, nullable=True)    # Separados por coma
    localidad = db.Column(db.String(100), nullable=True)
    codigo_postal = db.Column(db.String(20), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)

# === MODELO NOTA ===
class Nota(db.Model):
    __tablename__ = 'notas'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    texto = db.Column(db.Text, nullable=False)

# === RUTAS PROVEEDORES ===
@app.route('/proveedores')
def ver_proveedores():
    nombre = request.args.get('nombre', '').strip()
    localidad = request.args.get('localidad', '').strip()
    telefono = request.args.get('telefono', '').strip()

    query = Proveedor.query
    if nombre:
        query = query.filter(Proveedor.nombre.ilike(f"%{nombre}%"))
    if localidad:
        query = query.filter(Proveedor.localidad.ilike(f"%{localidad}%"))
    if telefono:
        query = query.filter(Proveedor.telefonos.ilike(f"%{telefono}%"))

    proveedores = query.all()
    return render_template('proveedores.html', proveedores=proveedores, filtro_nombre=nombre, filtro_localidad=localidad, filtro_telefono=telefono)

@app.route('/proveedor/nuevo', methods=['GET', 'POST'])
def agregar_proveedor():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        telefonos = request.form['telefonos'].strip()
        correos = request.form['correos'].strip()
        localidad = request.form['localidad'].strip()
        codigo_postal = request.form['codigo_postal'].strip()
        descripcion = request.form['descripcion'].strip()
        proveedor = Proveedor(
            nombre=nombre,
            telefonos=telefonos,
            correos=correos,
            localidad=localidad,
            codigo_postal=codigo_postal,
            descripcion=descripcion
        )
        db.session.add(proveedor)
        db.session.commit()
        flash('Proveedor añadido correctamente', 'success')
        return redirect(url_for('ver_proveedores'))
    return render_template('agregar_proveedor.html')

@app.route('/proveedor/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    if request.method == 'POST':
        proveedor.nombre = request.form['nombre'].strip()
        proveedor.telefonos = request.form['telefonos'].strip()
        proveedor.correos = request.form['correos'].strip()
        proveedor.localidad = request.form['localidad'].strip()
        proveedor.codigo_postal = request.form['codigo_postal'].strip()
        proveedor.descripcion = request.form['descripcion'].strip()
        db.session.commit()
        flash('Proveedor actualizado correctamente', 'success')
        return redirect(url_for('ver_proveedores'))
    return render_template('editar_proveedor.html', proveedor=proveedor)

@app.route('/proveedor/eliminar/<int:id>', methods=['POST'])
def eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    db.session.delete(proveedor)
    db.session.commit()
    flash('Proveedor eliminado correctamente', 'success')
    return redirect(url_for('ver_proveedores'))

# ---------- ZONA DE NOTAS ----------
from datetime import datetime

@app.route('/notas', methods=['GET', 'POST'])
def zona_notas():
    if request.method == 'POST':
        fecha_str = request.form.get('fecha')
        texto = request.form.get('nota', '').strip()
        if fecha_str and texto:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            nota = Nota(fecha=fecha, texto=texto)
            db.session.add(nota)
            db.session.commit()
            flash('Nota agregada correctamente', 'success')
        else:
            flash('Debes introducir una fecha y una nota.', 'danger')
        return redirect(url_for('zona_notas'))
    notas = Nota.query.order_by(Nota.fecha.desc()).all()
    return render_template('zona_notas.html', notas=notas)

@app.route('/notas/eliminar/<int:nota_id>', methods=['POST'])
def eliminar_nota(nota_id):
    nota = Nota.query.get_or_404(nota_id)
    db.session.delete(nota)
    db.session.commit()
    flash('Nota eliminada.', 'success')
    return redirect(url_for('zona_notas'))

# ---------- MAIN ----------
# --- BLOQUE TEMPORAL PARA CREAR TABLAS ---
with app.app_context():
    db.create_all()
# --- FIN BLOQUE TEMPORAL ---

if __name__ == '__main__':
    app.run(debug=True)

