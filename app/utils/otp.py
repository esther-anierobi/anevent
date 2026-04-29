import random


def generate_otp() -> str:
    """ Generates a random 6-digit OTP string """
    return str(random.randint(100000, 999999))
