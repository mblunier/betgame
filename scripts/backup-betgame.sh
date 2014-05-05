#!/bin/sh

#set -x

TMPDIR="/tmp/betgame"
[ -d $TMPDIR ] || mkdir $TMPDIR

name=${1:-"admin"}
pass=${2:-"None"}
site="http://127.0.0.1:6543/"
cookies="$TMPDIR/cookies.txt"

WGET="wget -v"
DATADIR=`date +"%Y-%m-%d_%H%M"`
[ -d $DATADIR ] || mkdir $DATADIR

wget --save-cookies $cookies --keep-session-cookies --load-cookies $cookies "${site}" \
     -O $TMPDIR/login_form

# extract the hidden _csrf token from the login form:
csrf=`grep _csrf /tmp/betgame/login_form | cut -d\" -f 6`
#echo $csrf

wget --save-cookies $cookies --keep-session-cookies --load-cookies $cookies \
     --post-data="form.submitted&_csrf=$csrf&alias=$name&password=$pass" "${site}login" \
     -O /dev/null

wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "${site}backup/categories" \
     -O $DATADIR/categories.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "${site}backup/settings" \
     -O $DATADIR/settings.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "${site}backup/matches" \
     -O $DATADIR/matches.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "${site}backup/players" \
     -O $DATADIR/players.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "${site}backup/tips" \
     -O $DATADIR/tips.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "${site}backup/final" \
     -O $DATADIR/final.dat
