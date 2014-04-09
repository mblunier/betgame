""" Define some application-wide properties.
"""

import socket
from datetime import datetime

PROJECT_TITLE = 'Brasil 2014 Bet Game'
ADMINS = [ 'admin', 'mb' ]

RESULTSERVER = 'wm2014.rolotec.ch'
RESULTPAGE = 'http://%s/results' % RESULTSERVER
# determine the local IP address to access this device
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((RESULTSERVER, 80))
GAME_URL = 'http://%s:8080' % s.getsockname()[0]
s.close()

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
    },
    {           # [6], like [4] but with smaller numbers
    'exacthit': 5,
    'outcome': 3,
    'missed': 1,
    'sumgoals': 3,
    'goaldiff': 2,
    'onescore': 1,
    'onefinalist': 5,
    'twofinalists': 10,
    }]

# bet values
BET_POINTS = SCORINGS[6]

# iterable list of group ids
GROUP_IDS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') 

# the final's match id
FINAL_ID = 64

# deadline for final tips (the beginning of the second stage)
FINAL_DEADLINE = datetime(2014, 6, 28, 18, 00)

