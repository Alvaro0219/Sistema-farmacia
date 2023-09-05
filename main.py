import sys, datetime
import typing
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QWidget
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from conexion_sqlite import Comunicacion

class VentanaPrincipal(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        loadUi('diseño.ui', self)

        self.bt_menu.clicked.connect(self.mover_menu)
        self.base_datos = Comunicacion()
        self.producto = None  # Variable para almacenar el producto seleccionado

        # Lógica para definir colores según las fechas de vencimiento
        self.hoy = datetime.datetime.now()
        self.proximo_mes = self.hoy + datetime.timedelta(days=30)
        self.proximos_3_meses = self.hoy + datetime.timedelta(days=90)

        #Ocultamos botones
        self.bt_restaurar.hide()
        #botones
        self.bt_refrescar.clicked.connect(self.mostrar_productos)
        self.bt_agregar.clicked.connect(self.registrar_productos)
        self.bt_borrar.clicked.connect(self.eliminar_productos)
        self.bt_actualiza_tabla.clicked.connect(self.modificar_productos)
        self.bt_buscar_actualizar.clicked.connect(self.buscar_por_codigo_actualiza)
        self.bt_buscar_borrar.clicked.connect(self.buscar_por_codigo_eliminar)

        #control barra de titulos
        self.bt_minimizar.clicked.connect(self.control_bt_minimizar)
        self.bt_restaurar.clicked.connect(self.control_bt_normal)
        self.bt_maximizar.clicked.connect(self.control_bt_maximizar)
        self.bt_menu.clicked.connect(self.mover_menu)
        self.bt_cerrar.clicked.connect(lambda: self.close())

        #eliminar barra y de titulo - opacidad
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)

        #SizeGrip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        #Mover ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        #coneccion botones
        self.bt_datos.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_datos))
        self.bt_registrar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_registrar))
        self.bt_actualizar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_actualizar))
        self.bt_eliminar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_eliminar))
        self.bt_ajustes.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_ajustes))

        #ancho de columna adaptable
        self.tabla_borrar.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    ##BARRA DE TITULO
    def control_bt_minimizar(self):
        self.showMinimized()

    def control_bt_normal(self):
        self.showNormal()
        self.bt_restaurar.hide()
        self.bt_maximizar.show()

    def control_bt_maximizar(self):
        self.showMaximized()
        self.bt_maximizar.hide()
        self.bt_restaurar.show()

    ##SizeGrip
    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

    ##mover ventana
    def mousePressEvent(self, event):
        self.click_position = event.globalPos()

    def mover_ventana(self, event):
        if self.isMaximized() == False:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.click_position)
                self.click_position = event.globalPos()
                event.accept()
        if event.globalPos().y() <=10:
            self.showMaximized()
            self.bt_maximizar.hide()
            self.bt_restaurar.show()
        else:
            self.showNormal()
            self.bt_restaurar.hide()
            self.bt_maximizar.show()

    #Metodo menu lateral izquierdo
    def mover_menu(self):
        width = self.frame_2.width()
        normal = 0
        if width == 0:
            extender = 200
        else:
            extender = normal
        self.animacion = QPropertyAnimation(self.frame_2, b'minimumWidth')
        self.animacion.setDuration(300)
        self.animacion.setStartValue(width)
        self.animacion.setEndValue(extender)
        self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animacion.start()

    #Configuracion pagina base de datos
    def mostrar_productos(self):
        datos = self.base_datos.mostrar_productos()
        i = len(datos)
        self.tabla_productos.setRowCount(i)
        tablerow = 0
        for row in datos:
            self.Id = row[0]
            self.tabla_productos.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(row[1]))
            self.tabla_productos.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(row[2]))
            self.tabla_productos.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(row[3]))

            # Convertir la fecha de vencimiento en formato AAAA/MM a un objeto datetime
            fecha_vencimiento_str = row[3]  # Elimina la adición del último día del mes
            fecha_vencimiento = datetime.datetime.strptime(fecha_vencimiento_str, '%Y/%m')

            # Determinar el color de fondo según la fecha de vencimiento
            if fecha_vencimiento <= self.hoy:
                color = QtGui.QColor(255, 0, 0)  # Rojo
            elif fecha_vencimiento <= self.proximo_mes:
                color = QtGui.QColor(255, 165, 0)  # Amarillo
            elif fecha_vencimiento <= self.proximos_3_meses:
                color = QtGui.QColor(255, 255, 0)  # Naranja
            else:
                color = QtGui.QColor(0, 128, 0)  # Verde

            for col in range(self.tabla_productos.columnCount()):
                item = self.tabla_productos.item(tablerow, col)
                if item:
                    item.setBackground(color)

            tablerow += 1

        self.signal_actualizar.setText("")
        self.signal_registrar.setText("")
        self.signal_eliminar.setText("")


    def registrar_productos(self):
        codigo = self.reg_codigo.text().upper()
        nombre = self.reg_nombre.text().upper()
        vencimiento = self.reg_vencimiento.text().upper()

        if codigo != '' and nombre != '' and vencimiento != '':
            # Verificar si el código ya existe en la base de datos
            if self.base_datos.verificar_codigo_existente(codigo):
                self.signal_registrar.setText('El código ya existe. Ingrese otro código.')
            else:
                self.base_datos.insertar_productos(codigo, nombre, vencimiento)
                self.signal_registrar.setText('Productos registrados')
                self.reg_codigo.clear()
                self.reg_nombre.clear()
                self.reg_vencimiento.clear()
        else:
            self.signal_registrar.setText('Hay espacios vacíos')

    def buscar_por_codigo_actualiza(self):
        codigo_producto = self.act_buscar.text().upper()  # Obtener el código ingresado por el usuario
        self.producto = self.base_datos.buscar_productos(codigo_producto)  # Cambiar el método de búsqueda
        if self.producto:
            self.Id = self.producto[0][0]
            self.act_codigo.setText(self.producto[0][1])
            self.act_nombre.setText(self.producto[0][2])
            self.act_vencimiento.setText(self.producto[0][3])
            self.signal_actualizar.setText("")  # Limpiar la señal de error/success
        else:
            self.signal_actualizar.setText("NO EXISTE")

    def modificar_productos(self):
        if self.producto:
            nuevo_codigo = self.act_codigo.text().upper()
            nuevo_nombre = self.act_nombre.text().upper()
            nuevo_vencimiento = self.act_vencimiento.text().upper()

            # Obtener el código actual del producto
            codigo_actual = self.producto[0][1]

            if nuevo_codigo != codigo_actual and self.base_datos.verificar_codigo_existente(nuevo_codigo):
                self.signal_actualizar.setText("Código ya existe")
                return

            act = self.base_datos.actualizar_productos(self.Id, nuevo_codigo, nuevo_nombre, nuevo_vencimiento)
            if act == 1:
                self.signal_actualizar.setText("ACTUALIZADO")
                self.act_codigo.clear()
                self.act_nombre.clear()
                self.act_vencimiento.clear()
                self.act_buscar.setText('')
                self.producto = None  # Resetear el producto seleccionado
            elif act == 0:
                self.signal_actualizar.setText("ERROR")
            else:
                self.signal_actualizar.setText("INCORRECTO")
        else:
            self.signal_actualizar.setText("Ningún producto seleccionado")


    def buscar_por_codigo_eliminar(self):
        codigo_producto = self.eliminar_buscar.text().upper()  # Obtener el código ingresado por el usuario
        productos = self.base_datos.buscar_productos(codigo_producto)  # Cambiar el método de búsqueda
        if productos:
            self.tabla_borrar.setRowCount(len(productos))
            tablerow = 0
            for row in productos:
                self.producto_a_borrar = row[0]  # Usar el ID del producto para eliminar
                #self.tabla_borrar.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(row[0])))  # Mostrar ID en la primera columna
                self.tabla_borrar.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(row[1]))
                self.tabla_borrar.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(row[2]))
                self.tabla_borrar.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(row[3]))  # Fecha de vencimiento

                # Convertir la fecha de vencimiento en formato AAAA/MM a un objeto datetime
                fecha_vencimiento_str = row[3] + "/28"  # Usar el último día del mes
                fecha_vencimiento = datetime.datetime.strptime(fecha_vencimiento_str, '%Y/%m/%d')

                # Determinar el color de fondo según la fecha de vencimiento
                if fecha_vencimiento <= self.hoy:
                    color = QtGui.QColor(255, 0, 0)  # Rojo
                elif fecha_vencimiento <= self.proximo_mes:
                    color = QtGui.QColor(255, 165, 0)  # Amarillo
                elif fecha_vencimiento <= self.proximos_3_meses:
                    color = QtGui.QColor(255, 255, 0)  # Naranja
                else:
                    color = QtGui.QColor(0, 128, 0)  # Verde

                for col in range(self.tabla_borrar.columnCount()):
                    item = self.tabla_borrar.item(tablerow, col)
                    if item:
                        item.setBackground(color)

                tablerow += 1
            self.signal_eliminar.setText("PRODUCTO SELECCIONADO")
        else:
            self.signal_eliminar.setText("NO EXISTE")
        
    def eliminar_productos(self):
        print("Eliminar productos function called")
        if hasattr(self, 'producto_a_borrar') and self.producto_a_borrar is not None:
            print("Producto a borrar:", self.producto_a_borrar)
            codigo_producto_item = self.tabla_borrar.item(self.tabla_borrar.currentRow(), 0)
            if codigo_producto_item is not None:
                codigo_producto = codigo_producto_item.text()  # Obtener el código del producto
                print("Código de producto a eliminar:", codigo_producto)
                self.tabla_borrar.removeRow(self.tabla_borrar.currentRow())  # Eliminar la fila de la tabla
                if self.base_datos.eliminar_productos_por_codigo(codigo_producto):  # Cambiar la función de eliminación
                    self.signal_eliminar.setText('PRODUCTO ELIMINADO')
                    self.eliminar_buscar.setText('')
                    self.producto_a_borrar = None  # Reiniciar el producto seleccionado
                else:
                    self.signal_eliminar.setText('Error al eliminar el producto de la base de datos')
            else:
                self.signal_eliminar.setText('Error al obtener el código del producto de la tabla')
        else:
            self.signal_eliminar.setText('Ningún producto seleccionado')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mi_app = VentanaPrincipal()
    mi_app.show()
    sys.exit(app.exec_())
    mi_app.base_datos.cerrar_conexion() #cerrar conexion cuando la app termine
