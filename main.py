from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
import json
from collections import Counter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas



Window.size = (360, 640)  # Tamaño para pruebas en escritorio


KV = '''

ScreenManager:
    LoginScreen:
    MainScreen:

<LoginScreen>:
    name: 'login'
    MDBoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 20
        MDTextField:
            id: username
            hint_text: "Nombre del vendedor"
            size_hint: None, None
            size: 280, 50
            pos_hint: {'center_x': 0.5}
        MDRaisedButton:
            text: "Iniciar Sesión"
            size_hint: None, None
            size: 200, 50
            pos_hint: {'center_x': 0.5}
            on_release: app.login(username.text)

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 20
        MDTextField:
            id: nombre_comprador
            hint_text: "Nombre del comprador"
            size_hint: None, None
            size: 280, 50
            pos_hint: {'center_x': 0.5}
        MDTextField:
            id: numeros_loteria
            hint_text: "Números de lotería (ej. 12x3, 45x2)"
            size_hint: None, None
            size: 280, 50
            pos_hint: {'center_x': 0.5}
        MDRaisedButton:
            text: "Vender"
            size_hint: None, None
            size: 200, 50
            pos_hint: {'center_x': 0.5}
            on_release: app.vender_loteria(nombre_comprador.text, numeros_loteria.text)
        MDRaisedButton:
            text: "Imprimir Ticket"
            size_hint: None, None
            size: 200, 50
            pos_hint: {'center_x': 0.5}
            on_release: app.imprimir_ticket()
        MDRaisedButton:
            text: "Venta Total"
            size_hint: None, None
            size: 200, 50
            pos_hint: {'center_x': 0.5}
            on_release: app.venta_total_pdf()
        MDRaisedButton:
            text: "Reiniciar Ventas"
            size_hint: None, None
            size: 200, 50
            pos_hint: {'center_x': 0.5}
            on_release: app.reiniciar_ventas()
'''

class LoginScreen(Screen):
    pass

class MainScreen(Screen):
    pass

class LoteriaApp(MDApp):
    ventas = []
    ticket_id = 1
    nombre_vendedor = ""

    def build(self):
        self.load_ventas()
        self.load_ticket_id()
        return Builder.load_string(KV)

    def login(self, nombre_vendedor):
        if nombre_vendedor:
            self.nombre_vendedor = nombre_vendedor
            self.root.current = 'main'
        else:
            self.show_dialog("Error", "Por favor, ingrese su nombre.")

    def vender_loteria(self, nombre_comprador, numeros_input):
        if not nombre_comprador or not numeros_input:
            self.show_dialog("Error", "Ingrese el nombre y los números de lotería.")
            return

        numeros_cantidad = numeros_input.split(',')
        numeros = []
        for item in numeros_cantidad:
            item = item.strip()
            if 'x' in item:
                numero, cantidad = item.split('x')
                numero = numero.strip()
                cantidad = int(cantidad.strip())
                numeros.extend([numero] * cantidad)
            else:
                numeros.append(item.strip())

        if numeros:
            contador = Counter(numeros)
            venta = {'nombre': nombre_comprador, 'numeros': numeros}
            self.ventas.append(venta)
            self.save_ventas()

            mensaje = f"¡Venta exitosa para {nombre_comprador}!\n"
            for numero, cantidad in contador.items():
                mensaje += f"Número {numero}: comprado {cantidad} veces\n"
            
            self.show_dialog_with_scroll("Venta Exitosa", mensaje)
        else:
            self.show_dialog("Error", "No hay números válidos.")

    def imprimir_ticket(self):
        if not self.ventas:
            self.show_dialog("Error", "No hay ventas para imprimir.")
            return

        venta = self.ventas[-1]
        nombre = venta['nombre']
        numeros = venta['numeros']
        contador = Counter(numeros)
        archivo_ticket = f"ticket_{self.ticket_id}.pdf"
        c = canvas.Canvas(archivo_ticket, pagesize=letter)
        c.drawString(100, 750, "Ticket de Lotería")
        c.drawString(100, 730, f"Nombre: {nombre}")

        y = 710
        for numero, cantidad in contador.items():
            c.drawString(100, y, f"Número {numero}: {cantidad} veces")
            y -= 20

        c.showPage()
        c.save()

        self.ticket_id += 1
        self.save_ticket_id()
        self.show_dialog("Ticket", f"Ticket guardado como {archivo_ticket}.")

    def venta_total_pdf(self):
        if not self.ventas:
            self.show_dialog("Error", "No hay ventas para generar el reporte.")
            return

        numeros_vendidos = [num for venta in self.ventas for num in venta['numeros']]
        contador = Counter(numeros_vendidos)
        archivo_ventas = "venta_total.pdf"
        c = canvas.Canvas(archivo_ventas, pagesize=letter)
        c.drawString(100, 750, "Reporte Total de Ventas")

        y = 730
        for numero, cantidad in sorted(contador.items(), key=lambda x: x[1], reverse=True):
            c.drawString(100, y, f"Número {numero}: {cantidad} veces vendido")
            y -= 20
            if y < 50:
                c.showPage()
                y = 750

        c.showPage()
        c.save()

        self.show_dialog("Reporte", f"Reporte guardado como {archivo_ventas}.")

    def reiniciar_ventas(self):
        self.ventas = []
        self.ticket_id = 1
        self.save_ventas()
        self.show_dialog("Reiniciar", "Ventas reiniciadas.")

    def show_dialog(self, title, text):
        if not hasattr(self, '_dialog'):
            self._dialog = None
        if self._dialog:
            self._dialog.dismiss()

        self._dialog = MDDialog(title=title, text=text)
        self._dialog.open()

    def show_dialog_with_scroll(self, title, message):
        content = BoxLayout(orientation='vertical')
        label = MDLabel(text=message, size_hint_y=None, height=200)
        scroll = ScrollView()
        scroll.add_widget(label)
        content.add_widget(scroll)

        dialog = MDDialog(title=title, type="custom", content_cls=content)
        dialog.open()

    def save_ventas(self):
        with open('ventas.json', 'w') as f:
            json.dump(self.ventas, f)

    def load_ventas(self):
        try:
            with open('ventas.json', 'r') as f:
                self.ventas = json.load(f)
        except FileNotFoundError:
            self.ventas = []

    def save_ticket_id(self):
        with open('ticket_id.json', 'w') as f:
            json.dump({'ticket_id': self.ticket_id}, f)

    def load_ticket_id(self):
        try:
            with open('ticket_id.json', 'r') as f:
                self.ticket_id = json.load(f).get('ticket_id', 1)
        except FileNotFoundError:
            self.ticket_id = 1

if __name__ == '__main__':
    LoteriaApp().run()
