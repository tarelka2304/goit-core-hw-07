from collections import UserDict
from datetime import datetime, date, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
              raise ValueError ("Ім’я не може бути порожнім")
        super().__init__(value)

        

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
             raise ValueError("Номер телефону має містити 10 цифр")
        super().__init__(value)


class Birthday(Field):
    FORMAT = "%d.%m.%Y"

    def __init__(self, value):
        try:
            parced = datetime.strptime(value, self.FORMAT)
            normalized = parced.strftime(self.FORMAT)
            super().__init__(normalized)
            self._date = parced.date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
    @property
    def date(self):
        return self._date



class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self,phone):
         self.phones.append(Phone(phone))

    def remove_phone(self, phone):
         phone_obj = self.find_phone(phone)
         if phone_obj:
             self.phones.remove(phone_obj)

    def find_phone(self,phone):
         for p in self.phones:
              if p.value == phone:
                   return p
        
         return None

    def edit_phone(self, old_phone, new_phone):
         old = self.find_phone(old_phone)
         if not old:
             raise ValueError("Старий номер не знайдено")
         
        
         self.add_phone(new_phone)
         self.remove_phone(old_phone)
         return True
         
    def add_birthday(self, date_str):
        self.birthday = Birthday(date_str)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self,record):
        self.data[record.name.value]=record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
    
    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
    
    def get_upcoming_birthdays(self, days: int = 7, today: date | None = None):
        if today is None:
            today = date.today()
        end_date = today + timedelta(days=days - 1)
        result = []
        for record in self.data.values():
            if not record.birthday:
                continue
            bday = record.birthday.date
            upcoming = bday.replace(year=today.year)
            if upcoming < today:
                upcoming = upcoming.replace(year=today.year + 1)
            if upcoming.weekday() == 5:
                upcoming = upcoming + timedelta(days=2)
            elif upcoming.weekday() == 6:
                upcoming = upcoming + timedelta(days=1)
            if today <= upcoming <= end_date:
                result.append({
                    "name": record.name.value,
                    "birthday": upcoming.strftime("%d.%m.%Y")
                })
        return result


# BOT:

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return str(e) if str(e) else "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough arguments for this command."
    return wrapper


def parse_input(user_input: str):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."


@input_error
def show_phones(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    if not record.phones:
        return f"No phones for {name}."
    return f"{name}: " + "; ".join(p.value for p in record.phones)


@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday_cmd(args, book: AddressBook):
    name, bday_str, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
    record.add_birthday(bday_str)
    return "Birthday added."


@input_error
def show_birthday_cmd(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    if record.birthday is None:
        return "Birthday is not set."
    return f"{name}: {record.birthday.value}"


@input_error
def birthdays_cmd(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays(days=7)
    if not upcoming:
        return "No birthdays in the next 7 days."
    by_date = {}
    for item in upcoming:
        by_date.setdefault(item["birthday"], []).append(item["name"])
    lines = []
    for d in sorted(by_date.keys(), key=lambda s: tuple(reversed([int(x) for x in s.split(".")]))):
        lines.append(f"{d}: {', '.join(by_date[d])}")
    return "\n".join(lines)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phones(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday_cmd(args, book))
        elif command == "show-birthday":
            print(show_birthday_cmd(args, book))
        elif command == "birthdays":
            print(birthdays_cmd(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()




