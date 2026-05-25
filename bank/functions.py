import random
from datetime import date

def generate_card_number():
    number = "4377"
    for i in range(0, 12):
        number += str(random.randint(0, 9))
    return number

def generate_cvv():
    cvv = ""
    for i in range(0, 3):
        cvv += str(random.randint(0, 9))
    return cvv

def default_expiry_date():
    today = date.today()

    return date(today.year + 4, today.month, today.day)