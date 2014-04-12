import json
import urllib2

from datetime import datetime
from properties import (
    PROJECT_TITLE,
    GAME_URL,
    RESULTPAGE,
    BET_POINTS, 
    FINAL_ID, 
    FINAL_DEADLINE, 
    GROUP_IDS 
    )

import webhelpers.paginate

from pyramid.response import Response

from pyramid.view import view_config
from pyramid.renderers import render
from pyramid.url import route_url

from pyramid.security import (
    remember, 
    forget
    )

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound
    )

import formencode
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Player,
    Category,
    Team,
    TeamGroup,
    Match,
    Final,
    Tip
    )

from scoring import (
    MatchTip,
    FinalTip,
    refresh_points,
    apply_results,
    sign
    )


def get_page_param(request, param='page'):
    """ @return Numerical value of the 'page' parameter. """
    try:
        return int(request.params[param])
    except:
        return 1

def login_form_view(request):
    return render('templates/login.pt',
                  { 'loggedin': request.authenticated_userid },
                  request)

def navigation_view(request):
    return render('templates/navigation.pt',
                  { 'viewer_username': request.authenticated_userid,
                    'login_form': login_form_view(request) },
                  request)

@view_config(permission='view', route_name='home',
             renderer='templates/main.pt')
def view_game(request):
    return { 'project': PROJECT_TITLE,
             'final_deadline': FINAL_DEADLINE,
             'game_url': GAME_URL,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='about',
             renderer='templates/about.pt')
def about_view(request):
    return { 'project': PROJECT_TITLE,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='help',
             renderer='templates/help.pt')
def help_view(request):
    return { 'project': PROJECT_TITLE,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='scoring',
             renderer='templates/scoring.pt')
def scoring_view(request):
    return { 'project': PROJECT_TITLE,
             'num_matches': DBSession.query(Match).count(),
             'scoring': BET_POINTS,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='score_table',
             renderer='templates/score_table.pt')
def score_table(request):
    match_scores = [(score1, score2) for score1 in range(0, 6) for score2 in range(score1, 6)]
    matches = [Match(0, datetime.now(), 'team1', 'team2', score1, score2) for (score1, score2) in match_scores]
    tip_scores = [(score1, score2) for score1 in range(0, 6) for score2 in range(0, 6)]
    tips = [Tip('none', 0, score1, score2) for (score1, score2) in tip_scores]
    match_tips = [MatchTip(match, tip) for match in matches for tip in tips]
    return { 'match_tips': match_tips,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='too_late',
             renderer='templates/too_late.pt')
def too_late(request):
    return { 'final_deadline': FINAL_DEADLINE,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }


# ----- Result/point update -----

@view_config(permission='view', route_name='results', renderer='json')
def results(request):
    """ Generate a list of scores for all played matches and the stage 2 team names. """
    matches = {}
    for match in Match.get_stage2():
        matches[match.d_id] = { "team1": match.d_team1, "team2": match.d_team2 }
    scores = {}
    for match in Match.get_played():
        scores[match.d_id] = { "score1": match.d_score1, "score2": match.d_score2 }
    return {'matches': matches,
            'scores': scores }

@view_config(permission='update', route_name='update_local')
def update_local(request):
    apply_results(results(request))
    return HTTPFound(location=route_url('view_players', request))

@view_config(permission='view', route_name='update_remote')
def update_remote(request):
    data = urllib2.urlopen(RESULTPAGE).read()
    apply_results(data)
    return HTTPFound(location=route_url('view_players', request))


# ----- Player views -----

class RegistrationSchema(formencode.Schema):
    allow_extra_fields = True
    alias = formencode.validators.PlainText(not_empty=True)
    name = formencode.validators.String(not_empty=True)
    mail = formencode.validators.Email(resolve_domain=False, not_empty=True)
    #category = formencode.validators.OneOf(categories, hideList=True)
    initial_password = formencode.validators.String(not_empty=True)
    confirm_password = formencode.validators.String(not_empty=True)
    chained_validators = [
        formencode.validators.FieldsMatch('initial_password', 'confirm_password')
    ]

@view_config(permission='view', route_name='register',
             renderer='templates/register.pt')
