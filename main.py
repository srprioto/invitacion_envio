"""
Envío de invitaciones por WhatsApp Web (Selenium) - Windows + Chrome

Instalación (una sola vez):
    pip install selenium

Uso:
    python enviar_whatsapp.py

La primera vez se abre Chrome y debes escanear el QR de WhatsApp Web.
La sesión queda guardada en la carpeta "whatsapp_profile", así que las
siguientes veces no necesitarás volver a escanear.
"""

import csv
import os
import random
import time
from datetime import datetime
from urllib.parse import quote

from selenium import webdriver
from selenium.common.exceptions import (
    NoAlertPresentException,
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

# ----------------------------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------------------------
CODIGO_PAIS = "51"

# Pausa aleatoria entre mensajes (segundos)
PAUSA_MIN = 2
PAUSA_MAX = 5

# Cada N mensajes se hace una pausa más larga (opcional, se pregunta al iniciar)
LOTE_TAMANO = 10
PAUSA_LOTE_MIN = 20
PAUSA_LOTE_MAX = 25

# Intentos por contacto si el envío falla (no aplica a números inválidos)
MAX_INTENTOS = 2

ARCHIVO_LOG = "log_envios.csv"
CARPETA_PERFIL = os.path.join(os.getcwd(), "whatsapp_profile")

# ----------------------------------------------------------------------
# CONTACTOS (pega aquí el resto de tus contactos)
# ----------------------------------------------------------------------
CONTACTOS = [
    {"nombre": "Renato Renzo Luna Herrera", "telefono": "984741614", "enlace": "https://invitacion-aniv.onrender.com/666ooo"},
    {"nombre": "JAIME JUCULACA CHURA", "telefono": "921570164", "enlace": "https://invitacion-aniv.onrender.com/04WYd3"},
    {"nombre": "JUAN ALBERTO HUARACHI PUMACHAPI", "telefono": "973784192", "enlace": "https://invitacion-aniv.onrender.com/0QdpMq"},
    {"nombre": "JOSE SANTOS MAMANI CCANAHUIRE", "telefono": "944133665", "enlace": "https://invitacion-aniv.onrender.com/0emiL7"},
    {"nombre": "GUINETTA YABAR HERRERA", "telefono": "973619361", "enlace": "https://invitacion-aniv.onrender.com/0izwRm"},
    {"nombre": "LUZ MARLENY MEZA PUMAHUILLCA", "telefono": "935796328", "enlace": "https://invitacion-aniv.onrender.com/0uLjHV"},
    {"nombre": "MARIA DEL CARMEN ANAYA JUCHARO", "telefono": "989411721", "enlace": "https://invitacion-aniv.onrender.com/0w2aRh"},
    {"nombre": "GUINETTA YABAR HERRERA", "telefono": "973619361", "enlace": "https://invitacion-aniv.onrender.com/0zCpm4"},  # duplicado: se omite
    {"nombre": "Alex Jaramillo Corrales", "telefono": "984747201", "enlace": "https://invitacion-aniv.onrender.com/14SLTB"},
    {"nombre": "Mavel Sarmiento Huanca", "telefono": "984055039", "enlace": "https://invitacion-aniv.onrender.com/1CSLC9"},
    {"nombre": "Danny Robert Moscoso Sanchez", "telefono": "974310648", "enlace": "https://invitacion-aniv.onrender.com/f82h4d"},
    {"nombre": "Abel Rimasca Chacon", "telefono": "984895486", "enlace": "https://invitacion-aniv.onrender.com/1EMxKP"},
    {"nombre": "Santiago Quispe Peralta", "telefono": "984851604", "enlace": "https://invitacion-aniv.onrender.com/1bM79c"},
    {"nombre": "Karla Zavala Vargas", "telefono": "992428989", "enlace": "https://invitacion-aniv.onrender.com/1hRfUX"},
]

# ----------------------------------------------------------------------
# MENSAJES  ({nombre} y {enlace} se reemplazan por los del contacto)
# ----------------------------------------------------------------------
MENSAJES = [
    # --- Mensaje 1 ---
    (
        "¡Hola, {nombre}! 👋✨\n"
        "\n"
        "Es un gusto saludarte. En el marco de la celebración de nuestro LXIX Aniversario "
        "Institucional y en homenaje al Señor de los Milagros 🙏🎉, la Gerencia Regional de "
        "Salud Cusco y la Dirección Ejecutiva de Inteligencia Sanitaria tienen el honor de "
        "invitarte cordialmente a acompañarnos en nuestras actividades conmemorativas.\n"
        "\n"
        "📅 Día Central: Miércoles, 7 de octubre\n"
        "📍 Lugar del Almuerzo de Confraternidad: Centro de Convenciones \"Crystal Palace\" "
        "(Av. Tomasa Ttito Condemayta N° 1875)\n"
        "⏰ Hora: 13:30 hrs\n"
        "\n"
        "Será una excelente oportunidad para compartir un momento ameno de confraternidad, "
        "disfrutar de nuestro programa musical 🎶, la entrega de premios 🏆 y rendir un "
        "especial reconocimiento a nuestros compañeros.\n"
        "\n"
        "Puedes revisar el programa completo y tu invitación oficial en el siguiente enlace:\n"
        "👉 {enlace}\n"
        "\n"
        "¡Contamos con tu grata presencia para celebrar juntos este aniversario! 🥂🎊\n"
        "\n"
        "Atentamente,\n"
        "Gerencia Regional de Salud Cusco"
    ),
    # --- Mensaje 2 ---
    (
        "¡Hola, {nombre}! 🌟✨\n"
        "\n"
        "Esperamos que te encuentres muy bien. Nos complace invitarte formalmente a las "
        "actividades por nuestro LXIX Aniversario Institucional y el homenaje al Señor de los "
        "Milagros 🙏, organizados por la Gerencia Regional de Salud Cusco y la Dirección "
        "Ejecutiva de Inteligencia Sanitaria.\n"
        "\n"
        "Te esperamos en el Día Central:\n"
        "📅 Fecha: Miércoles, 7 de octubre\n"
        "📍 Almuerzo de Confraternidad: Centro de Convenciones \"Crystal Palace\" "
        "(Av. Tomasa Ttito Condemayta N° 1875)\n"
        "⏰ Hora: 13:30 hrs\n"
        "\n"
        "Acompáñanos a disfrutar de nuestra ceremonia, momentos musicales 🎶, premiaciones 🏆 "
        "y el merecido reconocimiento a la trayectoria de nuestro personal.\n"
        "\n"
        "📲 Revisa tu tarjeta de invitación y el programa detallado aquí:\n"
        "👉 {enlace}\n"
        "\n"
        "¡Será un honor contar con tu presencia en este gran día! 🥂🎉"
    ),
    # --- Mensaje 3 ---
    (
        "¡Hola, {nombre}! 👋🎉\n"
        "\n"
        "¡Llegó el momento de celebrar juntos! La Gerencia Regional de Salud Cusco y la "
        "Dirección Ejecutiva de Inteligencia Sanitaria te invitan cordialmente a unirte a las "
        "celebraciones por nuestro LXIX Aniversario Institucional y el tributo al Señor de los "
        "Milagros 🙏✨.\n"
        "\n"
        "Apunta los datos de nuestro Día Central:\n"
        "🗓 Fecha: 7 de octubre\n"
        "📍 Lugar: Centro de Convenciones \"Crystal Palace\" (Av. Tomasa Ttito Condemayta N° 1875)\n"
        "🕐 Almuerzo de Confraternidad: 13:30 hrs\n"
        "\n"
        "Hemos preparado una jornada muy especial con música en vivo 🎵, ceremonia de "
        "reconocimientos y la entrega de premios de nuestras actividades institucionales 🏆🎊.\n"
        "\n"
        "Accede a todos los detalles de la invitación desde este enlace:\n"
        "👉 {enlace}\n"
        "\n"
        "¡Tu asistencia le dará un realce especial a nuestra fiesta! 🍾🥳"
    ),
    # --- Mensaje 4 ---
    (
        "Estimada {nombre}, recibes un cordial saludo 👋.\n"
        "\n"
        "En el marco de la conmemoración de nuestro LXIX Aniversario Institucional y rindiendo "
        "homenaje al Señor de los Milagros 🙏, la Gerencia Regional de Salud Cusco junto a la "
        "Dirección Ejecutiva de Inteligencia Sanitaria se complacen en invitarte a compartir "
        "con nosotros esta importante fecha.\n"
        "\n"
        "📌 Coordenadas del Día Central:\n"
        "📅 Fecha: 7 de octubre\n"
        "📍 Almuerzo de Confraternidad: Centro de Convenciones \"Crystal Palace\" "
        "(Av. Tomasa Ttito Condemayta N° 1875)\n"
        "⏰ Hora: 13:30 hrs\n"
        "\n"
        "Ven a compartir un grato momento junto a todo el equipo, disfrutar del show "
        "musical 🎷 y presenciar la entrega de reconocimientos y premios 🏅.\n"
        "\n"
        "Mira la tarjeta de invitación completa en el siguiente link:\n"
        "👉 {enlace}\n"
        "\n"
        "¡Agradecemos de antemano tu gentil asistencia! 🥂✨"
    ),
    # --- Mensaje 5 ---
    (
        "¡Hola, {nombre}! ✨👋\n"
        "\n"
        "¡Queremos invitarte a celebrar con nosotros! La Gerencia Regional de Salud Cusco y la "
        "Dirección Ejecutiva de Inteligencia Sanitaria tienen el agrado de convocar a tu "
        "presencia en las actividades de nuestro LXIX Aniversario Institucional y homenaje al "
        "Señor de los Milagros 🙏🎊.\n"
        "\n"
        "Te esperamos en nuestro Día Central:\n"
        "📅 Fecha: 7 de octubre\n"
        "⏰ Hora: 13:30 hrs (Almuerzo de Confraternidad)\n"
        "📍 Ubicación: Centro de Convenciones \"Crystal Palace\" (Av. Tomasa Ttito Condemayta N° 1875)\n"
        "\n"
        "Contaremos con ambientación musical 🎶, entrega de premios deportivos y culturales 🏆, "
        "y homenajes a nuestros colaboradores.\n"
        "\n"
        "Puedes visualizar el programa oficial ingresando aquí:\n"
        "👉 {enlace}\n"
        "\n"
        "¡Esperamos poder celebrar este aniversario juntos! 🎉🥂"
    ),
    # --- Mensaje 6 ---
    (
        "¡Estimada {nombre}! 👋🏼🥳\n"
        "\n"
        "Es motivo de gran alegría ponernos en contacto contigo. Queremos invitarte a ser parte "
        "de los festejos por el LXIX Aniversario Institucional de la Gerencia Regional de Salud "
        "Cusco y la Dirección Ejecutiva de Inteligencia Sanitaria, así como del homenaje al "
        "Señor de los Milagros 🙏✨.\n"
        "\n"
        "Unámonos en este día especial:\n"
        "📅 Fecha Central: 7 de octubre\n"
        "📍 Reunión/Almuerzo: Centro de Convenciones \"Crystal Palace\" "
        "(Av. Tomasa Ttito Condemayta N° 1875)\n"
        "🕐 Hora: 13:30 hrs\n"
        "\n"
        "Será una reunión inolvidable donde compartiremos buena música 🎵, premiación a los "
        "equipos ganadores 🥇 y la distinción a nuestros compañeros distinguidos.\n"
        "\n"
        "Consulta la invitación digital en este enlace:\n"
        "👉 {enlace}\n"
        "\n"
        "¡Contamos con tu compañía para hacer de este aniversario un evento memorable! 🥂🎊"
    ),
]

# ----------------------------------------------------------------------
# UTILIDADES
# ----------------------------------------------------------------------
XPATH_CHATS = '//div[@id="pane-side"]'
XPATH_CAJA_MENSAJE = '//footer//div[@contenteditable="true"]'
XPATH_POPUP = '//div[@data-animate-modal-popup="true"]'


def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def limpiar_telefono(tel):
    solo_digitos = "".join(c for c in str(tel) if c.isdigit())
    if len(solo_digitos) == 9:
        solo_digitos = CODIGO_PAIS + solo_digitos
    return solo_digitos


def quitar_duplicados(contactos):
    vistos, unicos = set(), []
    for c in contactos:
        tel = limpiar_telefono(c["telefono"])
        if tel in vistos:
            print(f"[OMITIDO] Duplicado: {c['nombre']} ({tel})")
            continue
        vistos.add(tel)
        unicos.append(c)
    return unicos


def cargar_ya_enviados():
    """Lee el log para no volver a escribirle a quien ya recibió el mensaje."""
    enviados = set()
    if os.path.exists(ARCHIVO_LOG):
        with open(ARCHIVO_LOG, newline="", encoding="utf-8-sig") as f:
            for fila in csv.DictReader(f):
                if fila.get("estado") == "ENVIADO":
                    enviados.add(fila["telefono"])
    return enviados


def preguntar_pausas_lote():
    """Pregunta al usuario si quiere pausas largas cada LOTE_TAMANO mensajes."""
    print("=" * 50)
    print(f"¿Quieres hacer una pausa larga cada {LOTE_TAMANO} mensajes?")
    print(f"  (pausa de {PAUSA_LOTE_MIN} a {PAUSA_LOTE_MAX} segundos, reduce el riesgo de bloqueo)")
    print("  S = Sí, hacer pausas")
    print("  N = No, continuar sin pausas largas (bajo tu propio riesgo)")
    print("=" * 50)
    while True:
        r = input("Tu respuesta (S/N): ").strip().lower()
        if r in ("s", "si", "sí"):
            print("-> Se harán pausas largas por lote.\n")
            return True
        if r in ("n", "no"):
            print("-> Se continuará sin pausas largas. Solo habrá la pausa corta entre mensajes.\n")
            return False
        print("Responde con S o N.")


def escribir_log(nombre, telefono, estado, detalle=""):
    nuevo = not os.path.exists(ARCHIVO_LOG)
    with open(ARCHIVO_LOG, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fecha", "nombre", "telefono", "estado", "detalle"])
        w.writerow([ahora(), nombre, telefono, estado, detalle])


def elegir_mensaje(ultimo_indice):
    """Elige un mensaje al azar, evitando repetir el anterior."""
    opciones = [i for i in range(len(MENSAJES)) if i != ultimo_indice]
    return random.choice(opciones) if opciones else 0


def iniciar_navegador():
    opciones = webdriver.ChromeOptions()
    opciones.add_argument(f"--user-data-dir={CARPETA_PERFIL}")
    opciones.add_argument("--start-maximized")
    opciones.add_argument("--disable-notifications")
    opciones.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=opciones)  # Selenium Manager descarga el driver solo


def esperar_login(driver):
    driver.get("https://web.whatsapp.com")
    print("Abriendo WhatsApp Web... si aparece el QR, escanéalo con tu celular.")
    try:
        WebDriverWait(driver, 180).until(
            lambda d: d.find_elements(By.XPATH, XPATH_CHATS)
        )
    except TimeoutException:
        raise SystemExit("No se detectó la sesión de WhatsApp en 3 minutos. Intenta de nuevo.")
    print("Sesión iniciada correctamente.\n")
    time.sleep(3)


def abrir_chat(driver, url):
    try:
        driver.get(url)
    except UnexpectedAlertPresentException:
        try:
            driver.switch_to.alert.accept()
        except NoAlertPresentException:
            pass
        driver.get(url)


XPATH_BOTON_ENVIAR = '//footer//span[@data-icon="send"]'
XPATH_PENDIENTE = '//span[@data-icon="msg-time"]'


def obtener_caja(driver):
    cajas = driver.find_elements(By.XPATH, XPATH_CAJA_MENSAJE)
    return cajas[0] if cajas else None


def texto_en_caja(driver):
    """Texto actual de la caja de mensaje. None si no se pudo leer."""
    try:
        caja = obtener_caja(driver)
        return None if caja is None else caja.text.strip()
    except Exception:
        return None


def limpiar_borrador(driver):
    """Borra lo que haya quedado escrito para no dejar borradores."""
    try:
        caja = obtener_caja(driver)
        if caja:
            caja.send_keys(Keys.CONTROL, "a")
            caja.send_keys(Keys.DELETE)
    except Exception:
        pass


def intentar_enviar(driver):
    """
    Intenta enviar lo escrito: 1) tecla Enter, 2) y 3) clic en el botón de enviar.
    Después de cada intento verifica que la caja haya quedado vacía.
    """
    for intento in range(1, 4):
        try:
            caja = obtener_caja(driver)
            if caja is None:
                break
            if intento == 1:
                caja.send_keys(Keys.ENTER)
            else:
                botones = driver.find_elements(By.XPATH, XPATH_BOTON_ENVIAR)
                if botones:
                    driver.execute_script("arguments[0].click();", botones[0])
                else:
                    caja.send_keys(Keys.ENTER)
        except Exception:
            pass

        fin = time.time() + 5
        while time.time() < fin:
            if texto_en_caja(driver) == "":
                return True
            time.sleep(0.3)
    return False


def esperar_confirmacion(driver, maximo=12):
    """Espera a que el mensaje deje de estar 'pendiente' (reloj) antes de cambiar de chat."""
    time.sleep(1)
    fin = time.time() + maximo
    while time.time() < fin:
        if not driver.find_elements(By.XPATH, XPATH_PENDIENTE):
            return True
        time.sleep(0.4)
    return False


def enviar_mensaje(driver, telefono, texto):
    """Devuelve (ok: bool, detalle: str)."""
    url = f"https://web.whatsapp.com/send?phone={telefono}&text={quote(texto)}"
    abrir_chat(driver, url)

    # Esperar a que aparezca la caja de texto o un aviso de error
    def listo(d):
        if d.find_elements(By.XPATH, XPATH_CAJA_MENSAJE):
            return "caja"
        if d.find_elements(By.XPATH, XPATH_POPUP):
            return "popup"
        return False

    try:
        resultado = WebDriverWait(driver, 45).until(listo)
    except TimeoutException:
        return False, "Tiempo agotado: el chat no cargó (¿sin internet?)."

    if resultado == "popup":
        return False, "Número inválido o sin WhatsApp."

    # Esperar a que el texto precargado aparezca en la caja
    fin = time.time() + 10
    while time.time() < fin and not texto_en_caja(driver):
        time.sleep(0.3)
    if not texto_en_caja(driver):
        return False, "El texto del mensaje no se cargó en la caja."

    time.sleep(random.uniform(0.5, 1.2))

    if not intentar_enviar(driver):
        limpiar_borrador(driver)
        return False, "No se pudo enviar tras 3 intentos (se limpió el borrador)."

    if not esperar_confirmacion(driver):
        return True, "Enviado, pero sin confirmar entrega (revisa tu internet)."
    return True, "Mensaje enviado."


def formatear_nombre(nombre):
    """Cada palabra con inicial mayúscula y el resto en minúscula."""
    return " ".join(p.capitalize() for p in str(nombre).split())


# ----------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ----------------------------------------------------------------------
def main():
    contactos = quitar_duplicados(CONTACTOS)
    ya_enviados = cargar_ya_enviados()
    pendientes = [c for c in contactos if limpiar_telefono(c["telefono"]) not in ya_enviados]

    if len(pendientes) < len(contactos):
        print(f"[INFO] {len(contactos) - len(pendientes)} contacto(s) ya recibieron el mensaje antes y se omiten.")
    print(f"[INFO] Contactos por enviar: {len(pendientes)}\n")
    if not pendientes:
        return

    usar_pausas_lote = preguntar_pausas_lote()

    driver = iniciar_navegador()
    exitosos = fallidos = 0
    ultimo_indice = None

    try:
        esperar_login(driver)

        for i, c in enumerate(pendientes, start=1):
            nombre = formatear_nombre(c["nombre"])
            telefono = limpiar_telefono(c["telefono"])

            ultimo_indice = elegir_mensaje(ultimo_indice)
            texto = MENSAJES[ultimo_indice].format(nombre=nombre, enlace=c["enlace"])

            print(f"[{i}/{len(pendientes)}] Enviando a {nombre} (+{telefono}) con mensaje #{ultimo_indice + 1}...")
            ok, detalle = False, ""
            for intento in range(1, MAX_INTENTOS + 1):
                try:
                    ok, detalle = enviar_mensaje(driver, telefono, texto)
                except Exception as e:
                    ok, detalle = False, f"Error inesperado: {type(e).__name__}: {e}"
                if ok or "inválido" in detalle:
                    break
                if intento < MAX_INTENTOS:
                    print(f"   ↻ Falló ({detalle}) Reintentando...")
                    time.sleep(2)

            if ok:
                exitosos += 1
                print(f"   ✅ ENVIADO a {nombre}")
                if "sin confirmar" in detalle:
                    print(f"   ⚠ {detalle}")
                escribir_log(nombre, telefono, "ENVIADO", f"Mensaje #{ultimo_indice + 1} | {detalle}")
            else:
                fallidos += 1
                print(f"   ❌ FALLÓ con {nombre}: {detalle}")
                escribir_log(nombre, telefono, "FALLIDO", detalle)

            if i == len(pendientes):
                break

            # Pausas para evitar bloqueos
            if usar_pausas_lote and i % LOTE_TAMANO == 0:
                pausa = random.randint(PAUSA_LOTE_MIN, PAUSA_LOTE_MAX)
                print(f"   ⏸ Pausa larga de lote: {pausa} s\n")
            else:
                pausa = random.randint(PAUSA_MIN, PAUSA_MAX)
                print(f"   ⏳ Esperando {pausa} s...\n")
            time.sleep(pausa)

    except KeyboardInterrupt:
        print("\n[INFO] Interrumpido por el usuario. Lo ya enviado quedó registrado en el log.")
    finally:
        print("\n" + "=" * 50)
        print(f"Resumen: {exitosos} enviados, {fallidos} fallidos.")
        print(f"Detalle completo en: {ARCHIVO_LOG}")
        print("=" * 50)
        driver.quit()


if __name__ == "__main__":
    main()