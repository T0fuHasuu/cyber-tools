# Password generator 
def checkPass(passwd):
    if passwd is None:
        return "Check Again"
    elif len(passwd) < 8:
        return "Too Short"
    elif len(passwd) == 8:
        return passwd

print(checkPass("12345678"))