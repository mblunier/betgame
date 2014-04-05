from datetime import datetime
from properties import (
    PROJECT_TITLE,
    #PLAYER_GROUPS,
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
    authenticated_userid, 
    remember, 
    forget
    )

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden
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
    MatchGroup,
    Final,
    Tip
    )

from scoring import (
    MatchTip,
    FinalTip,
    refresh_points,
    sign
    )

    
categories = [(c.d_alias, c.d_name) for c in Category.get_all()]


def get_page_param(request, param='page'):
    try:
        return int(request.params[param])
    except:
        return 1

def login_form_view(request):
    logged_in = authenticated_userid(request)
    return render('templates/login.pt',
                  { 'loggedin': logged_in },
                  request)

def navigation_view(request):
    return render('templates/navigation.pt',
                  { 'viewer_username': authenticated_userid(request),
                    'login_form': login_form_view(request) },
                  request)



@view_config(permission='view', route_name='home',
             renderer='templates/main.pt')
def view_game(request):
    return { 'project': PROJECT_TITLE,
             'final_deadline': FINAL_DEADLINE,
             'viewer_username': authenticated_userid(request),
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
             renderer='templates/scoretable.pt')
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
             'viewer_username': authenticated_userid(request),
             'navigation': navigation_view(request) }


# ----- player views -----

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
            headers = remember(request, alias)
            player = Player(alias=alias,
                            password=form.data['initial_password'],
                            name=form.data['name'],
                            mail=form.data['mail'],
                            unit=form.data['category'])
            DBSession().add(player)

            redirect_url = route_url('home', request)
            return HTTPFound(location=redirect_url, headers=headers)

    return { 'form': FormRenderer(form),
             'categories': categories,
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
            headers = remember(request, login)
            request.session.flash(u'Logged in successfully.')
            return HTTPFound(location=came_from, headers=headers)

    request.session.flash(u'Failed to login.')
    return HTTPFound(location=came_from)

@view_config(permission='post', route_name='logout')
def logout(request):
    request.session.invalidate()
    request.session.flash(u'Logged out successfully.')
    home = route_url('home', request)
    headers = forget(request)
    return HTTPFound(location=home, headers=headers)

@view_config(permission='view', route_name='view_players',
             renderer='templates/players.pt')
def view_players(request):
    viewer_username = authenticated_userid(request)
    url = webhelpers.paginate.PageURL_WebOb(request)
    page = get_page_param(request)
    players = webhelpers.paginate.Page(DBSession.query(Player).order_by(Player.d_points.desc(), Player.d_alias),
                                       page=page,
                                       url=url,
                                       items_per_page=15)
    #if not players:
    #    return HTTPNotFound('No players')
    return { 'players': players,
             'viewer_username': viewer_username,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_group_players',
             renderer='templates/group_players.pt')
def view_group_players(request):
    viewer_username = authenticated_userid(request)
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
             'viewer_username': viewer_username,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_player_groups',
             renderer='templates/player_groups.pt')
def view_player_groups(request):
    viewer_username = authenticated_userid(request)
    groups = Player.get_groups().all()
    if not groups:
        return HTTPNotFound('No player groups')
    # sort groups descending by the average number of points per player
    groups = sorted(groups, lambda g1,g2: sign((g1[3] / g1[2]) - (g2[3] / g2[2])), reverse=True)
    return { 'groups': groups,
             'viewer_username': viewer_username,
             'navigation': navigation_view(request) }


# ----- team/group views -----

@view_config(permission='view', route_name='view_teams',
             renderer='templates/teams.pt')
def view_teams(request):
    teams = DBSession.query(Team).all()
    return { 'teams': teams,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_team_groups',
             renderer='templates/group_teams.pt')
def view_team_groups(request):
    groups = [TeamGroup(group_id, Team.get_by_group(group_id)) for group_id in GROUP_IDS]
    return { 'groups': groups,
             'navigation': navigation_view(request) }


# ----- match views -----

@view_config(permission='view', route_name='view_matches',
             renderer='templates/matches.pt')
