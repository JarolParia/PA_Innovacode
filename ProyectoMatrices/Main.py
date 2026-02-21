from Matriz import Matriz ##Importamos la clase de matriz para poder usarla en el main, no es necesario importar en matriz al main
from validaciones import mostrar_estado##Importamos la funcion de validacion para poder usarla en el main
from Utils import crear_matriz, limpiar, menu_principal, menu_unitaria, menu_binaria, pausa #importaciones de todo lo del utils
from historial import guardar_operacion

def main():

    A = None
    B = None

    while True: # Bucle principal del programa
        limpiar()
        menu_principal() # Muestra el menú principal
        opcion = input("Seleccione una opción: ").strip()
    # Evaluamos la opción elegida
        match opcion:

#region operaciones unitarias
            # ================= UNITARIAS =================
            case "1":
                # Crear o actualizar matriz A
                A = crear_matriz("A", A)
                 # Si no se creó correctamente, vuelve al menú
                if A is None:
                    print("No hay matriz A disponible.")
                    continue
                    
                # Diccionario que contiene todas las operaciones unitarias
                # tipo: define qué devuelve la operación (matriz o número)
            
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
                
                 # Submenú de operaciones unitarias
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
                            # GUARDAR EN HISTORIAL
                            guardar_operacion(
                                f"{operacion['nombre']} a matriz A con escalar {escalar}",
                                matriz_resultado
                            )
                            pausa()
                         # -------OPERACIONES QUE DEVUELVEN NÚMERO ----------
                        elif operacion["tipo"] == "numero":
                            matriz_resultado = operacion["funcion"]()
                            print(f"\nResultado {operacion['nombre']} de A: {matriz_resultado}")
                             # GUARDAR EN HISTORIAL
                            guardar_operacion(
                                f"{operacion['nombre']} de matriz A",
                                matriz_resultado
                            )
                            pausa()
                        # ------- OPERACIONES QUE DEVUELVEN MATRIZ ----------
                        elif operacion["tipo"] == "matriz":
                            matriz_resultado = operacion["funcion"]()
                            print(f"\nResultado {operacion['nombre']} de A:")
                            matriz_resultado.mostrarMatriz()
                             # GUARDAR EN HISTORIAL
                            guardar_operacion(
                                f"{operacion['nombre']} de matriz A",
                                matriz_resultado
                            )                   
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
                
               # Diccionario de operaciones binarias entre A y B
                operaciones_binarias = {
                    "1": {"funcion": A.sumaMatrices, "nombre": "Suma de matrices"},
                    "2": {"funcion": A.restaMatrices, "nombre": "Resta de matrices"},
                    "3": {"funcion": A.divisionMatrices, "nombre": "Division de matrices"},
                    "4": {"funcion": A.multiplicacionMatricesHadamard, "nombre": "Multiplicacion Hadamard"},
                    "5": {"funcion": A.multiplicacionMatrices, "nombre": "producto matricial"},
                }
                
                # Submenú de operaciones binarias
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
                          # Ejecutar operación entre A y B
                        matriz_resultado = operacion["funcion"](B)
                        print(f"\nResultado {operacion['nombre']} de A y B:")
                        matriz_resultado.mostrarMatriz()
                        # GUARDAR EN HISTORIAL
                        guardar_operacion(
                            f"{operacion['nombre']} entre matriz A y matriz B",
                            matriz_resultado
                        )
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