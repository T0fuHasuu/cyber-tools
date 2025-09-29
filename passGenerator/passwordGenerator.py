import secrets
import string

def randomizePass(length=16, require_classes=True):
    if length < 8:
        raise ValueError("length must be longer than 8")

    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = string.punctuation   

    all_chars = lower + upper + digits + symbols

    pwd = []
    if require_classes:
        pwd.append(secrets.choice(lower))
        pwd.append(secrets.choice(upper))
        pwd.append(secrets.choice(digits))
        pwd.append(secrets.choice(symbols))
    
    remaining = max(0, length - len(pwd))
    for _ in range(remaining):
        pwd.append(secrets.choice(all_chars))

    secrets.SystemRandom().shuffle(pwd)
    return ''.join(pwd)

def main():
    a = int(input("Enter Length : "))
    print(randomizePass(a))
    

if __name__ == '__main__':
    main()