def view_matches(request):
    viewer_username = authenticated_userid(request)
    #matches = Match.get_played()
    matches = DBSession.query(Match).order_by(Match.d_begin).all()
    for match in matches:
        if match.d_id == FINAL_ID:
            final_tip = Final.get_player_tip(viewer_username)
            if final_tip:
                match.tip = Tip(viewer_username, FINAL_ID, final_tip.d_score1, final_tip.d_score2)
            else:
                match.tip = None
        else:
            match.tip = Tip.get_player_tip(viewer_username, match.d_id)
    return { 'now': datetime.now(),
             'matches': matches,
             'final_id': FINAL_ID,
             'final_deadline': FINAL_DEADLINE,
             'viewer_username': viewer_username,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_group_matches',
             renderer='templates/group_matches.pt')
def view_group_matches(request):
    viewer_username = authenticated_userid(request)
    group_id = request.matchdict['group']
    matches = Match.get_by_group(group_id).all()
    for match in matches:
        match.tip = Tip.get_player_tip(viewer_username, match.d_id)
    return { 'now': datetime.now(),
             'matches': matches,
             'viewer_username': viewer_username,
             'navigation': navigation_view(request) }


# ----- tip views -----

class MatchBetSchema(formencode.Schema):
    allow_extra_fields = True
    d_score1 = formencode.validators.Int(min=0, not_empty=True)
    d_score2 = formencode.validators.Int(min=0, not_empty=True)

@view_config(permission='post', route_name='match_bet',
             renderer='templates/match_bet.pt')
def match_bet(request):
    player_id = authenticated_userid(request)
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
             renderer='templates/tips.pt')
def view_tips(request):
    viewer_username = authenticated_userid(request)
    tips = DBSession.query(Tip).all()
    return { 'tips': tips,
             'viewer_username': viewer_username,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_match_tips',
             renderer='templates/match_tips.pt')
def view_match_tips(request):
    viewer_username = authenticated_userid(request)
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
             'viewer_username': viewer_username,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_player_tips',
             renderer='templates/player_tips.pt')
def view_player_tips(request):
    viewer_username = authenticated_userid(request)
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
             'viewer_username': viewer_username,
             'navigation': navigation_view(request) }


# ----- final views -----

class FinalBetSchema(formencode.Schema):
    allow_extra_fields = True
    d_team1 = formencode.validators.String(not_empty=True)
    d_team2 = formencode.validators.String(not_empty=True)
    d_score1 = formencode.validators.Int(min=0, not_empty=True)
    d_score2 = formencode.validators.Int(min=0, not_empty=True)

@view_config(permission='post', route_name='final_bet',
             renderer='templates/final_bet.pt')
def final_bet(request):
    player_id = authenticated_userid(request)
    final_tip = Final.get_player_tip(player_id)
    if final_tip:
        request.session.flash(u'You already entered a final tip.')
        return HTTPFound(location=route_url('view_final_tip', request, player=player_id))

    final_tip = Final(player_id)

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
        return HTTPFound(location=route_url('view_final_tip', request, player=player_id))

    teams = [(team.d_id,team.d_name) for team in DBSession.query(Team).order_by(Team.d_name)]

    return { 'tip': final_tip,
             'form': FormRenderer(form),
             'teams': teams,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_final_tips',
             renderer='templates/final_tips.pt')
def view_final_tips(request):
    viewer_username = authenticated_userid(request)
    final = Match.get_final()
    tips = [FinalTip(final, tip) for tip in DBSession.query(Final)]
    return { 'final': final,
             'tips': tips,
             'viewer_username': viewer_username,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_final_tip',
             renderer='templates/final_tip.pt')
def view_final_tip(request):
    player = request.matchdict['player']
    tip = Final.get_player_tip(player)
    return { 'tip': tip,
             'navigation': navigation_view(request) }


# ----- admin stuff -----

@view_config(permission='update', route_name='set_score')
def set_score(request):
    viewer_username = authenticated_userid(request)
    if viewer_username and viewer_username == 'mb':
        id = request.matchdict['id']
        score1 = request.matchdict['score1']
        score2 = request.matchdict['score2']
        try:
            match = Match.get_by_id(id)
            match.d_score1 = int(score1)
            match.d_score2 = int(score2)
            #session = DBSession()
            #session.add(match)
            #session.flush()
            refresh_points()
        except:
            pass
        return HTTPFound(location=route_url('view_matches', request))
    return HTTPForbidden("this function is reserved for the administrator!")

@view_config(permission='update', route_name='update')
def update(request):
    viewer_username = authenticated_userid(request)
    if viewer_username and viewer_username == 'mb':
        refresh_points()
        return HTTPFound(location=route_url('view_players', request))
    return HTTPForbidden("this function is reserved for the administrator!")
