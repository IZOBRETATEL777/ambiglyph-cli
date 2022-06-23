import requests

API_URL = "http://167.235.50.112:8081/ambiglyph-server"
IS_AUTHENTICATED = False
JWT_TOKEN = None


def authenticate(login="client", password="client"):
    data = {
        "login": login,
        "password": password
    }
    response = requests.post(API_URL + "/authenticate", json=data)
    if response.status_code == 200:
        global JWT_TOKEN
        JWT_TOKEN = response.json()["token"]
        global IS_AUTHENTICATED
        IS_AUTHENTICATED = True
    else:
        print("Authentication failed")


def register(login, password):
    global IS_AUTHENTICATED
    global JWT_TOKEN
    if IS_AUTHENTICATED is True:
        return
    authenticate()
    if JWT_TOKEN is None:
        return
    headers = {"Authorization": "Bearer " + JWT_TOKEN}
    data = {
        "login": login,
        "password": password
    }
    response = requests.post(API_URL + "/users", json=data, headers=headers)
    if response.status_code == 200:
        print("Registration successful")
        authenticate(login, password)
        IS_AUTHENTICATED = True
    else:
        print("Registration failed")
        JWT_TOKEN = None


def get_text():
    while True:
        print("Please enter option")
        print("1 - to enter text manually")
        print("2 - to enter text from file")
        choice = input("Enter your choice: ")
        if choice == "1":
            text = input("Enter text: ")
            return text
        elif choice == "2":
            file_name = input("Enter file name: ")
            with open(file_name, "r") as f:
                text = f.read()
            return text
        else:
            print("Invalid choice")


def get_range():
    while True:
        print("Please enter range of words to be shown")
        range = int(input())
        if range > 0:
            return range
        else:
            print("Invalid range")


def check_text():
    if JWT_TOKEN is None:
        return
    text = get_text()
    print("Original text:")
    print(text + "\n")
    word_range = get_range()
    data = {
        "text": text,
        "suggestionsNumber": word_range,
        "warninsNumber": word_range
    }
    response = requests.post(API_URL + "/check", json=data, headers={"Authorization": "Bearer " + JWT_TOKEN})
    if response.status_code == 200:
        current_text = response.json()["text"]
        candidates = response.json()["candidates"]
        warnings = response.json()["warnings"]
        if (response.json()["haveDetections"] == True):
            print("Text is ambiguous!\n")
            print(current_text)
            if len(candidates) == 0:
                return
            print("Do you want to repair it? (y/n)")
            choice = input("Enter your choice: ")
            if choice == "y":
                repaired = repair_text(current_text, candidates)
                print("Repaired text:")
                print(repaired)
                print("Do you want to save it? (y/n)")
                choice = input("Enter your choice: ")
                if choice == "y":
                    with open("repaired.txt", "w") as f:
                        f.write(repaired)
                    print("Repaired text saved to file")
        else:
            print("Nothing found")


def repair_text(text, candidates):
    for idx, candidate in enumerate(candidates):
        meta = "<%ambiglyph-detected>" + str(idx) + "<ambiglyph-detected%>"
        for word in candidate:
            print(f"Is {word} a {meta}? (y/n)")
            choice = input("Enter your choice: ")
            if choice == "y":
                text = text.replace(meta, word)
                print(text)
                break
    for idx in enumerate(candidates):
        meta = "<%ambiglyph-warning>" + str(idx) + "<ambiglyph-warning%>"
        text = text.replace(meta, "")
    return text


def add_word(word):
    if JWT_TOKEN is None or IS_AUTHENTICATED is False:
        print("You are not logged in")
        return
    data = {
        "word": word
    }
    headers = {
        "Authorization": "Bearer " + JWT_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.post(API_URL + "/words", json=data, headers=headers, timeout=None)
    if response.status_code == 200:
        print("Word added")
    else:
        print("Word not added")


def get_dictionary():
    if JWT_TOKEN is None:
        return
    response = requests.get(API_URL + "/words", headers={"Authorization": "Bearer " + JWT_TOKEN})
    if response.status_code == 200:
        print(response.json())
    else:
        print("Nothing found")


def getSession():
    print("Welcome to the Ambiglyph CLI!")
    print("Please enter:"
            "\n1 - to login"
            "\n2 - to register"
            "\n3 - to contine without login"
            "\n4 - to exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        login = input("Enter your login: ")
        password = input("Enter your password: ")
        authenticate(login, password)
    elif choice == "2":
        login = input("Enter your login: ")
        password = input("Enter your password: ")
        register(login, password)
    elif choice == "3":
        authenticate()
        if JWT_TOKEN is not None:
            print("You are logged in")
        else:
            print("You are not logged in")
    elif choice == "4":
        print("Goodbye!")
        exit(0)
    else:
        print("Invalid choice")


def main():
    while JWT_TOKEN is None:
        getSession()
    while True:
        print("Please enter:"
                "\n1 - to check text"
                "\n2 - to add word"
                "\n3 - to get dictionary"
                "\n4 - to exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            check_text()
        elif choice == "2":
            word = input("Enter word: ")
            add_word(word)
        elif choice == "3":
            get_dictionary()
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()

