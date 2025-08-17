# --------->ejercicio fibonacci hasta 4mill la suma de los pares---------
a = 0
b = 1
res = 0

for i in range(1000):
    i = a + b
    a = b
    b = i
    if i < 4000000:
        if (i % 2 == 0):
            res += i
    else:
        break
    print(i)
print('pares fibo hasta 4 millones : ', res)

# --------> numeros primos de 600851475143---------------
num = 600851475143
i = 2
while i <= num:
    if num % i == 0:
        factor = i
        num = num / i
    else:
        i += 1
print(factor)

# --------> palindromo de 3 numeros
def palindormo(num):
    pal_str = str(num)
    for i in range(0, int(len(pal_str)/2)):
        if pal_str[i] != pal_str[-i-1]:
            return False
    return True

num_maximo = 0
for i in range(999, 99, -1):
    for j in range(999, 99, -1):
        res = i * j
        if palindormo(res)> num_maximo:
            num_maximo = res

print('palindromo ==>', num_maximo)

