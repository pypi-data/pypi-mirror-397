# Set locale FIRST before importing anything else
import locale
try:
    locale.setlocale(locale.LC_NUMERIC, 'C')  # Ensure decimal point is '.'
except locale.Error:
    pass  # Fallback if 'C' locale is not available

from .core import main

if __name__ == "__main__":
    main()