import csv
import os
import random
import time
from datetime import datetime
from urllib.parse import quote

from contactos import CONTACTOS
from selenium import webdriver
from selenium.common.exceptions import (
    NoAlertPresentException,
    StaleElementReferenceException,
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

# Segundos que la página debe permanecer sin recargarse antes de escribir/enviar
ESTABILIDAD_SEGUNDOS = 3

ARCHIVO_LOG = "log_envios.csv"
CARPETA_PERFIL = os.path.join(os.getcwd(), "whatsapp_profile")

# ----------------------------------------------------------------------
# MENSAJES  ({nombre} y {enlace} se reemplazan por los del contacto)
# En WhatsApp la negrita se escribe con UN solo asterisco: *texto*
# ----------------------------------------------------------------------
MENSAJES = [

    # --- Mensaje 1 ---

    (
        "¡Hola, {nombre}! 👋✨\n"
        "\n"
        "Es un gusto saludarte. En el marco de la celebración de nuestro LXIX Aniversario "
        "Institucional y en homenaje al Señor de los Milagros 🙏🎉, la Gerencia Regional de "
        "Salud Cusco y la Dirección Ejecutiva de Inteligencia Sanitaria tienen el agrado de "
        "invitarte a ser parte de esta celebración.\n"
        "\n"
        "🎊 Hemos preparado una jornada especial con actividades, música, reconocimientos "
        "y momentos de confraternidad.\n"
        "\n"
        "🔗 *Guarda este enlace:* {enlace}\n"
        "Aquí podrás consultar tu invitación oficial y el programa completo.\n"
        "\n"
        "¡Esperamos contar con tu grata presencia! 🥂🎉"
    ),

    # --- Mensaje 2 ---

    (
        "¡Hola, {nombre}! 🌟😊\n"
        "\n"
        "Queremos compartir contigo una invitación muy especial con motivo de nuestro "
        "LXIX Aniversario Institucional y el homenaje al Señor de los Milagros 🙏✨.\n"
        "\n"
        "La Gerencia Regional de Salud Cusco y la Dirección Ejecutiva de Inteligencia "
        "Sanitaria te invitan cordialmente a acompañarnos en esta celebración. 🎉\n"
        "\n"
        "📲 *Importante: guarda tu enlace de invitación:* {enlace}\n"
        "Desde allí podrás revisar tu invitación y conocer el programa de actividades.\n"
        "\n"
        "¡Será un gusto celebrar este día contigo! 🎊🥂"
    ),

    # --- Mensaje 3 ---

    (
        "¡Hola, {nombre}! 👋🎉\n"
        "\n"
        "¡Estamos de aniversario! 🎊 La Gerencia Regional de Salud Cusco y la Dirección "
        "Ejecutiva de Inteligencia Sanitaria desean contar contigo en las actividades por "
        "nuestro LXIX Aniversario Institucional, junto con el homenaje al Señor de los "
        "Milagros. 🙏\n"
        "\n"
        "🎶 Disfrutaremos de música, reconocimientos, premiaciones 🏆 y un agradable "
        "momento de confraternidad.\n"
        "\n"
        "🔗 *Guarda tu enlace personal:* {enlace}\n"
        "En él encontrarás tu invitación oficial y el programa completo.\n"
        "\n"
        "¡Contamos contigo para celebrar juntos! 🥂✨"
    ),

    # --- Mensaje 4 ---

    (
        "¡Hola, {nombre}! ✨👋\n"
        "\n"
        "Con mucha alegría queremos invitarte a ser parte de las actividades conmemorativas "
        "por el *LXIX Aniversario Institucional de la Gerencia Regional de Salud Cusco* "
        "y el homenaje al Señor de los Milagros. 🙏🎉\n"
        "\n"
        "Será una ocasión especial para compartir, disfrutar de nuestro programa musical 🎶, "
        "participar de las premiaciones 🏆 y reconocer a nuestros compañeros.\n"
        "\n"
        "👉 *Guarda este enlace para acceder a tu invitación:* {enlace}\n"
        "Allí encontrarás todos los detalles del programa.\n"
        "\n"
        "¡Nos encantará contar con tu presencia! 🎊"
    ),

    # --- Mensaje 5 ---

    (
        "¡Hola, {nombre}! 😊🎊\n"
        "\n"
        "La Gerencia Regional de Salud Cusco y la Dirección Ejecutiva de Inteligencia "
        "Sanitaria tienen el agrado de hacerte llegar tu invitación por nuestro "
        "*LXIX Aniversario Institucional*, en homenaje al Señor de los Milagros. 🙏✨\n"
        "\n"
        "Hemos preparado una celebración para compartir juntos un momento de confraternidad, "
        "música 🎵, premios 🏆 y reconocimientos especiales.\n"
        "\n"
        "🔗 *Guarda tu enlace de invitación:* {enlace}\n"
        "Podrás ingresar nuevamente cuando quieras para revisar el programa completo.\n"
        "\n"
        "¡Te esperamos para celebrar juntos este aniversario! 🎉🥂"
    ),

    # --- Mensaje 6 ---

    (
        "¡Hola, {nombre}! 👋🌟\n"
        "\n"
        "Tenemos el gusto de invitarte a participar de la celebración por nuestro "
        "*LXIX Aniversario Institucional* y del homenaje al Señor de los Milagros. "
        "🙏🎉\n"
        "\n"
        "Será un momento especial para reencontrarnos, compartir en confraternidad y "
        "disfrutar de las actividades preparadas para esta fecha. 🎶🏆🎊\n"
        "\n"
        "📌 *No olvides guardar este enlace:* {enlace}\n"
        "Es tu acceso a la invitación oficial y al programa completo.\n"
        "\n"
        "¡Esperamos verte y celebrar juntos! 🥂✨"
    ),

    # --- Mensaje 7 ---

    (
        "¡Hola, {nombre}! 🙌✨\n"
        "\n"
        "Queremos hacerte llegar una cordial invitación para celebrar juntos el "
        "*LXIX Aniversario Institucional de la Gerencia Regional de Salud Cusco*, "
        "acompañando también el homenaje al Señor de los Milagros. 🙏🎉\n"
        "\n"
        "🎶 Tendremos una jornada especial con música, premiaciones 🏆, reconocimientos "
        "y un espacio para compartir entre compañeros.\n"
        "\n"
        "🔗 *Guarda este enlace, será importante para ti:* {enlace}\n"
        "Desde allí podrás consultar tu invitación y revisar el programa completo.\n"
        "\n"
        "¡Será un placer contar con tu presencia! 🎊🥂"
    ),

]

# ----------------------------------------------------------------------
# SELECTORES (WhatsApp Web los cambia seguido; si algo falla, revisa aquí)
# ----------------------------------------------------------------------
XPATH_CHATS = '//div[@id="pane-side"]'
XPATH_CAJA_MENSAJE = '//footer//div[@contenteditable="true"]'
XPATH_POPUP = '//div[@data-animate-modal-popup="true"]'
XPATH_BOTON_ENVIAR = (
    '//footer//button[@aria-label="Enviar" or @aria-label="Send"]'
    ' | //footer//span[contains(@data-icon,"send")]'
)
# Reloj de "pendiente" solo del ÚLTIMO mensaje enviado
XPATH_PENDIENTE = (
    '(//div[contains(@class,"message-out")])[last()]'
    '//span[contains(@data-icon,"msg-time")]'
)

# Fragmentos (en minúscula) del popup de WhatsApp cuando el número no es válido
TEXTOS_INVALIDO = (
    "no es válido",
    "no es valido",
    "no está en whatsapp",
    "no esta en whatsapp",
    "no está registrado",
    "invalid",
    "not on whatsapp",
    "isn't on whatsapp",
)

# Detalle devuelto cuando el número no tiene WhatsApp (no se reintenta)
DETALLE_INVALIDO = "Número inválido o sin WhatsApp."


# ----------------------------------------------------------------------
# UTILIDADES
# ----------------------------------------------------------------------
def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def limpiar_telefono(tel):
    solo_digitos = "".join(c for c in str(tel) if c.isdigit())
    if len(solo_digitos) == 9:
        solo_digitos = CODIGO_PAIS + solo_digitos
    return solo_digitos


def telefono_valido(tel):
    return tel.isdigit() and 10 <= len(tel) <= 15


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


def formatear_nombre(nombre):
    """Cada palabra con inicial mayúscula y el resto en minúscula."""
    return " ".join(p.capitalize() for p in str(nombre).split())


# ----------------------------------------------------------------------
# NAVEGADOR
# ----------------------------------------------------------------------
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
    # Evita el diálogo "¿Salir del sitio?" cuando queda un borrador escrito
    try:
        driver.execute_script("window.onbeforeunload = null;")
    except Exception:
        pass
    try:
        driver.get(url)
    except UnexpectedAlertPresentException:
        try:
            driver.switch_to.alert.accept()
        except NoAlertPresentException:
            pass
        driver.get(url)


def esperar_pagina_estable(driver, segundos=ESTABILIDAD_SEGUNDOS, maximo=60):
    """
    Espera la caja de texto (o el popup de error) y comprueba que la página
    NO se recargue durante `segundos`. Devuelve "caja", "popup" o None.

    Se usa una marca en window: si la página se recarga, la marca desaparece
    y se vuelve a esperar. Así no se envía justo antes de una recarga.
    """
    fin = time.time() + maximo
    while time.time() < fin:
        try:
            # 1) La caja de texto tiene prioridad: si existe, el chat cargó bien
            if driver.find_elements(By.XPATH, XPATH_CAJA_MENSAJE):
                driver.execute_script("window.__bot_marca = true;")
                time.sleep(segundos)
                sigue = driver.execute_script("return window.__bot_marca === true;")
                if sigue and driver.find_elements(By.XPATH, XPATH_CAJA_MENSAJE):
                    return "caja"
                # La marca desapareció: la página se recargó, se vuelve a esperar
                continue

            # 2) Un popup solo cuenta como error si su texto indica número inválido.
            #    Otros popups (p. ej. "Iniciando chat...") se ignoran y se sigue esperando.
            for popup in driver.find_elements(By.XPATH, XPATH_POPUP):
                texto_popup = popup.text.lower()
                if any(k in texto_popup for k in TEXTOS_INVALIDO):
                    return "popup"
        except Exception:
            pass
        time.sleep(0.5)
    return None


# ----------------------------------------------------------------------
# ENVÍO
# ----------------------------------------------------------------------
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
                time.sleep(1)
                continue
            if intento == 1:
                caja.click()
                caja.send_keys(Keys.ENTER)
            else:
                botones = driver.find_elements(By.XPATH, XPATH_BOTON_ENVIAR)
                if botones:
                    driver.execute_script("arguments[0].click();", botones[0])
                else:
                    caja.send_keys(Keys.ENTER)
        except StaleElementReferenceException:
            time.sleep(1)
            continue
        except Exception:
            pass

        fin = time.time() + 5
        while time.time() < fin:
            if texto_en_caja(driver) == "":
                return True
            time.sleep(0.3)
    return False


def esperar_confirmacion(driver, maximo=12):
    """Espera a que el último mensaje deje de estar 'pendiente' (reloj) antes de cambiar de chat."""
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

    # Esperar caja de texto estable (sin recargas) o aviso de error
    resultado = esperar_pagina_estable(driver)
    if resultado is None:
        return False, "Tiempo agotado: el chat no cargó (¿sin internet?)."
    if resultado == "popup":
        return False, DETALLE_INVALIDO

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

            if not telefono_valido(telefono):
                fallidos += 1
                print(f"[{i}/{len(pendientes)}] ❌ Teléfono con formato inválido: {nombre} ({telefono})")
                escribir_log(nombre, telefono, "FALLIDO", "Teléfono con formato inválido.")
                continue

            ultimo_indice = elegir_mensaje(ultimo_indice)
            texto = MENSAJES[ultimo_indice].format(nombre=nombre, enlace=c["enlace"])

            print(f"[{i}/{len(pendientes)}] Enviando a {nombre} (+{telefono}) con mensaje #{ultimo_indice + 1}...")
            ok, detalle = False, ""
            for intento in range(1, MAX_INTENTOS + 1):
                try:
                    ok, detalle = enviar_mensaje(driver, telefono, texto)
                except Exception as e:
                    ok, detalle = False, f"Error inesperado: {type(e).__name__}: {e}"
                if ok or detalle == DETALLE_INVALIDO:
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