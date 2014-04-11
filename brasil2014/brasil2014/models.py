import cryptacular.bcrypt

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    func,
    )
from sqlalchemy.types import (
    DateTime,
    Integer,
    String,
    Unicode
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    synonym
    )
from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
    Everyone,
    Authenticated,
    Allow
    )

from properties import FINAL_DEADLINE, FINAL_ID, ADMINS

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

class RootFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'post'),
        (Allow, 'group:admins', 'update')
    ]

    def __init__(self, request):
        pass  # pragma: no cover

def groupfinder(userid, request):
    if userid in ADMINS:
        return ['group:admins']
    return []

def hash_password(password):
    return unicode(crypt.encode(password))

class Player(Base):
    __tablename__ = 't_player'
    d_alias = Column(String(10), primary_key=True)
    d_name = Column(Unicode(50), default=u'Anonymous')
    d_mail = Column(Unicode(50), nullable=True)
    d_unit = Column(String(10))
    d_points = Column(Integer)

    _password = Column('d_password', Unicode(60))

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    d_password = property(_get_password, _set_password)
    d_password = synonym('_password', descriptor=d_password)

    def __init__(self, alias, password, name, mail, unit):
        self.d_alias = alias
        self.d_password = password
        self.d_name = name
        self.d_mail = mail
        self.d_unit = unit
        self.d_points = 0

    @classmethod
    def check_password(cls, username, password):
        player = cls.get_by_username(username)
        if not player:
            return False
        return crypt.check(player.d_password, password)

    @classmethod
    def exists(cls, username):
        return DBSession.query(cls).filter(cls.d_alias == username).first() is not None

    @classmethod
    def get_by_username(cls, username):
        return DBSession.query(cls).filter(cls.d_alias == username).first()

    @classmethod
    def get_by_unit(cls, unit):
        return DBSession.query(cls).filter(cls.d_unit == unit).order_by(cls.d_points.desc())

    @classmethod
    def get_groups(cls):
        """ Retrieve player groups as a list of tuples: (d_unit, n_players, n_points) """
        return DBSession.query(cls, cls.d_unit, 
                               func.count(cls.d_alias).label('n_players'), 
                               func.sum(cls.d_points).label('n_points')).group_by(cls.d_unit)

    @classmethod
    def ranking(cls):
        return DBSession.query(cls).order_by(cls.d_points.desc(), cls.d_alias)


class Category(Base):
    __tablename__ = 't_category'
    d_alias = Column(String(20), primary_key=True)
    d_name = Column(Unicode(30))

    def __init__(self, alias, name):
        self.d_alias = alias
        self.d_name = name

    @classmethod
    def option_list(cls):
        return [(c.d_alias, c.d_name) for c in DBSession.query(cls).order_by(cls.d_name)]


class Team(Base):
    __tablename__ = 't_team'
    d_id = Column(String(3), primary_key=True)
    d_name = Column(Unicode(30))
    d_group = Column(String(1))
    d_played = Column(Integer, default=0)
    d_points = Column(Integer, default=0)
    d_shot = Column(Integer, default=0)
    d_rcvd = Column(Integer, default=0)

    def __init__(self, id, name, group):
        self.d_id = id
        self.d_name = name
        self.d_group = group
        self.d_played = 0
        self.d_points = 0
        self.d_shot = 0
        self.d_rcvd = 0

    @classmethod
    def get_all(cls):
        return DBSession.query(cls).order_by(cls.d_name)

    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).filter(cls.d_id == id).first()

    @classmethod
    def get_by_group(cls, group):
        return DBSession.query(cls).filter(cls.d_group == group).\
                                    order_by(cls.d_points.desc(), cls.d_shot.desc())


class TeamGroup:
    def __init__(self, id, teams=[]):
        """ Associate a list of teams with a group id. """
        self.group_id = id
        self.teams = teams


