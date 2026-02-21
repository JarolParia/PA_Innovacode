from datetime import datetime

RUTA_ARCHIVO = "historial.txt"

def guardar_operacion(tipo_operacion, resultado):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(RUTA_ARCHIVO, "a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha} | {tipo_operacion}\n")
        archivo.write("Resultado:\n")
        archivo.write(str(resultado))  # FORZAMOS STR
        archivo.write("\n" + "-" * 50 + "\n")