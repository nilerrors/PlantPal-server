import string
import random


def generate_random_code(length: int):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(length))
