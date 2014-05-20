import json

from datetime import datetime
from properties import (
    FINAL_DEADLINE
    )

from .models import (
    DBSession,
    Setting,
    Team,
    Player,
    Rank,
    Final,
    Match,
    Tip
    )

import logging
log = logging.getLogger(__name__)

# list of predefined scorings
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

sign = lambda num: cmp(num, 0)

def get_betpoints(table):
    log.info('===== retrieving betpoints from table "%s"...', str(table) if table else 'settings')
    try:
        return {
                'exacthit': int(Setting.get('scoring_exacthit').d_value),
                'goaldiff': int(Setting.get('scoring_goaldiff').d_value),
                'missed': int(Setting.get('scoring_missed').d_value),
                'onefinalist': int(Setting.get('scoring_onefinalist').d_value),
                'onescore': int(Setting.get('scoring_onescore').d_value),
                'outcome': int(Setting.get('scoring_outcome').d_value),
                'sumgoals': int(Setting.get('scoring_sumgoals').d_value),
                'twofinalists': int(Setting.get('scoring_twofinalists').d_value)
               } if table is None else SCORINGS[int(table)]
    except:
        log.error('===== ...failed, using hard-coded table"')
        return SCORINGS[6]

BET_POINTS = None

def reload_betpoints(table=None):
    global BET_POINTS
    BET_POINTS = get_betpoints(table)

reload_betpoints()


class MatchTip:
    """ Associate a match tip with the respective match and calculate the resulting points. """
    def __init__(self, match, tip):
        self.match = match
        self.tip = tip
        self.points = evaluate_match_tip(match, tip)


class FinalTip:
    """ Associate a final tip with the respective match and calculate the resulting points. """
    def __init__(self, final, tip):
        self.match = final
        self.tip = tip
        self.points = evaluate_final_tip(final, tip)


def scoring_MB(initial, match, tip):
    """ Calculate score points the traditional way. """
    points = 0
    if (tip.d_score1 + tip.d_score2) == (match.d_score1 + match.d_score2):
       points += BET_POINTS['sumgoals']
    if abs(tip.d_score1 - tip.d_score2) == abs(match.d_score1 - match.d_score2):
       points += BET_POINTS['goaldiff']
    if tip.d_score1 in [match.d_score1, match.d_score2]:
       points += BET_POINTS['onescore']
    if tip.d_score2 in [match.d_score1, match.d_score2]:
       points += BET_POINTS['onescore']
    return points


def scoring_NO(initial, match, tip):
    """ Calculate score points the new way. """
    diff1 = abs(match.d_score1 - tip.d_score1)
    diff2 = abs(match.d_score2 - tip.d_score2)
    return initial + (match.d_score1 + match.d_score2) - (diff1 + diff2) * BET_POINTS['onescore']


def scoring_NO2(initial, match, tip):
    """ Calculate score points the newer way. """
    diff = abs(sign(match.d_score1 - match.d_score2) + sign(tip.d_score1 - tip.d_score2))
    return initial + diff * BET_POINTS['onescore']


# select the scoring function
scoring = scoring_NO


def evaluate_match_tip(match, tip):
    """ Calculate score points for a single match. """
    if match.d_score1 is None or match.d_score2 is None:
        # match has not been played yet
        return 0

    if tip.d_score1 is None or tip.d_score2 is None:
        # the tip is invalid (this shouldn't occur)
        log.error('invalid tip: player %s, match %d (%s:%s)', 
                   tip.d_player, tip.d_match, tip.d_score1, tip.d_score2)
        return 0

    if match.d_score1 == tip.d_score1 and match.d_score2 == tip.d_score2:
        return scoring(BET_POINTS['exacthit'], match, tip)
    elif sign(match.d_score1 - match.d_score2) == sign(tip.d_score1 - tip.d_score2):
        return scoring(BET_POINTS['outcome'], match, tip)
    else:
        return scoring(BET_POINTS['missed'], match, tip)


def evaluate_final_tip(final, final_tip):
    """ Calculate score points for the final team bet. """
    finalists = 0
    if final_tip.d_team1 in [final.d_team1, final.d_team2]:
        finalists += 1
    if final_tip.d_team2 in [final.d_team1, final.d_team2]:
        finalists += 1
    if finalists == 1:
        points = BET_POINTS['onefinalist']
    elif finalists == 2:
        points = BET_POINTS['twofinalists']
    else:
        points = 0

    match = Match(final.d_id, begin=final.d_begin,
                  team1=final.d_team1, team2=final.d_team2, 
                  score1=final.d_score1, score2=final.d_score2)
    tip = Tip(player=final_tip.d_player, match=final.d_id,
              score1=final_tip.d_score1, score2=final_tip.d_score2)
    return points + evaluate_match_tip(match, tip)


def update_ranking():
    """ Update the rank table by grouping number of players having the same number of points. """
    # empty table
    num = Rank.delete_all()
    log.info('===== deleted %d ranks', num)

    rank = None
    for player in Player.ranking():
        if rank is None or player.d_points != rank.d_points:
            rank = Rank(rank.d_position + rank.d_players if rank else 1, player.d_points)
            DBSession.add(rank)
        rank.add_player()

