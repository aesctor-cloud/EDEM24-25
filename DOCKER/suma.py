import sys

def suma(a, b):
    return a + b

try:
    num1 = int(sys.argv[1])
    num2 = int(sys.argv[2])
except IndexError:
    print("Uso: docker run pysum <num1> <num2>")
    sys.exit(1)
    
resultado = suma(num1, num2)
print(f"La suma de {num1} y {num2} es {resultado}")