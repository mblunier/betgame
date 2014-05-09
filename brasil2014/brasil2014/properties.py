""" Define some application-wide properties.

TODO: move these to a config file.
"""

from datetime import datetime

PROJECT_TITLE = 'Unofficial Brasil 2014 Bet Game'
ADMINS = [ 'admin' ]

# iterable list of group ids
GROUP_IDS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') 

# the final's match id
FINAL_ID = 64

# deadline for final tips (the beginning of the second stage)
FINAL_DEADLINE = datetime(2014,6,28, 18,00)
