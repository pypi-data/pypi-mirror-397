def add(a, b):
    "this function adds two numbers"
    return a + b    

def subtract(a, b):
    "this function subtracts two numbers"
    return a - b            

def multiply(a, b):
    "this function multiplies two numbers"
    return a * b    

def divide(a, b):
    "this function divides two numbers"
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b    

def power(a, b):
    "this function raises a to the power of b"
    return a ** b

def modulus(a, b):
    "this function returns the modulus of a and b"
    return a % b

def floor_divide(a, b):
    "this function performs floor division of a by b"
    if b == 0:
        raise ValueError("Cannot perform floor division by zero.")
    return a // b

def square_root(a):
    "this function returns the square root of a number"
    if a < 0:
        raise ValueError("Cannot compute square root of a negative number.")
    return a ** 0.5

def cube_root(a):
    "this function returns the cube root of a number"
    return a ** (1/3)

def percentage(a, b):
    "this function returns b percent of a"
    return (a * b) / 100