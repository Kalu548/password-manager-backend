from utils import user, utilities, password
import utils 
from prettytable import PrettyTable
import csv 
from halo import Halo

menu = """
+---------------------+------------------------------------------------------+
| Command             | Function                                             |
+---------------------+------------------------------------------------------+
| login               | Log in to your account to access your profile.         |
| register            | Create a new account and register with the system.     |
| show_all_passwords  | Retrieve a comprehensive list of all saved passwords.  |
| show_password       | View specific details of a stored password.            |
| create_password     | Create a new password in your account.                 |
| delete_password     | Remove a saved password from your account.             |
| update_password     | Modify an existing password in your records.           |
| export              | Export all saved passwords into a CSV file.            |
| logout              | Safely log out from your account.                      |
| exit                | Exit                                                   |
+---------------------+------------------------------------------------------+
"""


USER_ID = ""
MASTER_KEY = ""

def get_decrypted_password_data(user_id, master_key):
    try:
        password_info = password.get_password(password_id, user_id)
        password_info["password"] = utilities.decrypt_password(password_info["password"], master_key)
        return password_info
    except Exception as e:
        print("Password Does not exist")

def print_password(password_info):
    if password_info:
        table = PrettyTable
        table.field_names = ["Id", "Name", "Username", "Password", "URL", "Created At"]
        table.add_row([password_info["id"], password_info["name"], password_info["username"], password_info["password"], password_info["url"], password_info["created_at"]])
        print(table)


print(menu)
while True:
    print(USER_ID, MASTER_KEY)
    command = input("Enter a command: ")
    if command == "register":
        email = input("Enter your email: ")
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        spinner = Halo(text='Creating your account', spinner='dots')
        spinner.start()
        master_key = utilities.generate_master_key()
        hashed_master_key = utilities.generate_password_hash(master_key)
        hashed_password = utilities.generate_password_hash(password)
        try:
            user_id = user.create_user(email, username, hashed_password, hashed_master_key)
            spinner.succeed(text="Account created successfully")
            print("A master key has been generated. Please keep it safe as It cannot be recovered for security reasons.")
            print("Master Key - ", master_key)
            print("Please log in into your account")
        except Exception as e:
            spinner.fail(text="User already exists")

    elif command == "login":
        email = input("Enter your email: ")
        entered_password = input("Enter your password: ")
        master_key = input("Enter your master key: ")
        spinner = Halo(text='Logging in', spinner='dots')
        spinner.start()
        user_info = user.get_user_from_email(email)
        if not utilities.check_password_hash(entered_password, user_info["password"]):
            spinner.fail(text="Incorrect password")
            continue
        if not utilities.check_password_hash(master_key, user_info["master_key"]):
            spinner.fail("Incorrect master key")
            continue
        spinner.succeed("Successfully logged into your account")
        USER_ID = str(user_info["id"])
        MASTER_KEY = master_key
    
    elif command == "exit":
        break
    # check if USER_ID and MASTER_KEY is not empty if they are empty prompt the user to log in
    elif len(USER_ID) == 0 or len(MASTER_KEY) == 0:
        print("Please log in into your account")
        continue

    elif command == "show_all_passwords":
        table = PrettyTable()
        table.field_names = ["Id", "Name", "Username", "URL", "Created At"]
        spinner = Halo(text='Retrieving passwords', spinner='dots')
        spinner.start()
        user_passwords = password.get_all_passwords(USER_ID)
        if len(user_passwords) == 0:
            spinner.warn(text="You do not have any passwords saved")
        else:
            spinner.succeed(text="Successfully retrieved passwords")
            for i in user_passwords:
                table.add_row([i["id"], i["name"], i["username"], i["url"], i["created_at"]])
            print(table)

    elif command == "create_password":
        name = input("Enter the name of the password: ")
        username = input("Enter the username: ")
        user_password = input("Enter the password: ")
        url = input("Enter the url: ")
        spinner = Halo(text='Creating password', spinner='dots')
        spinner.start()
        try:
            password_id = password.create_password(USER_ID, name, url, username, user_password)
            spinner.succeed("Password created successfully")
            print("Password id: ", password_id)
        except Exception as e:
            spinner.fail("Password already exists")

    elif command == "show_password":
        password_id = input("Enter the password id: ")
        password_data = get_decrypted_password_data(USER_ID, MASTER_KEY)
        print_password(password_data)

    
    elif command == "delete_password":
        password_id = input("Enter the password id: ")
        conifrmation = input("Are you sure you want to delete this password? (y/n): ")
        spinner = Halo(text='Deleting password', spinner='dots')
        spinner.start()
        if conifrmation.lower() != "y":
            if password.delete_password(password_id, USER_ID):
                spinner.succeed("Password deleted successfully")
            else:
                spinner.fail("Password does not exist")
        else:
            spinner.fail("Password not deleted")

    elif command == "update_password":
        password_id = input("Enter the password id: ")
        password_data = get_decrypted_password_data(USER_ID, MASTER_KEY)
        print_password(password_data)
        field = input("Enter the field you want to update (name, username, password, url):  ")
        if field not in ["name" , "username" , "password" , "url" ]:
            print("Invalid field")
        else:
            changed_value = input("Enter the new value: ")
            spinner = Halo(text='Updating password', spinner='dots')
            spinner.start()
            password_data[field] = changed_value
            encrypted_password = utilities.encrypt_password(password_data["password"])
            try:
                password.update_password(password_id, password_data["name"], password_data["username"], encrypted_password, password_data["url"])
                spinner.succeed("Password updated successfully")
            except Exception as e:
                spinner.fail("Password does not exist" , e)

    elif command == "export":
        passwords = password.user_password_list(USER_ID, MASTER_KEY)
        spinner = Halo(text='Exporting passwords', spinner='dots')
        spinner.start()
        with open("saved_passwords.csv", mode="w") as file:
            writer = csv.writer(file)
            writer.writerow(["Id", "Name", "Username", "Password", "Url", "Created At"])
            writer.writerows(passwords)
        spinner.succeed("Passwords exported successfully")

    elif command == "exit":
        break
    print()
