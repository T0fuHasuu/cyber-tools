import datetime

def birthYear(year):
    day = 1
    month = 1
    current_year = datetime.datetime.now().year
    passwords = []
    while year != current_year or month != 12 or day != 31:
        password = f"{day:02d}{month:02d}{year}"
        passwords.append(password)
        day += 1
        if day > 31:
            day = 1
            month += 1
            if month > 12:
                month = 1
                year += 1  
    return passwords

def savePasswords(passwords, filename="pass.txt"):
    with open(filename, "a") as file:
        for password in passwords:
            file.write(password + "\n")
    print(f"Passwords saved successfully to {filename}.")

def main():
    year = int(input("Enter your birth year: "))
    passwords = birthYear(year)
    savePasswords(passwords)

if __name__=='__main__':
    main()