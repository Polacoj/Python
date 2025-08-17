"""Inside 30DaysOfPython create a folder called day_2. Inside this folder create a file named variables.py--✅
Write a python comment saying 'Day 2: 30 Days of python programming' --✅
Declare a first name variable and assign a value to it --✅
Declare a last name variable and assign a value to it --✅ 
Declare a full name variable and assign a value to it --✅
Declare a country variable and assign a value to it --✅
Declare a city variable and assign a value to it--✅
Declare an age variable and assign a value to it--✅
Declare a year variable and assign a value to it--✅
Declare a variable is_married and assign a value to it--✅
Declare a variable is_true and assign a value to it --❌
Declare a variable is_light_on and assign a value to it--✅
Declare multiple variable on one line--✅"""

# Dia 2: 30 dias en python

firs_name = "Alexis"
last_name = "Jankowicz"
full_name = "Alexis Jankowicz"
country = "Argentina"
city = "Buenos Aires"
age = 45
year = 2023
is_married = False
is_light_on = False
nombre, apellido, edad, casado = "Alexis", "Jankowicz", 45, False

"""Check the data type of all your variables using type() built-in function --✅
Using the len() built-in function, find the length of your first name --✅
Compare the length of your first name and your last name
Declare 5 as num_one and 4 as num_two --✅
Add num_one and num_two and assign the value to a variable total --✅
Subtract num_two from num_one and assign the value to a variable diff --✅
Multiply num_two and num_one and assign the value to a variable product --✅
Divide num_one by num_two and assign the value to a variable division --✅
Use modulus division to find num_two divided by num_one and assign the value to a variable remainder --✅
Calculate num_one to the power of num_two and assign the value to a variable exp --✅
Find floor division of num_one by num_two and assign the value to a variable floor_division --✅
----The radius of a circle is 30 meters.
Calculate the area of a circle and assign the value to a variable name of area_of_circle --✅
Calculate the circumference of a circle and assign the value to a variable name of circum_of_circle --✅
Take radius as user input and calculate the area. --✅
Use the built-in input function to get first name, last name, country and age from a user and store the value 
to their corresponding variable names --✅
Run help('keywords') in Python shell or in your file to check for the Python reserved words or keywords --❌"""

print(type(firs_name))
print(type(full_name))
print(type(last_name))
print(type(country))
print(type(city))
print(type(age))
print(type(year))
print(type(is_married))
print(type(is_light_on))
print(len(firs_name))
print(len(last_name))
num_one = 5
num_two = 4
total = num_one + num_two
diferencia = num_one - num_two
mult = num_two * num_one
div = num_one / num_two
modulo = num_two % num_one
potencia = num_one**num_two
redonde_hacia_abajo_resultado = num_one // num_two
area = 3.14 * (30 ** 2)
print("area = " + str(area) + " mts")
circunferencia = 60 * 3.14
print("circunferencia = ",circunferencia, "mts")
radius = int(input("Ingrese radio del circulo: "))
print(f"El area del radio {radius} es {(3.14 * (radius**2))}")
nombre = input("nombre: ")
apellido = input("apellido: ")
edad = int(input("edad: "))
print(f"el nombre es {nombre} de apellido {apellido} y {edad} años")

