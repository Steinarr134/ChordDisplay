import sys
if 'win' in sys.platform:
    from .FakeButtonHandler import *
else:
    from .ButtonCode import *
