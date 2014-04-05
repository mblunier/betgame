# -*- coding: utf-8 -*-

import os
import sys
import transaction

from datetime import datetime

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Team,
    Match,
    Final,
    Player,
    Category,
    Base
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    # register the 'admin' user
    with transaction.manager:
        DBSession.add(Player(alias="admin", password="None", name="Admin", mail="office@rolotec.ch", unit="Administration"))

    # player categories (org. units)
    with transaction.manager:
        DBSession.add(Category(alias="B+S",         name="Operation & Support"))
        DBSession.add(Category(alias="Marketing",   name="Marketing"))
        DBSession.add(Category(alias="Projects",    name="Projects"))
        DBSession.add(Category(alias="Products",    name="Products"))
        DBSession.add(Category(alias="QA",          name="Quality Assurance"))
        DBSession.add(Category(alias="Sales",       name="Sales"))
        DBSession.add(Category(alias="Security",    name="Information Security"))
        DBSession.add(Category(alias="Services",    name="Services"))
        DBSession.add(Category(alias="CltAppMob",   name="Client App. Mobile"))
        DBSession.add(Category(alias="CltAppNat",   name="Client App. Native"))
        DBSession.add(Category(alias="CltAppWeb",   name="Client App. Web"))
        DBSession.add(Category(alias="CntApp",      name="Content App."))
        DBSession.add(Category(alias="SrvAppDel",   name="Server App. Delivery"))
        DBSession.add(Category(alias="SrvAppCalc",  name="Server App. Calculation"))
        DBSession.add(Category(alias="SrvAppProc",  name="Server App. Processing"))
        DBSession.add(Category(alias="Terminals",   name="Payment Terminals"))

    # teams/groups
    with transaction.manager:
        DBSession.add(Team(id='BRA', name=u'Brazil',      group='A'))
        DBSession.add(Team(id='CRO', name=u'Croatia',     group='A'))
        DBSession.add(Team(id='MEX', name=u'Mexico',      group='A'))
        DBSession.add(Team(id='CMR', name=u'Cameroon',    group='A'))

        DBSession.add(Team(id='ESP', name=u'Spain',       group='B'))
        DBSession.add(Team(id='NED', name=u'Netherlands', group='B'))
        DBSession.add(Team(id='CHI', name=u'Chile',       group='B'))
        DBSession.add(Team(id='AUS', name=u'Australia',   group='B'))

        DBSession.add(Team(id='COL', name=u'Colombia',    group='C'))
        DBSession.add(Team(id='GRE', name=u'Greece',      group='C'))
        DBSession.add(Team(id='CIV', name=u'Côte d\'Ivoire',group='C'))
        DBSession.add(Team(id='JPN', name=u'Japan',       group='C'))

        DBSession.add(Team(id='URU', name=u'Uruguay',     group='D'))
        DBSession.add(Team(id='CRC', name=u'Costa Rica',  group='D'))
        DBSession.add(Team(id='ENG', name=u'England',     group='D'))
        DBSession.add(Team(id='ITA', name=u'Italy',       group='D'))

        DBSession.add(Team(id='SUI', name=u'Switzerland', group='E'))
        DBSession.add(Team(id='ECU', name=u'Ecuador',     group='E'))
        DBSession.add(Team(id='FRA', name=u'France',      group='E'))
        DBSession.add(Team(id='HON', name=u'Honduras',    group='E'))

        DBSession.add(Team(id='ARG', name=u'Argentina',   group='F'))
        DBSession.add(Team(id='BIH', name=u'Bosnia-Herzegowina',group='F'))
        DBSession.add(Team(id='IRN', name=u'Iran',        group='F'))
        DBSession.add(Team(id='NGA', name=u'Nigeria',     group='F'))

        DBSession.add(Team(id='GER', name=u'Germany',     group='G'))
        DBSession.add(Team(id='POR', name=u'Portugal',    group='G'))
        DBSession.add(Team(id='GHA', name=u'Ghana',       group='G'))
        DBSession.add(Team(id='USA', name=u'USA',         group='G'))

        DBSession.add(Team(id='BEL', name=u'Belgium',     group='H'))
        DBSession.add(Team(id='ALG', name=u'Algeria',     group='H'))
        DBSession.add(Team(id='RUS', name=u'Russia',      group='H'))
        DBSession.add(Team(id='KOR', name=u'Korea Rep.',  group='H'))

    # tournament schedule
    with transaction.manager:
        DBSession.add(Match(id= 1, begin=datetime(2014,6,12, 22,00), team1='BRA', team2='CRO'))
        DBSession.add(Match(id= 2, begin=datetime(2014,6,13, 18,00), team1='MEX', team2='CMR'))
        DBSession.add(Match(id= 3, begin=datetime(2014,6,13, 21,00), team1='ESP', team2='NED'))
        DBSession.add(Match(id= 4, begin=datetime(2014,6,14, 00,00), team1='CHI', team2='AUS'))
        DBSession.add(Match(id= 5, begin=datetime(2014,6,14, 18,00), team1='COL', team2='GRE'))
        DBSession.add(Match(id= 7, begin=datetime(2014,6,14, 21,00), team1='URU', team2='CRC'))
        DBSession.add(Match(id= 8, begin=datetime(2014,6,15, 10,00), team1='ENG', team2='ITA'))
        DBSession.add(Match(id= 6, begin=datetime(2014,6,15, 03,00), team1='CIV', team2='JPN'))
        DBSession.add(Match(id= 9, begin=datetime(2014,6,15, 18,00), team1='SUI', team2='ECU'))
        DBSession.add(Match(id=10, begin=datetime(2014,6,15, 21,00), team1='FRA', team2='HON'))
        DBSession.add(Match(id=11, begin=datetime(2014,6,16, 00,00), team1='ARG', team2='BIH'))
        DBSession.add(Match(id=13, begin=datetime(2014,6,16, 18,00), team1='GER', team2='POR'))
        DBSession.add(Match(id=12, begin=datetime(2014,6,16, 21,00), team1='IRN', team2='NGA'))
        DBSession.add(Match(id=14, begin=datetime(2014,6,17, 00,00), team1='GHA', team2='USA'))
        DBSession.add(Match(id=15, begin=datetime(2014,6,17, 18,00), team1='BEL', team2='ALG'))
        DBSession.add(Match(id=17, begin=datetime(2014,6,17, 21,00), team1='BRA', team2='MEX'))
        DBSession.add(Match(id=16, begin=datetime(2014,6,18, 00,00), team1='RUS', team2='KOR'))
        DBSession.add(Match(id=20, begin=datetime(2014,6,18, 18,00), team1='AUS', team2='NED'))
        DBSession.add(Match(id=19, begin=datetime(2014,6,18, 21,00), team1='ESP', team2='CHI'))
        DBSession.add(Match(id=18, begin=datetime(2014,6,18, 19,00), team1='CMR', team2='CRO'))
        DBSession.add(Match(id=21, begin=datetime(2014,6,19, 18,00), team1='COL', team2='CIV'))
        DBSession.add(Match(id=23, begin=datetime(2014,6,19, 21,00), team1='URU', team2='ENG'))
        DBSession.add(Match(id=22, begin=datetime(2014,6,20, 00,00), team1='JPN', team2='GRE'))
        DBSession.add(Match(id=24, begin=datetime(2014,6,20, 18,00), team1='ITA', team2='CRC'))
        DBSession.add(Match(id=25, begin=datetime(2014,6,20, 21,00), team1='SUI', team2='FRA'))
        DBSession.add(Match(id=26, begin=datetime(2014,6,21, 00,00), team1='HON', team2='ECU'))
        DBSession.add(Match(id=27, begin=datetime(2014,6,21, 18,00), team1='ARG', team2='IRN'))
        DBSession.add(Match(id=29, begin=datetime(2014,6,21, 21,00), team1='GER', team2='GHA'))
        DBSession.add(Match(id=28, begin=datetime(2014,6,22, 00,00), team1='NGA', team2='BIH'))
        DBSession.add(Match(id=31, begin=datetime(2014,6,22, 18,00), team1='BEL', team2='RUS'))
        DBSession.add(Match(id=32, begin=datetime(2014,6,22, 21,00), team1='KOR', team2='ALG'))
        DBSession.add(Match(id=30, begin=datetime(2014,6,23, 00,00), team1='USA', team2='POR'))
        DBSession.add(Match(id=35, begin=datetime(2014,6,23, 18,00), team1='AUS', team2='ESP'))
        DBSession.add(Match(id=36, begin=datetime(2014,6,23, 18,00), team1='NED', team2='CHI'))
        DBSession.add(Match(id=34, begin=datetime(2014,6,23, 22,00), team1='CRO', team2='MEX'))
        DBSession.add(Match(id=33, begin=datetime(2014,6,23, 22,00), team1='CMR', team2='BRA'))
        DBSession.add(Match(id=40, begin=datetime(2014,6,24, 18,00), team1='CRC', team2='ENG'))
        DBSession.add(Match(id=39, begin=datetime(2014,6,24, 18,00), team1='ITA', team2='URU'))
        DBSession.add(Match(id=37, begin=datetime(2014,6,24, 22,00), team1='JPN', team2='COL'))
        DBSession.add(Match(id=38, begin=datetime(2014,6,24, 22,00), team1='GRE', team2='CIV'))
        DBSession.add(Match(id=43, begin=datetime(2014,6,25, 18,00), team1='NGA', team2='ARG'))
        DBSession.add(Match(id=44, begin=datetime(2014,6,25, 18,00), team1='BIH', team2='IRN'))
        DBSession.add(Match(id=41, begin=datetime(2014,6,25, 22,00), team1='HON', team2='SUI'))
        DBSession.add(Match(id=42, begin=datetime(2014,6,25, 22,00), team1='ECU', team2='FRA'))
        DBSession.add(Match(id=46, begin=datetime(2014,6,26, 18,00), team1='POR', team2='GHA'))
        DBSession.add(Match(id=45, begin=datetime(2014,6,26, 18,00), team1='USA', team2='GER'))
        DBSession.add(Match(id=47, begin=datetime(2014,6,26, 22,00), team1='KOR', team2='BEL'))
        DBSession.add(Match(id=48, begin=datetime(2014,6,26, 22,00), team1='ALG', team2='RUS'))

        DBSession.add(Match(id=49, begin=datetime(2014,6,28, 18,00), team1= '1A', team2= '2B'))
        DBSession.add(Match(id=50, begin=datetime(2014,6,28, 22,00), team1= '1C', team2= '2D'))
        DBSession.add(Match(id=51, begin=datetime(2014,6,29, 18,00), team1= '1B', team2= '2A'))
        DBSession.add(Match(id=52, begin=datetime(2014,6,29, 22,00), team1= '1D', team2= '2C'))
        DBSession.add(Match(id=53, begin=datetime(2014,6,30, 18,00), team1= '1E', team2= '2F'))
        DBSession.add(Match(id=54, begin=datetime(2014,6,30, 22,00), team1= '1G', team2= '2H'))
        DBSession.add(Match(id=55, begin=datetime(2014,7,1,  18,00), team1= '1F', team2= '2E'))
        DBSession.add(Match(id=56, begin=datetime(2014,7,1,  22,00), team1= '1H', team2= '2G'))

        DBSession.add(Match(id=57, begin=datetime(2014,7,4,  22,00), team1='W49', team2='W50'))
        DBSession.add(Match(id=58, begin=datetime(2014,7,4,  18,00), team1='W53', team2='W54'))
        DBSession.add(Match(id=59, begin=datetime(2014,7,5,  22,00), team1='W51', team2='W52'))
        DBSession.add(Match(id=60, begin=datetime(2014,7,5,  18,00), team1='W55', team2='W56'))

        DBSession.add(Match(id=61, begin=datetime(2014,7,8,  22,00), team1='W57', team2='W58'))
        DBSession.add(Match(id=62, begin=datetime(2014,7,9,  22,00), team1='W59', team2='W60'))

        DBSession.add(Match(id=63, begin=datetime(2014,7,12, 22,00), team1='L61', team2='L62'))
        DBSession.add(Match(id=64, begin=datetime(2014,7,13, 21,00), team1='W61', team2='W62'))