def add_player(request):
    form = Form(request, schema=RegistrationSchema)
    if 'form.submitted' in request.POST and form.validate():
        alias = form.data['alias']
        if (Player.exists(alias)):
            request.session.flash(u'Alias is already used, please choose another one.')
        else:
            player = Player(alias=alias,
                            password=form.data['initial_password'],
                            name=form.data['name'],
                            mail=form.data['mail'],
                            unit=form.data['category'])
            DBSession().add(player)
            headers = remember(request, alias)
            return HTTPFound(location=route_url('home', request), headers=headers)
    return { 'form': FormRenderer(form),
             'categories': Category.option_list(),
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='login')
def login(request):
    main_view = route_url('home', request)
    came_from = request.params.get('came_from', main_view)
    post_data = request.POST
    if 'submit' in post_data:
        login = post_data['alias']
        password = post_data['password']
        if Player.check_password(login, password):
            request.session.flash(u'Logged in successfully.')
            return HTTPFound(location=came_from, headers=remember(request, login))
        else:
            request.session.flash(u'Failed to login.')
    return HTTPFound(location=came_from)

@view_config(permission='post', route_name='logout')
def logout(request):
    request.session.invalidate()
    request.session.flash(u'Logged out successfully.')
    return HTTPFound(location=route_url('home', request), headers=forget(request))

@view_config(permission='view', route_name='view_players',
             renderer='templates/players.pt')
def view_players(request):
    url = webhelpers.paginate.PageURL_WebOb(request)
    page = get_page_param(request)
    players = webhelpers.paginate.Page(Player.ranking(),
                                       page=page,
                                       url=url,
                                       items_per_page=15)
    #if not players:
    #    return HTTPNotFound('No players')
    return { 'players': players,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_group_players',
             renderer='templates/group_players.pt')
def view_group_players(request):
    category = request.matchdict['category']
    page = get_page_param(request)
    url = webhelpers.paginate.PageURL_WebOb(request)
    players = webhelpers.paginate.Page(Player.get_by_unit(category),
                                       page=page,
                                       url=url,
                                       items_per_page=10)
    #if not players:
    #   return HTTPNotFound('No players in this category')
    # sort groups descending by the average number of points per player
    return { 'category': category,
             'players': players,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_player_groups',
             renderer='templates/player_groups.pt')
def view_player_groups(request):
    groups = Player.get_groups().all()
    if not groups:
        return HTTPNotFound('No player groups')
    # sort groups descending by the average number of points per player
    groups = sorted(groups, lambda g1,g2: sign((g1[3] / g1[2]) - (g2[3] / g2[2])), reverse=True)
    return { 'groups': groups,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }


# ----- Team/Group views -----

@view_config(permission='view', route_name='view_teams',
             renderer='templates/teams.pt')
def view_teams(request):
    return { 'teams': Team.get_all(),
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_team_groups',
             renderer='templates/group_teams.pt')
def view_team_groups(request):
    groups = [TeamGroup(group_id, Team.get_by_group(group_id)) for group_id in GROUP_IDS]
    return { 'groups': groups,
             'navigation': navigation_view(request) }


# ----- Match views -----

@view_config(permission='view', route_name='view_matches',
             renderer='templates/matches.pt', http_cache=0)
def view_matches(request):
    player = request.authenticated_userid
    #matches = Match.get_played()
    matches = Match.get_all()
    for match in matches:
        if match.d_id == FINAL_ID:
            final_tip = Final.get_player_tip(player)
            if final_tip:
                match.tip = Tip(player, FINAL_ID, final_tip.d_score1, final_tip.d_score2)
            else:
                match.tip = None
        else:
            match.tip = Tip.get_player_tip(player, match.d_id)
    return { 'now': datetime.now(),
             'matches': matches,
             'final_id': FINAL_ID,
             'final_deadline': FINAL_DEADLINE,
             'viewer_username': player,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_group_matches',
             renderer='templates/group_matches.pt', http_cache=0)
def view_group_matches(request):
    player = request.authenticated_userid
    group_id = request.matchdict['group']
    matches = Match.get_by_group(group_id).all()
    for match in matches:
        match.tip = Tip.get_player_tip(player, match.d_id)
    return { 'now': datetime.now(),
             'matches': matches,
             'viewer_username': player,
             'navigation': navigation_view(request) }


# ----- Tip views -----

class MatchBetSchema(formencode.Schema):
    allow_extra_fields = True
    d_score1 = formencode.validators.Int(min=0, not_empty=True)
    d_score2 = formencode.validators.Int(min=0, not_empty=True)

@view_config(permission='post', route_name='match_bet',
             renderer='templates/match_bet.pt')
def match_bet(request):
    player_id = request.authenticated_userid
    match_id = request.matchdict['match']
    match = Match.get_by_id(match_id)
    if match.d_begin < datetime.now():
        return HTTPFound(location=route_url('too_late', request))

    tip = Tip.get_player_tip(player_id, match_id)

    form = Form(request, schema=MatchBetSchema, obj=tip)
    if 'form.submitted' in request.POST and form.validate():
        session = DBSession()
        if not tip:
            tip = Tip(player=player_id, match=match_id)
            session.add(tip)
        tip.d_score1 = form.data['d_score1']
        tip.d_score2 = form.data['d_score2']
        return HTTPFound(location=route_url('view_match_tips', request, match=match_id))

    return { 'match': match,
             'tip': tip,
             'form': FormRenderer(form),
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_tips',
             renderer='templates/tips.pt', http_cache=0)
