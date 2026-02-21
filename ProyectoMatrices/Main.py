from Matriz import Matriz ##Importamos la clase de matriz para poder usarla en el main, no es necesario importar en matriz al main
from validaciones import mostrar_estado##Importamos la funcion de validacion para poder usarla en el main
from Utils import crear_matriz, limpiar, menu_principal, menu_unitaria, menu_binaria, pausa #importaciones de todo lo del utils

def main():

    A = None
    B = None

    while True:
        limpiar()
        menu_principal()
        opcion = input("Seleccione una opción: ").strip()

        match opcion:

#region operaciones unitarias
            # ================= UNITARIAS =================
            case "1":
                A = crear_matriz("A", A)
                if A is None:
                    print("No hay matriz A disponible.")
                    continue
                    
                operaciones_unitarias = {
                    "1": {"tipo": "escalar", "funcion": A.sumaEscalar, "nombre": "Suma escalar"},
                    "2": {"tipo": "escalar", "funcion": A.restaEscalar, "nombre": "Resta escalar"},
                    "3": {"tipo": "escalar", "funcion": A.multiplicacionEscalar, "nombre": "Multiplicación escalar"},
                    "4": {"tipo": "escalar", "funcion": A.divisionEscalar, "nombre": "División escalar"},
                    "5": {"tipo": "numero", "funcion": A.determinante, "nombre": "Determinante"},
                    "6": {"tipo": "matriz", "funcion": A.matrizAdjunta, "nombre": "Matriz adjunta"},
                    "7": {"tipo": "matriz", "funcion": A.inversa, "nombre": "Inversa"},
                    "8": {"tipo": "numero", "funcion": A.traza, "nombre": "Traza"},
                    "9": {"tipo": "matriz", "funcion": A.transpuesta, "nombre": "Transpuesta"},
                }
                    
                while True:
                    menu_unitaria()
                    opcion = input("Seleccione operación: ").strip()

                    try:
                        if opcion == "0":
                            break
                        
                        if opcion not in operaciones_unitarias:
                            print ("opción inválida")
                            continue

                        operacion = operaciones_unitarias[opcion]

                        mostrar_estado(A)

                        if operacion["tipo"] == "escalar":
                            escalar = float(input("Escalar:"))
                            matriz_resultado = operacion["funcion"](escalar)
                            print(f"\nResultado {operacion['nombre']} A y {escalar}:")
                            matriz_resultado.mostrarMatriz()
                            pausa()

                        elif operacion["tipo"] == "numero":
                            matriz_resultado = operacion["funcion"]()
                            print(f"\nResultado {operacion['nombre']} de A: {matriz_resultado}")
                            pausa()
                        
                        elif operacion["tipo"] == "matriz":
                            matriz_resultado = operacion["funcion"]()
                            print(f"\nResultado {operacion['nombre']} de A:")
                            matriz_resultado.mostrarMatriz()
                            pausa()

                    except Exception as e:
                        print("Error:", e)
                        pausa()

#endregion

#region operaciones binarias

            # ================= BINARIAS =================
            case "2":
                A = crear_matriz("A", A)
                if A is None:
                    print("\nNo hay matriz A disponible.")
                    continue

                B = crear_matriz("B", B)
                if B is None:
                    print("\nNo hay matriz B disponible.")
                    continue

                operaciones_binarias = {
                    "1": {"funcion": A.sumaMatrices, "nombre": "Suma de matrices"},
                    "2": {"funcion": A.restaMatrices, "nombre": "Resta de matrices"},
                    "3": {"funcion": A.divisionMatrices, "nombre": "Division de matrices"},
                    "4": {"funcion": A.multiplicacionMatricesHadamard, "nombre": "Multiplicacion Hadamard"},
                    "5": {"funcion": A.multiplicacionMatrices, "nombre": "producto matricial"},
                }

                while True:
                    menu_binaria()
                    opcion = input("Seleccione operación: ").strip()

                    try:
                        if opcion == "0":
                            break

                        if opcion not in operaciones_binarias:
                            print("Opcion invalida")
                            continue

                        mostrar_estado(A, B)

                        operacion = operaciones_binarias[opcion]
                        matriz_resultado = operacion["funcion"](B)
                        print(f"\nResultado {operacion['nombre']} de A y B:")
                        matriz_resultado.mostrarMatriz()
                        pausa()

                    except Exception as e:
                        print("Error:", e)
                        pausa()

            case "0":
                print("\nPrograma finalizado")
                break

            case _:
                print("\n"+"Opción inválida")
#endregion

if __name__ == "__main__": #conexion
    main()