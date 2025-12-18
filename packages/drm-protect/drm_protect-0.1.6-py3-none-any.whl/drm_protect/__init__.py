import sys

major, minor = sys.version_info.major, sys.version_info.minor

if major == 3 and minor == 9:
    from .module309 import main
elif major == 3 and minor == 10:
    from .module310 import main
elif major == 3 and minor == 11:
    from .module311 import main
elif major == 3 and minor == 12:
    from .module312 import main
elif major == 3 and minor == 13:
    from .module313 import main
else:
    raise Exception(f"Python {major}.{minor} is not supported!")

__all__ = ["main"]

main()