def view_tips(request):
    return { 'tips': Tip.get_all(),
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_match_tips',
             renderer='templates/match_tips.pt', http_cache=0)
def view_match_tips(request):
    match_id = request.matchdict['match']
    match = Match.get_by_id(match_id)
    match_tips = [MatchTip(match, tip) for tip in Tip.get_match_tips(match_id)]
    page = get_page_param(request)
    url = webhelpers.paginate.PageURL_WebOb(request)
    tips = webhelpers.paginate.Page(match_tips,
                                    page=page,
                                    url=url,
                                    items_per_page=10)
    return { 'match': match,
             'tips': tips,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_player_tips',
             renderer='templates/player_tips.pt', http_cache=0)
def view_player_tips(request):
    player_id = request.matchdict['player']
    player = Player.get_by_username(player_id)
    tips = []
    for tip in Tip.get_player_tips(player_id):
        match = Match.get_by_id(tip.d_match)
        tips.append(MatchTip(match, tip))
    final = Match.get_final()
    final_tip = Final.get_player_tip(player_id)
    if final and final_tip:
        tips.append(FinalTip(final, final_tip))
    return { 'player': player,
             'tips': tips,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }


# ----- Final views -----

class FinalBetSchema(formencode.Schema):
    allow_extra_fields = True
    d_team1 = formencode.validators.String(not_empty=True)
    d_team2 = formencode.validators.String(not_empty=True)
    d_score1 = formencode.validators.Int(min=0, not_empty=True)
    d_score2 = formencode.validators.Int(min=0, not_empty=True)

@view_config(permission='post', route_name='final_bet',
             renderer='templates/final_bet.pt')
def final_bet(request):
    player = request.authenticated_userid
    final_tip = Final.get_player_tip(player)
    if final_tip:
        request.session.flash(u'You already entered a final tip.')
        return HTTPFound(location=route_url('view_final_tip', request, player=player))

    final_tip = Final(player)

    form = Form(request, schema=FinalBetSchema, obj=final_tip)
    if 'form.submitted' in request.POST and form.validate():
        # verify, that the tip was entered on time
        if FINAL_DEADLINE < datetime.now():
            return HTTPFound(location=route_url('too_late', request))
        final_tip.d_team1 = form.data['d_team1']
        final_tip.d_team2 = form.data['d_team2']
        final_tip.d_score1 = form.data['d_score1']
        final_tip.d_score2 = form.data['d_score2']
        DBSession().add(final_tip)
        return HTTPFound(location=route_url('view_final_tip', request, player=player))

    teams = [(team.d_id,team.d_name) for team in Team.get_all()]

    return { 'tip': final_tip,
             'form': FormRenderer(form),
             'teams': teams,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_final_tips',
             renderer='templates/final_tips.pt', http_cache=0)
def view_final_tips(request):
    final = Match.get_final()
    tips = [FinalTip(final, tip) for tip in Final.get_all()]
    return { 'final': final,
             'tips': tips,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_final_tip',
             renderer='templates/final_tip.pt', http_cache=0)
def view_final_tip(request):
    player = request.matchdict['player']
    tip = Final.get_player_tip(player)
    return { 'tip': tip,
             'navigation': navigation_view(request) }


# ----- Admin stuff -----

@view_config(permission='update', route_name='set_match')
def set_match(request):
    try:
        match = Match.get_by_id(request.matchdict['id'])
        if match:
            if match.d_begin < FINAL_DEADLINE: 
                request.session.flash(u'Cannot update group stage matches.')
            else:
                match.d_team1 = request.matchdict['team1']
                match.d_team2 = request.matchdict['team2']
        else:
            request.session.flash(u'Invalid match id.')
        return HTTPFound(location=route_url('view_matches', request))
    except:
        request.session.flash(u'Updating match teams failed.')
        return HTTPFound(location=route_url('home', request))

@view_config(permission='update', route_name='set_score')
def set_score(request):
    try:
        match = Match.get_by_id(request.matchdict['id'])
        if match:
            match.d_score1 = int(request.matchdict['score1'])
            match.d_score2 = int(request.matchdict['score2'])
            #refresh_points()
        else:
            request.session.flash(u'Invalid match id.')
        return HTTPFound(location=route_url('view_matches', request))
    except:
        request.session.flash(u'Updating score and points failed.')
        return HTTPFound(location=route_url('home', request))