class Match(Base):
    __tablename__ = 't_match'
    d_id = Column(Integer, primary_key=True)
    d_begin = Column(DateTime)
    # the following constraints cannot be fulfilled:
    #d_team1 = Column(String(3), ForeignKey('t_team.d_id'))
    #d_team2 = Column(String(3), ForeignKey('t_team.d_id'))
    d_team1 = Column(String(3), nullable=False)
    d_team2 = Column(String(3), nullable=False)
    d_score1 = Column(Integer, nullable=True)
    d_score2 = Column(Integer, nullable=True)

    def __init__(self, id, begin, team1, team2, score1=None, score2=None):
        self.d_id = id
        self.d_begin = begin
        self.d_team1 = team1
        self.d_team2 = team2
        self.d_score1 = score1
        self.d_score2 = score2

    def __str__(self):
        return '{0} {1}:{2} {3}:{4}'.format(self.d_id, self.d_team1, self.d_team2, self.d_score1, self.d_score2)

    @classmethod
    def get_all(cls):
        return DBSession.query(cls).order_by(cls.d_begin).all()

    @classmethod
    def get_by_id(cls, match_id):
        return DBSession.query(cls).filter(cls.d_id == match_id).first()

    @classmethod
    def get_by_group(cls, group):
        group_teams = [team.d_id for team in Team.get_by_group(group)]
        return DBSession.query(cls).filter(cls.d_team1.in_(group_teams)).\
                                    filter(cls.d_team2.in_(group_teams)).\
                                    order_by(cls.d_begin)

    @classmethod
    def get_final(cls):
        """ Retrieve final match, but make sure it has already been played. """
        return DBSession.query(cls).filter(cls.d_id == FINAL_ID).first()    # .one()

    @classmethod
    def get_stage2(cls):
        """ Retrieve the list of stage 2 matches. """
        return DBSession.query(cls).filter(cls.d_begin >= FINAL_DEADLINE)

    @classmethod
    def get_played(cls):
        """ Retrieve the list of played matches. """
        return DBSession.query(cls).filter(cls.d_score1 != None).filter(cls.d_score2 != None)


class Tip(Base):
    __tablename__ = 't_tip'
    d_player = Column(String(10), ForeignKey('t_player.d_alias'), primary_key=True)
    d_match = Column(Integer, ForeignKey('t_match.d_id'), primary_key=True)
    d_score1 = Column(Integer, nullable=True)
    d_score2 = Column(Integer, nullable=True)

    def __init__(self, player, match, score1=None, score2=None):
        self.d_player = player
        self.d_match = match
        self.d_score1 = score1
        self.d_score2 = score2

    @classmethod
    def get_all(cls):
        return DBSession.query(cls).order_by(cls.d_player)

    @classmethod
    def get_match_tips(cls, match):
        return DBSession.query(cls).filter(cls.d_match == match).order_by(cls.d_player)

    @classmethod
    def get_player_tips(cls, player):
        return DBSession.query(cls).filter(cls.d_player == player)

    @classmethod
    def get_player_tip(cls, player, match):
        return DBSession.query(cls).filter(cls.d_player == player).\
                                    filter(cls.d_match == match).first()


class Final(Base):
    __tablename__ = 't_final'
    d_player = Column(String(10), ForeignKey('t_player.d_alias'), primary_key=True)
    d_team1 = Column(String(3), ForeignKey('t_team.d_id'))
    d_team2 = Column(String(3), ForeignKey('t_team.d_id'))
    d_score1 = Column(Integer, nullable=True)
    d_score2 = Column(Integer, nullable=True)

    def __init__(self, player, team1=None, team2=None, score1=None, score2=None):
        self.d_player = player
        self.d_team1 = team1
        self.d_team2 = team2
        self.d_score1 = score1
        self.d_score2 = score2

    @classmethod
    def get_all(cls):
        return DBSession.query(cls)

    @classmethod
    def get_player_tip(cls, player):
        return DBSession.query(cls).filter(cls.d_player == player).first()
