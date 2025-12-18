def fahrenheit_to_celsius(f):
    """
    Convert temperature from Fahrenheit to Celsius.
    """
    return (f - 32) * 5 / 9


def celsius_to_fahrenheit(c):
    """
    Convert temperature from Celsius to Fahrenheit.
    """
    return (c * 9 / 5) + 32


def celsius_to_kelvin(c):
    """
    Convert temperature from Celsius to Kelvin.
    """
    return c + 273.15


def kelvin_to_celsius(k):
    """
    Convert temperature from Kelvin to Celsius.
    """
    return k - 273.15


def fahrenheit_to_kelvin(f):
    """
    Convert temperature from Fahrenheit to Kelvin.
    """
    return celsius_to_kelvin(fahrenheit_to_celsius(f))


def kelvin_to_fahrenheit(k):
    """
    Convert temperature from Kelvin to Fahrenheit.
    """
    return celsius_to_fahrenheit(kelvin_to_celsius(k))
