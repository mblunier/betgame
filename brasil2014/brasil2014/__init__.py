from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings

from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    RootFactory,
    groupfinder
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    session_factory = session_factory_from_settings(settings)

    authn_policy = AuthTktAuthenticationPolicy('s0secret', callback=groupfinder, hashalg='md5')
    #authn_policy = AuthTktAuthenticationPolicy('s0secret')
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        root_factory=RootFactory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        session_factory=session_factory
        )

    # since version 1.5 templating is not included by default
    config.include('pyramid_chameleon')

    config.add_static_view('static', 'brasil2014:static', cache_max_age=3600)
    config.include(addroutes)
    config.scan()

    return config.make_wsgi_app()


def addroutes(config):
    """ Define URL mappings.
    Note, that order is relevant as the first matching route will hide
    any following routes with the same initial pattern. 
    """
    config.add_route('about', '/about')
    config.add_route('help', '/help')
    config.add_route('home', '/')
    config.add_route('infoscreen', '/infoscreen')
    config.add_route('links', '/links')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('db_backup', '/backup/{table}')
    config.add_route('db_restore', '/restore')
    config.add_route('results', '/results')
    config.add_route('categories', '/categories')
    config.add_route('scoring', '/scoring')
    config.add_route('score_table', '/scoretable')
    config.add_route('settings', '/settings')
    config.add_route('system_info', '/sysinfo')
    config.add_route('too_late', '/too_late')
    config.add_route('unregister', '/unregister/{alias}')
    config.add_route('update_category', '/category/{name}/{value}')
    config.add_route('update_local', '/update_local')
    config.add_route('update_match', '/match/{id}/{team1}/{team2}')
    config.add_route('update_remote', '/update_remote')
    config.add_route('update_score', '/score/{id}/{score1}/{score2}')
    config.add_route('update_setting', '/setting/{name}/{value}')
    config.add_route('final_bet', '/bet/final')
    config.add_route('match_bet', '/bet/{match}')
    config.add_route('view_final_tips', '/final_tips')
    config.add_route('view_final_tip', '/final_tip/{player}')
    config.add_route('view_group_matches', '/group_matches/{group}')
    config.add_route('view_stage2_matches', '/stage2_matches')
    config.add_route('view_matches', '/matches')
    config.add_route('view_match_tips', '/match_tips/{match}')
    config.add_route('view_upcoming_matches', '/upcoming/{num}')
    config.add_route('view_players', '/players')
    config.add_route('view_group_players', '/group_players/{category}')
    config.add_route('view_group_teams', '/group_teams/{group}')
    config.add_route('view_player_groups', '/player_groups')
    config.add_route('view_player_tips', '/player_tips/{player}')
    config.add_route('view_team_groups', '/team_groups')
    config.add_route('view_teams', '/teams')
    config.add_route('view_tips', '/tips')

