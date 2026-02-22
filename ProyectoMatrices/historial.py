from datetime import datetime
import os

RUTA_ARCHIVO = os.path.join(os.path.dirname(__file__), "historial.txt")

def guardar_operacion(tipo_operacion, resultado, A=None, B=None):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(RUTA_ARCHIVO, "a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha} | {tipo_operacion}\n")

        if A is not None:
            archivo.write("\nMatriz A:\n")
            archivo.write(str(A) + "\n")

        if B is not None:
            archivo.write("\nMatriz B:\n")
            archivo.write(str(B) + "\n")

        archivo.write("\nResultado:\n")
        archivo.write(str(resultado))

        archivo.write("\n" + "-" * 50 + "\n")