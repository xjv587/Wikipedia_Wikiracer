import random
import sys
from typing import Callable, Iterator
from itertools import chain
from collections import defaultdict
from types import ModuleType
from importlib import reload
from urllib.request import urlopen

import pytest
from py_wikiracer.internet import Internet
from py_wikiracer.wikiracer import Parser, BFSProblem, DFSProblem, DijkstrasProblem, ASTARProblem, WikiracerProblem


def test_parser():
    internet = Internet()
    html = internet.get_page("/wiki/Henry_Krumrey")
    assert Parser.get_links_in_page(html) == ['/wiki/Main_Page',
                                              '/wiki/Henry_Krumrey',
                                              '/wiki/Wisconsin_State_Senate',
                                              '/wiki/Wisconsin_Senate,_District_20',
                                              '/wiki/Wisconsin_State_Assembly',
                                              '/wiki/Plymouth,_Sheboygan_County,_Wisconsin',
                                              '/wiki/Republican_Party_(United_States)',
                                              '/wiki/Sheboygan_County,_Wisconsin',
                                              '/wiki/United_States_presidential_election_in_Wisconsin,_1900',
                                              '/wiki/Crystal_Lake,_Illinois']


def test_trivial():
    """
    All pages contain a link to themselves, which any search algorithm should recognize.
    """
    bfs_internet = Internet()
    bfs = BFSProblem(bfs_internet)

    dfs_internet = Internet()
    dfs = DFSProblem(dfs_internet)

    dij_internet = Internet()
    dij = DijkstrasProblem(dij_internet)

    assert bfs.bfs(source = "/wiki/ASDF", goal = "/wiki/ASDF") == ["/wiki/ASDF", "/wiki/ASDF"]
    assert dfs.dfs(source = "/wiki/ASDF", goal = "/wiki/ASDF") == ["/wiki/ASDF", "/wiki/ASDF"]
    assert dij.dijkstras(source = "/wiki/ASDF", goal = "/wiki/ASDF") == ["/wiki/ASDF", "/wiki/ASDF"]

    assert bfs_internet.requests == ["/wiki/ASDF"]
    assert dfs_internet.requests == ["/wiki/ASDF"]
    assert dij_internet.requests == ["/wiki/ASDF"]


def test_trivial_2():
    """
    Searches going to page 1 distance away.
    """
    bfs_internet = Internet()
    bfs = BFSProblem(bfs_internet)

    dfs_internet = Internet()
    dfs = DFSProblem(dfs_internet)

    dij_internet = Internet()
    dij = DijkstrasProblem(dij_internet)

    assert bfs.bfs(source = "/wiki/Reese_Witherspoon", goal = "/wiki/Academy_Awards") == ["/wiki/Reese_Witherspoon", "/wiki/Academy_Awards"]
    assert dfs.dfs(source = "/wiki/Reese_Witherspoon", goal = "/wiki/Academy_Awards") == ["/wiki/Reese_Witherspoon", "/wiki/Academy_Awards"]
    assert dij.dijkstras(source = "/wiki/Reese_Witherspoon", goal = "/wiki/Academy_Awards") == ["/wiki/Reese_Witherspoon", "/wiki/Academy_Awards"]

    assert bfs_internet.requests == ["/wiki/Reese_Witherspoon"]
    assert dfs_internet.requests == ["/wiki/Reese_Witherspoon"]
    assert dij_internet.requests == ["/wiki/Reese_Witherspoon"]


def test_bfs_basic():
    """
    BFS depth 2 search
    """
    bfs_internet = Internet()
    bfs = BFSProblem(bfs_internet)
    res = bfs.bfs(source="/wiki/Potato_chip", goal="/wiki/Staten_Island")
    assert res == ["/wiki/Potato_chip", '/wiki/Saratoga_Springs,_New_York', "/wiki/Staten_Island"]
    assert bfs_internet.requests == ['/wiki/Potato_chip', '/wiki/Main_Page', '/wiki/French_fries',
                                     '/wiki/United_Kingdom', '/wiki/North_American_English', '/wiki/Australian_English',
                                     '/wiki/British_English', '/wiki/Irish_English', '/wiki/Potato', '/wiki/Deep_frying',
                                     '/wiki/Baking', '/wiki/Air_frying', '/wiki/Snack', '/wiki/Side_dish',
                                     '/wiki/Appetizer', '/wiki/Edible_salt', '/wiki/Herbs', '/wiki/Spice', '/wiki/Cheese',
                                     '/wiki/Artificial_flavors', '/wiki/Food_additive', '/wiki/Snack_food',
                                     '/wiki/William_Kitchiner', '/wiki/Mary_Randolph', '/wiki/Saratoga_Springs,_New_York']


def test_dfs_basic():
    """
    DFS depth 2 search
    """
    dfs_internet = Internet()
    dfs = DFSProblem(dfs_internet)
    res = dfs.dfs(source = "/wiki/Calvin_Li", goal = "/wiki/Microsoft_Bing")
    assert res == ['/wiki/Calvin_Li', '/wiki/Tencent_Weibo', '/wiki/XMPP', '/wiki/Yammer', '/wiki/Microsoft_Bing']
    assert dfs_internet.requests == ['/wiki/Calvin_Li', '/wiki/Tencent_Weibo', '/wiki/XMPP', '/wiki/Yammer']


