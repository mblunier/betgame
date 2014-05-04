brasil2014 README
==================

Getting Started
---------------

- Follow the steps to setup a virtual Python environment as described
  in 'DEVELOP.txt'.

- Get a copy of the distributed game 'brasil2014-x.y.tar.gz'.

- Install the game (this step must be repeated for every new release):
  (betgame)$ easy_install path/to/brasil2014-x.y.tar.gz

- Edit the categories in '~/betgame/lib/python2.7/site-packages/brasil2014-x.y-py2.7.egg/brasil2014/scripts/initialize_db.py'.

- Extract the production.ini file from the archive and adapt it as desired
  (as port 80 is reserved for root the default port is 8080).

- Initialize database content:
  $ initialize_brasil2014_db production.ini

- Launch the service:
  $ pserve production.ini

- Open the URL http://<hostname_or_ip>:8080 in your preferred web browser.



Administration
--------------
Some pages are restricted to the administrator(s) maintaining a betgame
instance. Once everything is initialized most of the required steps can
be automated. This chapter describes the available functions (all URLs
relative to the root):

  /backup/{table}
	Dumps the binary content of the indicated table. Available table
	names are: 'categories', 'settings', 'players', 'matches', 'teams',
	'tips' and 'final'. Their content should be saved as files to be
	available for restoring.

  /match/{id}/{team1}/{team2}
	Specifies the team mnemonics for the stage 2 match with id {id}. This
	is required after stage 1 and after every stage 2 match.

  /restore
	Displays a form to specify a table name and a data file with saved
	table contents. After submitting the form the file is uploaded and
	its content replaces all items with matching keys.

  /score/{id}/{score1}/{score2}
	Specifies the score for the match with id {id}. Using -1 for the
	scores deletes the score. This is required after every match.

  /setting/{name}/{value}
	Creates or updates a setting (see below).

  /sysinfo
  	Shows information about the server where the game is running.

  /unregister/{alias}
	Deletes the player {alias} together with all related data from the DB.

  /update_local
	Updates all team & player points according to the locally stored match
	results.

  /update_remote
	Updates all team & player points according to the match results stored
	on the configured result server (default: 'wm2014.rolotec.ch'). Calling
	this function regularly or at least after every match suffices to keep 
	the local instance up to date.


Settings
--------
Some aspects of the game are customizable via the Setting table. The following
keys are recognized:

  admin_alias (default: admin)
	The alias of the admin user.

  admin_mail (default: admin@rolotec.ch)
	The contact mail shown on the help page.

  result_server (default: wm2014.rolotec.ch)
	The name of the server providing match results. Any instance of the
	betgame where results are entered may be used.

  items_per_page
	The number of items shown on pages with pagination.

  scoring_exacthit (default: 5)
	The number of points for an exact hit.

  scoring_goaldiff (default: 2)
	The number of points for guessing the goal difference.

  scoring_missed (default: 1)
	The number of points for entering a bet. Only taken if neither an
	exact hit nor the outcome was guessed.

  scoring_onefinalist (default: 5)
	Number of points for guessing 1 finalist.

  scoring_onescore (default: 1)
	The number of points for guessing 1 score exactly. Not used for the
	default scoring algorithm.

  scoring_outcome (default: 3)
	The number of points for guessing the outcome (1/X/2) without hitting
	the exact result.

  scoring_sumgoals (default: 3)
	The number of points for guessing the goal difference.

  scoring_twofinalists (default: 10)
	Number of points for guessing both finalists.

All stored settings can be viewed via /settings.
