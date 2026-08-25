CURRENCY_SYMBOLS = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "AED": "د.إ",
    "CAD": "C$",
    "JPY": "¥",
}


def get_currency_symbol(currency_code):
    return CURRENCY_SYMBOLS.get(currency_code, "₹")


def get_supported_currencies():
    return [
        {"code": "INR", "name": "Indian Rupee", "symbol": "₹"},
        {"code": "USD", "name": "US Dollar", "symbol": "$"},
        {"code": "EUR", "name": "Euro", "symbol": "€"},
        {"code": "GBP", "name": "British Pound", "symbol": "£"},
        {"code": "AED", "name": "UAE Dirham", "symbol": "د.إ"},
        {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
        {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
    ]