def test_dijkstras_basic():
    """
    Dijkstra's depth 2 search
    """
    dij_internet = Internet()
    dij = DijkstrasProblem(dij_internet)
    # This costFn is to make sure there are never any ties coming out of the heap, since the default costFn produces ties and we don't define a tiebreaking mechanism for priorities
    assert dij.dijkstras(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia") == ['/wiki/Calvin_Li', '/wiki/Chinese_language', '/wiki/Wikipedia']
    assert dij_internet.requests == ['/wiki/Calvin_Li', '/wiki/Weibo', '/wiki/Hubei', '/wiki/Wuxia', '/wiki/Wuhan', '/wiki/Pinyin', '/wiki/Tencent', '/wiki/Wu_Yong', '/wiki/Cao_Cao', '/wiki/John_Woo', '/wiki/Kelly_Lin', '/wiki/Sina_Corp', '/wiki/Huo_Siyan', '/wiki/Shawn_Yue', '/wiki/Main_Page']


def test_astar_basic():
    a_internet = Internet()
    astar = ASTARProblem(a_internet)
    assert astar.astar(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia") == ['/wiki/Calvin_Li', '/wiki/Chinese_language', '/wiki/Wikipedia']


class CustomInternet:
    def __init__(self):
        self.requests = []

    def get_page(self, page):
        self.requests.append(page)
        return f'<a href="{page}"></a>'


def test_none_on_fail():
    """
    Program should return None on failure
    """
    # Override the internet to inject our own HTML
    bfs_internet = CustomInternet()
    bfs = BFSProblem(bfs_internet)

    dfs_internet = CustomInternet()
    dfs = DFSProblem(dfs_internet)

    dij_internet = CustomInternet()
    dij = DijkstrasProblem(dij_internet)

    assert bfs.bfs(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia") == None
    assert dfs.dfs(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia") == None
    assert dij.dijkstras(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia") == None

    assert bfs_internet.requests == ["/wiki/Calvin_Li"]
    assert dfs_internet.requests == ["/wiki/Calvin_Li"]
    assert dij_internet.requests == ["/wiki/Calvin_Li"]


def test_dfs_complex():
    """
    A complex DFS example to test your searching algorithm.
    """
    dfs_internet = Internet()
    dfs = DFSProblem(dfs_internet)
    res = dfs.dfs(source="/wiki/John_Wick", goal="/wiki/World_War_II")
    expected = [
        '/wiki/John_Wick', '/wiki/Klaatu_(The_Day_the_Earth_Stood_Still)',
        '/wiki/John_Wick_(comic)', '/wiki/The_Last_Barfighter',
        '/wiki/John_Wick_(character)',
        '/wiki/The_Day_the_Earth_Stood_Still_(2008_film)',
        '/wiki/Scott_Derrickson%27s_unrealized_projects', '/wiki/The_Gorge_(film)',
        '/wiki/Jon_Weinbach', '/wiki/Amy_Hennig', '/wiki/John_Lasseter',
        '/wiki/Don_Granger', '/wiki/IMDb_(identifier)', '/wiki/Amazon_Labor_Union',
        '/wiki/Amazon_Vine', '/wiki/Congress_of_Essential_Workers',
        '/wiki/Amazon_worker_organization', '/wiki/Statistically_improbable_phrase',
        '/wiki/Computational_linguistics', '/wiki/Outline_of_computer_science',
        '/wiki/Document_management_system', '/wiki/Curlie', '/wiki/AOL_TV',
        '/wiki/TOC_protocol', '/wiki/Socialthing', '/wiki/Singingfish',
        '/wiki/AOL_Seed', '/wiki/Radio_KOL_(Kids_Online)', '/wiki/AOL_Radio',
        '/wiki/Zune_software', '/wiki/WWE_Classics_on_Demand',
        '/wiki/Windows_Media_Center', '/wiki/Microsoft_Minesweeper',
        '/wiki/Microsoft_Mahjong', '/wiki/Hover!', '/wiki/Windows_File_Manager',
        '/wiki/DVD_Player_(Windows)', '/wiki/Comparison_of_DVR_software_packages',
        '/wiki/Video_player_(software)', '/wiki/Comparison_of_portable_media_players',
        '/wiki/Comparison_of_iPod_Managers', '/wiki/Dock_connector',
        '/wiki/Common_external_power_supply', '/wiki/IEC_62700', '/wiki/ATX',
        '/wiki/Small_Form_Factor_Special_Interest_Group', '/wiki/Mobile-ITX',
        '/wiki/Computer_hardware', '/wiki/Runt_pulse', '/wiki/Threshold_voltage',
        '/wiki/ISBN_(identifier)', '/wiki/World_Book_Capital', '/wiki/The_Philobiblon',
        '/wiki/World_Book_Day', '/wiki/Preservation_(library_and_archive)',
        '/wiki/Outline_of_books', '/wiki/Novel', '/wiki/World_War_II'
    ]
    assert res == expected
    assert len(dfs_internet.requests) == len(expected)-1
    assert dfs_internet.requests == expected[:-1]


def test_wikiracer_basic_1():
    """
    Tests wikiracer speed on one input.
    A great implementation can do this in less than 8 internet requests.
    A good implementation can do this in less than 15 internet requests.
    A mediocre implementation can do this in less than 30 internet requests.

    To make your own test cases like this, I recommend finding a starting page,
    clicking on a few links, and then seeing if your program can get from your
    start to your end in only a few downloads.
    """
    limit = 8

    racer_internet = Internet()
    racer = WikiracerProblem(racer_internet)
    racer.wikiracer(source="/wiki/Computer_science", goal="/wiki/Richard_Soley")
    assert len(racer_internet.requests) <= limit


def test_wikiracer_basic_2():
    """
    Tests wikiracer speed on one input.
    A great implementation can do this in less than 25 internet requests.
    A good implementation can do this in less than 80 internet requests.
    A mediocre implementation can do this in less than 300 internet requests.
    """
    limit = 25

    racer_internet = Internet()
    racer = WikiracerProblem(racer_internet)
    res = racer.wikiracer(source="/wiki/Waakirchen", goal="/wiki/Australasian_Virtual_Herbarium")
    assert len(racer_internet.requests) <= limit