#!/bin/sh

#set -x

TMPDIR="/tmp/betgame"
[ -d $TMPDIR ] || mkdir -p $TMPDIR

site="localhost:6543"
name="admin"
pass="None"
cookies="$TMPDIR/cookies.txt"

WGET="wget -nv"
DATADIR=$HOME/backup/$(echo ${site} | tr ':' '_')
[ -d $DATADIR ] || mkdir -p $DATADIR
cd $DATADIR

wget --save-cookies $cookies --keep-session-cookies --load-cookies $cookies "${site}" \
     -O $TMPDIR/login_form

# extract the hidden _csrf token from the login form:
csrf=`grep _csrf /tmp/betgame/login_form | cut -d\" -f 6`
#echo $csrf

wget --save-cookies $cookies --keep-session-cookies --load-cookies $cookies \
     --post-data="form.submitted&_csrf=$csrf&alias=$name&password=$pass" "http://${site}/login" \
     -O /dev/null

wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/categories" -O categories.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/settings" -O settings.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/matches" -O matches.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/players" -O players.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/tips" -O tips.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/final" -O final.dat

git ci -a -m'$(date +"%Y-%m-%d_%H%M")'
