import cv2
import qrcode
import sqlite3
from twilio.rest import Client


# Configuración de Twilio
account_sid = 'ACac7ba3db02f67876ba32e0aa0fe329ae'
auth_token = '0122aa64d39a64a184c2a1b3f2c381e2'
twilio_client = Client(account_sid, auth_token)
twilio_phone_number = 'whatsapp:+14155238886'

# Conectar  la base de datos 
conn = sqlite3.connect('mi_base_de_datos.db')
cursor = conn.cursor()

# Crear la tabla "alumnos" si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS alumnos (
                nombre TEXT,
                telefono TEXT,
                cuenta TEXT,
                qr_code TEXT)''')
# Funcion para Enviar MSJ De Whatsapp
def send_whatsapp_message(to, message):
    twilio_client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to='whatsapp:+5215513049734'

    )

while True:
    # Solicitar datos del alumno desde la consola
    nombre_alumno = input("Nombre del alumno (o 'q' para salir): ")
    if nombre_alumno.lower() == 'q':
        break  # Salir del bucle si el usuario ingresa 'q'

    telefono = input("Teléfono del alumno: ")
    numero_cuenta = input("Número de cuenta del alumno: ")

    # Crear el contenido del QR
    contenido_qr = f"Nombre: {nombre_alumno}\nTeléfono: {telefono}\nCuenta: {numero_cuenta}"

    # Generar el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(contenido_qr)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Guardar la imagen del código QR en un archivo
    qr_filename = f"{nombre_alumno}_qr.png"
    img.save(qr_filename)

    # Insertar los datos en la base de datos
    cursor.execute("INSERT INTO alumnos (nombre, telefono, cuenta, qr_code) VALUES (?, ?, ?, ?)",
                   (nombre_alumno, telefono, numero_cuenta, qr_filename))
    conn.commit()

    # Escanear el código QR
    print("Escanea el código QR para confirmar el registro.")
    camera = cv2.VideoCapture(0)  # Abre la cámara
    while True:
        ret, frame = camera.read()
        if ret:
            detector = cv2.QRCodeDetector()
            decoded_info, _, _ = detector.detectAndDecode(frame)
            if decoded_info:
                # Compara el contenido del código QR con el contenido del alumno
                if contenido_qr == decoded_info:
                    print("Registro confirmado.")
                    send_whatsapp_message(twilio_phone_number, f"¡El alumno {nombre_alumno} se ha registrado!")
                    break
                else:
                    print("Código QR no coincide con el registro.")
            cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) == 27:  # Salir con la tecla Esc
            break
    camera.release()
    cv2.destroyAllWindows()
    

conn.close()
