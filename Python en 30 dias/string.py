#Concatenate the string 'Thirty', 'Days', 'Of', 'Python' to a single string, 'Thirty Days Of Python'.
print('Thirty', 'Days', 'Of', 'Python')

#Declare a variable named company and assign it to an initial value "Coding For All".
company = "Coding For All"

#Print the length of the company string using len() method and print().
print(len(company))

#Change all the characters to uppercase letters using upper() method.
#Change all the characters to lowercase letters using lower() method.

company_up = company.upper()
print('1', company_up)
companu_lo = company.lower()
print('2', companu_lo)

#Use capitalize(), title(), swapcase() methods to format the value of the string Coding For All.
print('3', company.capitalize())
print('4', company.title())
print('5', company.swapcase())

#Cut(slice) out the first word of Coding For All string.
print('6', company[7:])

#Check if Coding For All string contains a word Coding using the method index, find or other methods.
busqueda = "Coding"
print('7', company.index(busqueda))

#Replace the word coding in the string 'Coding For All' to Python.
nuevo = company.replace("Coding", "coding")
print('8', nuevo)

#Split the string 'Coding For All' using space as the separator (split()) .

print('9', company.split(', '))
print('10', company.split(' '))

#What is the character at index 0 in the string Coding For All.
print(company[0])

#What is the last index of the string Coding For All.
print(company[-1])

#Create an acronym or an abbreviation for the name 'Python For Everyone'.
variable = "Python For Everyone"

print('11', variable)