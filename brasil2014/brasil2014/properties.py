""" Define some application-wide properties.
"""

from datetime import datetime

PROJECT_TITLE = 'Brasil2014 Bet Game'

SCORINGS = [{   # [0]
    'exacthit': 12,
    'outcome': 7,
    'missed': 0,
    'sumgoals': 4,
    'goaldiff': 2,
    'onescore': 1,
    'onefinalist': 20,
    'twofinalists': 50,
    },
    {           # [1]
    'exacthit': 10,
    'outcome': 5,
    'missed': 0,
    'sumgoals': 3,
    'goaldiff': 2,
    'onescore': 1,
    'onefinalist': 20,
    'twofinalists': 30,
    },
    {           # [2]
    'exacthit': 5,
    'outcome': 4,
    'missed': 0,
    'sumgoals': 3,
    'goaldiff': 2,
    'onescore': 1,
    'onefinalist': 10,
    'twofinalists': 20,
    },
    {           # [3]
    'exacthit': 10,
    'outcome': 10,
    'missed': 5,
    'sumgoals': 3,
    'goaldiff': 2,
    'onescore': 1,
    'onefinalist': 20,
    'twofinalists': 50,
    },
    {           # [4]
    'exacthit': 10,
    'outcome': 5,
    'missed': 2,
    'sumgoals': 3,
    'goaldiff': 2,
    'onescore': 1,
    'onefinalist': 10,
    'twofinalists': 25,
    },
    {           # [5]
    'exacthit': 10,
    'outcome': 6,
    'missed': 3,
    'sumgoals': 3,
    'goaldiff': 2,
    'onescore': 1,
    'onefinalist': 20,
    'twofinalists': 50,
    }]

# bet values
BET_POINTS = SCORINGS[4]

# iterable list of group ids
GROUP_IDS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') 

# the final's match id
FINAL_ID = 64

# deadline for final tips (the beginning of the first quarter final)
FINAL_DEADLINE = datetime(2014, 6, 28, 18, 00)

