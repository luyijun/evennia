
"""
This file contains the generic, assorted views that don't fall under one of
the other applications. Views are django's way of processing e.g. html
templates on the fly.

"""
from django.contrib.admin.sites import site
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from src.objects.models import ObjectDB
from src.players.models import PlayerDB

_BASE_CHAR_TYPECLASS = settings.BASE_CHARACTER_TYPECLASS


def page_index(request):
    """
    Main root page.
    """
    # Some misc. configurable stuff.
    # TODO: Move this to either SQL or settings.py based configuration.
    fpage_player_limit = 4

    # A QuerySet of the most recently connected players.
    recent_connected = PlayerDB.objects.get_recently_connected_players()
    recent_users = recent_connected[:fpage_player_limit]
    nplyrs_conn_recent = len(recent_connected) or "0"
    nplyrs = PlayerDB.objects.num_total_players() or "0"
    nplyrs_reg_recent = len(PlayerDB.objects.get_recently_created_players()) or "0"
    nsess = len(PlayerDB.objects.get_connected_players()) or "0"

    nobjs = ObjectDB.objects.all().count()
    nrooms = ObjectDB.objects.filter(db_location__isnull=True).exclude(db_typeclass_path=_BASE_CHAR_TYPECLASS).count()
    nexits = ObjectDB.objects.filter(db_location__isnull=False, db_destination__isnull=False).count()
    nchars = ObjectDB.objects.filter(db_typeclass_path=_BASE_CHAR_TYPECLASS).count()
    nothers = nobjs - nrooms - nchars - nexits

    pagevars = {
        "page_title": "Front Page",
        "players_connected_recent": recent_users,
        "num_players_connected": nsess or "0",
        "num_players_registered": nplyrs or "0",
        "num_players_connected_recent": nplyrs_conn_recent or "0",
        "num_players_registered_recent": nplyrs_reg_recent or "0",
        "num_rooms": nrooms or "0",
        "num_exits": nexits or "0",
        "num_objects" : nobjs or "0",
        "num_characters": nchars or "0",
        "num_others": nothers or "0"
    }

    return render(request, 'evennia_general/index.html', pagevars)


def to_be_implemented(request):
    """
    A notice letting the user know that this particular feature hasn't been
    implemented yet.
    """

    pagevars = {
        "page_title": "To Be Implemented...",
    }

    return render(request, 'evennia_general/tbi.html', pagevars)


@staff_member_required
def evennia_admin(request):
    """
    Helpful Evennia-specific admin page.
    """
    return render(
        request, 'evennia_general/evennia_admin.html', {
            'playerdb': PlayerDB})


def admin_wrapper(request):
    """
    Wrapper that allows us to properly use the base Django admin site, if needed.
    """
    return staff_member_required(site.index)(request)