import random
from validaciones import validarMatrizCuadrada, puedenMultiplicarse

class Matriz:

    # Inicializa una matriz de tamaño filas x columnas llena de ceros
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.matriz = [[0 for _ in range(columnas)] for _ in range(filas)]
        
        
#region crear matriz de manera aleatroria  
    @classmethod
    def crearMatriz(cls):
        while True:
            try: 
                filas = int(input("Ingrese el número de filas: "))
                columnas = int(input("Ingrese el número de columnas: "))

                if filas <= 0 or columnas <= 0:  # Validación: dimensiones mayores a 0
                    print("Los valores deben ser mayores que 0. Intente nuevamente")
                    continue

                break
            except ValueError:
                print("Entrada no valida, porfavor ingrese un número entero")

        return cls._crear_aleatoria(filas, columnas)

# Método que llena la matriz con números aleatorios entre 1 y 20
    @classmethod
    def _crear_aleatoria(cls,filas,columnas):
        obj = cls(filas, columnas)
        for i in range(filas):
            for j in range(columnas):
                obj.matriz[i][j]= random.randint(1,20)
        return obj
    
#endregion
    
#region crear matriz de manera manual y mostrar la matriz 

    @classmethod
    def crear_manual(cls):
        while True:
            try:
                filas = int(input("Ingrese número de filas: "))
                columnas = int(input("Ingrese número de columnas: "))
                
                if filas<=0 or columnas<=0:
                    print("Las dimensiones deben ser mayores que 0.")
                    continue

                obj = cls(filas, columnas)

                for i in range(filas):
                    for j in range(columnas):
                        valor = float(input(f"Valor [{i}][{j}]: "))
                        obj.matriz[i][j] = valor

                return obj
            
            except ValueError:
                print("Entrada inválida. Debe ingresar números.")
        

    def mostrarMatriz(self): #crea un espacio al rededor de los numeros, que se vea bonito
        print()
        for fila in self.matriz:
            print(" ".join(f"{num:8.2f}" for num in fila)) #la matriz formateada con dos decimales
        print()
        
        #metodo especial = Cuando alguien quiera convertir mi objeto en texto, así es como debe mostrarse.
    def __str__(self):
        texto = ""
        for fila in self.matriz:
            texto += " ".join(f"{num:8.2f}" for num in fila) + "\n"
        return texto       

#endregion
    

#region operaciones de dos matrices ejemplo a<->b   
# Método general para aplicar operaciones elemento a elemento
    def operacionesEntreMatrices(self,other,operacion):
        
        if not isinstance(other, Matriz): # Verifica que el objeto sea una matriz
            raise TypeError("El objeto debe ser una matriz")
        
        if self.filas != other.filas or self.columnas != other.columnas:# Verifica que tengan el mismo tamaño
            raise ValueError("Las matrices deben de tener el mismo tamaño")
        
        nueva_matriz = Matriz(self.filas, self.columnas)
        
        # Recorre cada posición y aplica la operación
        for i in range(self.filas):
            for j in range(self.columnas):
                nueva_matriz.matriz[i][j] = operacion(self.matriz[i][j], other.matriz[i][j])

        return nueva_matriz

    def sumaMatrices(self,other):
        return self.operacionesEntreMatrices(other,lambda a,b: a+b)

    def restaMatrices(self,other):
        return self.operacionesEntreMatrices(other,lambda a,b: a-b)
    
    def divisionMatrices(self,other):
        def dividir(a,b):
            if b == 0:
                raise ZeroDivisionError("\nNo se puede dividir entre 0 en la matriz B")
            return a/b
        return self.operacionesEntreMatrices(other, dividir)
    
    
    def multiplicacionMatricesHadamard(self,other):
        return self.operacionesEntreMatrices(other,lambda a,b: a*b)
    
    def multiplicacionMatrices(self, other):

        if puedenMultiplicarse(self.columnas, other.filas) == False:
            raise ValueError("Las columnas de la matriz A deben coincidir con las filas de la matriz B")

        matrizR = Matriz(self.filas, other.columnas)

        for i in range (self.filas):
            for j in range (other.columnas):
                for k in range (self.columnas):
                    matrizR.matriz[i][j] += self.matriz[i][k]*other.matriz[k][j]

        return matrizR #matriz resultado
    
