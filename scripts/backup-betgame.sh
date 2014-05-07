#!/bin/sh

#set -x

TMPDIR="/tmp/betgame"
[ -d $TMPDIR ] || mkdir $TMPDIR

site=${1:-"127.0.0.1:8080"}
name=${2:-"admin"}
pass=${3:-"None"}
cookies="$TMPDIR/cookies.txt"

WGET="wget -v"
DATADIR=`echo ${site} | tr ':' '_'`@`date +"%Y-%m-%d_%H%M"`
[ -d $DATADIR ] || mkdir $DATADIR

wget --save-cookies $cookies --keep-session-cookies --load-cookies $cookies "${site}" \
     -O $TMPDIR/login_form

# extract the hidden _csrf token from the login form:
csrf=`grep _csrf /tmp/betgame/login_form | cut -d\" -f 6`
#echo $csrf

wget --save-cookies $cookies --keep-session-cookies --load-cookies $cookies \
     --post-data="form.submitted&_csrf=$csrf&alias=$name&password=$pass" "http://${site}/login" \
     -O /dev/null

wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/categories" \
     -O $DATADIR/categories.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/settings" \
     -O $DATADIR/settings.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/matches" \
     -O $DATADIR/matches.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/players" \
     -O $DATADIR/players.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/tips" \
     -O $DATADIR/tips.dat
wget --keep-session-cookies --save-cookies $cookies --load-cookies $cookies "http://${site}/backup/final" \
     -O $DATADIR/final.dat