def refresh_points():
    """ Update the points for all teams and players at once. """

    log.info('===== updating all points & scores')

    def find_team(team_id, teams):
        """ Find a team in a list of teams. """
        for team in teams:
            if team.d_id == team_id:
                return team
        return None

    # retrieve all teams to clear their points & scores
    teams = Team.get_all()
    for team in teams:
        team.d_played = 0
        team.d_points = 0
        team.d_shot = 0
        team.d_rcvd = 0

    def find_player(player_id, players):
        """ Find a player in a list of players. """
        for player in players:
            if player.d_alias == player_id:
                return player
        return None

    log.info('===== ...evaluating final tips')
    final = Match.get_final()

    # retrieve all players to initialize their points,
    # apply the final tip immediately, if present and
    # the final result is available
    players = Player.get_all()
    for player in players:
        player.d_points = 0
        final_tip = Final.get_player_tip(player.d_alias)
        if final:
            if final_tip:
                player.d_points = evaluate_final_tip(final, final_tip)
                log.info('player "%s" scored %d points for final tip %s:%s %s:%s (%s:%s %s:%s)',
                          player.d_alias, player.d_points,
                          final_tip.d_team1, final_tip.d_team2,
                          final_tip.d_score1, final_tip.d_score2,
                          final.d_team1, final.d_team2,
                          final.d_score1, final.d_score2)
            elif datetime.now() >= FINAL_DEADLINE:
                # player forgot to enter a final bet...
                log.warn('player "%s" forgot to enter a final tip', player.d_alias)
        else:   
            # the final has not been played yet...
            log.info('player "%s" has not yet entered a final tip (%s:%s %s:%s)',
                      player.d_alias,
                      final.d_team1, final.d_team2,
                      final.d_score1, final.d_score2)

        log.debug('player "%s" starts with %d points', 
                   player.d_alias, player.d_points)

    log.info('===== ...applying scores to stage 1 matches')
    for match in Match.get_played():
        # update all team points & scores for stage 1 matches
        if match.d_begin < FINAL_DEADLINE:
            log.debug('match %d (%s:%s) with score %d:%d --> updating team scores', 
                       match.d_id, match.d_team1, match.d_team2, 
                       match.d_score1, match.d_score2)
            team1 = find_team(match.d_team1, teams)
            team1.d_played += 1
            team1.d_shot += match.d_score1
            team1.d_rcvd += match.d_score2
            team2 = find_team(match.d_team2, teams)
            team2.d_played += 1
            team2.d_shot += match.d_score2
            team2.d_rcvd += match.d_score1
            if match.d_score1 > match.d_score2:
                # home team wins
                team1.d_points += 3
            elif match.d_score1 < match.d_score2:
                # away team wins
                team2.d_points += 3
            else:
                # draw
                team1.d_points += 1
                team2.d_points += 1
        else:
            log.debug('match %d (%s:%s) starts after %s --> skip team update', 
                       match.d_id, match.d_team1, match.d_team2, FINAL_DEADLINE)

        # the final tip has already been evaluated
        if final and match is final:
            log.debug('skipping final match %d (%s:%s)', 
                       match.d_id, match.d_team1, match.d_team2)
            continue

        # evaluate all player tips for the current match
        for tip in Tip.get_match_tips(match.d_id):
            player = find_player(tip.d_player, players)
            if player:
                tip_points = evaluate_match_tip(match, tip)
                log.debug('player "%s" tip %s:%s for match %d (%s:%s) with score %d:%d --> %d points', 
                           player.d_alias, tip.d_score1, tip.d_score2, 
                           match.d_id, match.d_team1, match.d_team2, 
                           match.d_score1, match.d_score2,
                           tip_points)
                player.d_points += tip_points
            else:
                # a tip from an unknown player?!
                log.error('unknown player "%s" entered tip (%s:%s) for match %d, %s:%s',
                           tip.d_player, tip.d_score1, tip.d_score2,
                           match.d_id, match.d_team1, match.d_team2)

    log.info('===== updated all points & scores')

    update_ranking()
    log.info('===== updated ranking')

def apply_results(data):
    """ Process the output generated by a 'results' view. """
    result = json.loads(data)
    matches = result['matches']
    scores = result['scores']
    for id, team in matches.iteritems():
        match = Match.get_by_id(id)
        if match:
            log.debug("apply_result: match %s = %s : %s", id, team['team1'], team['team2'])
            match.d_team1 = team['team1']
            match.d_team2 = team['team2']
    for id, score in scores.iteritems():
        match = Match.get_by_id(id)
        if match:
            log.debug("apply_result: score %s = %s : %s", id, score['score1'], score['score2'])
            match.d_score1 = int(score['score1'])
            match.d_score2 = int(score['score2'])
    log.debug("apply_result: %d scores", len(scores))
    if len(scores) > 0:
        refresh_points()