#endregion    
    
#region operaciones con escalar

    def operacionesEscalares(self,k,operacion):

        nueva_matriz = Matriz(self.filas, self.columnas)

        for i in range(self.filas):
            for j in range(self.columnas):
                nueva_matriz.matriz[i][j] = operacion(self.matriz[i][j], k)

        return nueva_matriz
    
    def sumaEscalar(self,k):
        return self.operacionesEscalares(k, lambda a,k:a+k)
    
    def restaEscalar(self,k):
        return self.operacionesEscalares(k, lambda a,k:a-k)
    
    def multiplicacionEscalar(self,k):
        return self.operacionesEscalares(k, lambda a,k:a*k)
    
    def divisionEscalar(self,k):
        if k==0:
            raise ZeroDivisionError("\nNo se puede dividir entre 0")
        return self.operacionesEscalares(k, lambda a,k:a/k )

#endregion

#region operaciones avanzadas
    def determinante(self):
        # Verifica que la matriz sea cuadrada (misma cantidad de filas y columnas)
        validarMatrizCuadrada(self.filas, self.columnas)

        # Caso base: matriz de 1x1 → el determinante es el único elemento
        if self.filas == 1:
            return self.matriz[0][0]

        # Caso base: matriz de 2x2 → fórmula directa
        if self.filas == 2:
            return (self.matriz[0][0] * self.matriz[1][1]
                    - self.matriz[0][1] * self.matriz[1][0])

        # Caso general: expansión por cofactores usando la primera fila
        det = 0
        for col in range(self.columnas):

            # Construir la submatriz eliminando la fila 0 y la columna actual
            submatriz = [
                [self.matriz[i][j] for j in range(self.columnas) if j != col]
                for i in range(1, self.filas)
            ]

            # Crear un nuevo objeto Matriz con la submatriz
            sub = Matriz(self.filas - 1, self.columnas - 1)
            sub.matriz = submatriz

            # Aplicar la fórmula del cofactor y llamar recursivamente al determinante
            det += ((-1) ** col) * self.matriz[0][col] * sub.determinante()

        # Retornar el determinante total
        return det


    def matrizAdjunta(self):
        # Verifica que la matriz sea cuadrada
        validarMatrizCuadrada(self.filas, self.columnas)

        n = self.filas
        cofactores = Matriz(n, n)

        # Calcular la matriz de cofactores
        for i in range(n):
            for j in range(n):

                # Crear la submatriz eliminando la fila i y la columna j
                submatriz = [
                    [self.matriz[f][c] for c in range(n) if c != j]
                    for f in range(n) if f != i
                ]

                # Crear objeto matriz para calcular su determinante
                sub = Matriz(n - 1, n - 1)
                sub.matriz = submatriz

                # Calcular el cofactor usando el signo (-1)^(i+j)
                cofactores.matriz[i][j] = ((-1) ** (i + j)) * sub.determinante()

        # La matriz adjunta es la transpuesta de la matriz de cofactores
        adjunta = Matriz(n, n)
        for i in range(n):
            for j in range(n):
                adjunta.matriz[j][i] = cofactores.matriz[i][j]

        return adjunta

    def inversa(self):
        validarMatrizCuadrada(self.filas,self.columnas)

        det = self.determinante()

        if det == 0:
            raise ValueError("La matriz no tiene inversa (determinante = 0)")

        adjunta = self.matrizAdjunta()

        inversa = adjunta.multiplicacionEscalar(1 / det)

        return inversa

    def traza(self):
        validarMatrizCuadrada(self.filas,self.columnas)

        suma = 0
        for i in range(self.filas):
            suma += self.matriz[i][i]

        return suma

    def transpuesta(self):
        matTranspuesta = Matriz(self.columnas,self.filas)
        for j in range(self.columnas):
            for i in range(self.filas):
                matTranspuesta.matriz[j][i] = self.matriz[i][j]
        
        return matTranspuesta    
#endregion