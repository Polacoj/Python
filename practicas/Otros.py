print(help("keywords"))
print(help("is"))


# -----------FORMATOS para enteros-------------
num1 = 1_000_000_000
num2 = 10_000_0000
total = num1+num2

print(type(num1))
print(type(num2))
print(type(total))
print(total)

print(f'{total:,}')
print(f'{total:_}')

listOne = [20, 40, 60, 80]
listTwo = [20, 40, 60, 80]

print(id(listOne), id(listTwo))
print(listOne == listTwo)
print(listOne is listTwo)   # -------IS------> compara el ID-la ubicacion en memoria----

var = "James Bond"
print(var[4::-1])   # ------------4 posicicon inicial, -1 en sentido hacia la izquierda


# ------> corroborar tipo de entrada-------------

def check_user_input(input):
    try:
        # Convert it into integer
        val = int(input)
        print("Input is an integer number. Number = ", val)
    except ValueError:
        try:
            # Convert it into float
            val = float(input)
            print("Input is a float  number. Number = ", val)
        except ValueError:
            print("No.. input is not a number. It's a string")


input1 = input("Enter your Age ")
check_user_input(input1)

input2 = input("Enter any number ")
check_user_input(input2)

input2 = input("Enter the last number ")
check_user_input(input2)


