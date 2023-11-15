from tkinter import Tk, Label, Entry, Button, StringVar, ttk, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import os
import platform

class Aplicacion:
    def __init__(self, master):
        
        self.master = master
        master.title("Automatización")
        
    # Crear un objeto de estilo ttk
        style = ttk.Style()

        # Definir un nuevo estilo para los Combobox
        style.configure('TCombobox', background='white')

        # Configuración de estilo
        self.master.configure(bg="#f0f0f0")  # Color de fondo
        self.margin = 20  # Márgenes alrededor de los elementos

        # Elementos de entrada
        self.label_mail = Label(master, text="Correo Electrónico:", bg="#f0f0f0", fg="#000000")
        self.label_mail.pack(pady=(self.margin, 0))

        self.entry_mail_var = StringVar()  # Variable asociada al campo de entrada
        self.entry_mail = Entry(master, bg="#f0f0f0", fg="#000000", textvariable=self.entry_mail_var)  # Color de fondo blanco
        self.entry_mail.pack(pady=(0, self.margin))

        self.label_contrasenia = Label(master, text="Contraseña:", bg="#f0f0f0", fg="#000000")
        self.label_contrasenia.pack(pady=(self.margin, 0))

        self.entry_contrasenia = Entry(master, show="*", bg="#f0f0f0", fg="#000000")
        self.entry_contrasenia.pack(pady=(0, self.margin))

        self.label_hora = Label(master, text="Hora:", bg="#f0f0f0", fg="#000000")
        self.label_hora.pack(pady=(self.margin, 0))

        self.combobox_hora = ttk.Combobox(master, values=list(range(24)), style='TCombobox')
        self.combobox_hora.set("12")
        self.combobox_hora.pack(pady=(0, 10))

        self.label_minuto = Label(master, text="Minuto:", bg="#f0f0f0", fg="#000000")
        self.label_minuto.pack(pady=(10, 0))

        self.combobox_minuto = ttk.Combobox(master, values=list(range(60)), style='TCombobox')
        self.combobox_minuto.set("0")
        self.combobox_minuto.pack(pady=(0, 10))

        # Botón de inicio
        self.boton_iniciar = Button(master, text="Iniciar Automatización", command=self.validar_campos, bg="#f0f0f0", fg="#000000")
        self.boton_iniciar.pack(pady=(self.margin, 0))

        # Configuración de márgenes laterales
        self.master.geometry(f"+{self.margin}+{self.margin}")
        
        # Configuración de rutas
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.configuracion = {
            'chromedriver_directory': 'chromedriver_directory',
            'url': 'https://prenotami.esteri.it/',
            'timeout': 30  # Ajusta el tiempo de espera según sea necesario
        }

        # Agregar una entrada en la configuración para almacenar la ruta al chromedriver específico
        # para el sistema operativo actual
        self.configuracion['chromedriver_path'] = self.obtener_chromedriver_path()

        
    def obtener_chromedriver_path(self):
        sistema_operativo = platform.system().lower()

        # Seleccionar la ruta al chromedriver según el sistema operativo
        if sistema_operativo == 'windows':
            return os.path.join(self.configuracion['chromedriver_directory'], 'chromedriver_win')
        elif sistema_operativo == 'darwin':
            return os.path.join(self.configuracion['chromedriver_directory'], 'chromedriver_mac')
        else:
            # Por defecto, asumir que es Linux (puedes ajustar esto según sea necesario)
            return os.path.join(self.configuracion['chromedriver_directory'], 'chromedriver_linux')

    def inicializar_navegador(self):
        os.environ['PATH'] = f"{os.environ['PATH']}:{self.configuracion['chromedriver_directory']}"
        return webdriver.Chrome()

    def login(self, driver):
        mail = self.entry_mail.get()
        contrasenia = self.entry_contrasenia.get()
        timeout = self.configuracion['timeout']
        

        # Esperar a que la página se cargue completamente
        #WebDriverWait(driver, timeout).until(EC.execute_script("return document.readyState == 'complete'"))       

        timeout = self.configuracion['timeout']
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, 'login-email')))
        
        campo_nombre = driver.find_element(By.ID, 'login-email')
        campo_apellido = driver.find_element(By.ID, 'login-password')

        campo_nombre.send_keys(mail)
        campo_apellido.send_keys(contrasenia)

        try:
            parent_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, 'login-form'))
            )

            element = WebDriverWait(parent_element, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'button.primary.g-recaptcha'))
            )

            element.click()
            print(f"Login completado")
        except Exception as e:
            print(f"No se pudo hacer clic en el elemento. Error: {str(e)}")

    def esperar_hora_para_prenota(self, driver):
        
        hora = self.combobox_hora.get()
        minuto = self.combobox_minuto.get()
        
        WebDriverWait(driver, self.configuracion['timeout']).until(
            EC.presence_of_element_located((By.ID, 'dataTableServices'))
        )

        enlace = WebDriverWait(driver, self.configuracion['timeout']).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="/Services/Booking/3440"]'))
        )

        boton_prenota = enlace.find_element(By.TAG_NAME, 'button')
        print(f"Botón de prenota encontrado, esperando a las {hora}:{minuto} para proseguir")

        while True:
            now = datetime.now()
            if now.hour == hora and now.minute == minuto:
                break
            time.sleep(15)  # Esperar 15 segundos antes de verificar nuevamente

        boton_prenota.click()
        print(f"Hora de ejecución registrada: {now.hour:02d}:{now.minute:02d}:{now.second:02d}")
        print(f"Botón de prenota seleccionado")

    def conseguir_turno(self, driver):
        self.login(driver)
        element = WebDriverWait(driver, self.configuracion['timeout']).until(
            EC.presence_of_element_located((By.ID, 'advanced'))
        )
        element.click()
        self.esperar_hora_para_prenota(driver)
        print(f"Proceso finalizado")
        
    def validar_campos(self):
        mail = self.entry_mail.get()
        contrasenia = self.entry_contrasenia.get()

        if not mail or not contrasenia:
            messagebox.showwarning("Error", "Por favor, complete ambos campos.")
        else:
            self.iniciar_automatizacion()


    def iniciar_automatizacion(self):

        driver = self.inicializar_navegador()

        print(f"Cargando URL: {self.configuracion['url']}")
        driver.get(self.configuracion['url'])

      
        self.conseguir_turno(driver)
        driver.quit()

if __name__ == "__main__":
    root = Tk()
    app = Aplicacion(root)
    root.mainloop()
