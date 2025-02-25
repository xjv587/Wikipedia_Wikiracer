from py_wikiracer.internet import Internet
from typing import List, Callable
from collections import deque
from html.parser import HTMLParser
import heapq
import re
import time
import math

class Parser:

    @staticmethod
    def get_links_in_page(html: str) -> List[str]:
        links = []
        disallowed = Internet.DISALLOWED
        link_pattern = r'<a\s+href="/wiki/([^"#?]+)"'
        link_matches = re.findall(link_pattern, html)

        for link in link_matches:
            if not any(disallowed_char in link for disallowed_char in disallowed):
                links.append(f"/wiki/{link}")

        unique_links = []
        for link in links:
            if link not in unique_links:
                unique_links.append(link)

        return unique_links

class BFSProblem:
    def __init__(self, internet: Internet):
        self.internet = internet

    def bfs(self, source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia"):
        queue = deque()
        visited = set()
        parent = {}
        queue.append(source)
        visited.add(source)

        while queue:
            if source == goal:
                self.internet.get_page(source)
                return [source, goal]

            current_page = queue.popleft()
            page_html = self.internet.get_page(current_page)
            links_on_page = Parser.get_links_in_page(page_html)
            for link in links_on_page:
                if link not in visited:
                    visited.add(link)
                    parent[link] = current_page
                    queue.append(link)
                    if link == goal:
                        path = [link]
                        while current_page != source:
                            path.insert(0, current_page)
                            current_page = parent[current_page]
                        path.insert(0, source)
                        return path

        return None

class DFSProblem:
    def __init__(self, internet: Internet):
        self.internet = internet
        self.at_time = None

    def dfs(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):
        stack = [source]
        visited = set()
        parent = {}
        start_time = time.time()

        while stack and (time.time() - start_time) < 100:
            if source == goal:
                self.internet.get_page(source)
                return [source, goal]

            current_page = stack[-1]

            if current_page not in visited:
                visited.add(current_page)
                page_html = self.internet.get_page(current_page)
                links_on_page = Parser.get_links_in_page(page_html)
                unvisited_links = [link for link in links_on_page if link not in visited]

                if unvisited_links:
                    stack.extend(unvisited_links)
                    for link in unvisited_links:
                        parent[link] = current_page
                        if link == goal:
                            path = [link]
                            p = parent[link]
                            while p != source:
                                path.insert(0, p)
                                p = parent[p]
                                stack.pop()
                            path.insert(0, source)
                            return path
                else:
                    stack.pop()
            else:
                stack.pop()
        return None

class DijkstrasProblem:
    def __init__(self, internet: Internet):
        self.internet = internet
        # Dijkstras can pass wikiracer_basic_1 <= 8, but can't pass wikiracer_basic_2 <= 300

    def dijkstras(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):
        heap = [(0, source)]
        visited = set()
        visited.add(source)
        cost = {source: 0}
        parents = {}

        while heap:
            if source == goal:
                self.internet.get_page(source)
                return [source, goal]

            current_cost, current_page = heapq.heappop(heap)
            page_html = self.internet.get_page(current_page)
            links_on_page = Parser.get_links_in_page(page_html)
            for link in links_on_page:
                if link not in visited:
                    visited.add(link)
                    parents[link] = current_page
                    new_cost = cost[current_page] + self.calculate_cost(current_page, link)
                    if (link not in cost) or (new_cost < cost[link]):
                        cost[link] = new_cost
                        heapq.heappush(heap, (cost[link], link))
                    if link == goal:
                        path = [link]
                        while current_page != source:
                            path.insert(0, current_page)
                            current_page = parents[current_page]
                        path.insert(0, source)
                        return path

        return None

    def calculate_cost(self, current_page, goal):
        current_words = set(current_page.split('_'))
        goal_words = set(goal.split('_'))
        shared_words = current_words.intersection(goal_words)
        cost = (abs(len(current_words)-len(goal_words)) + 1) / (len(shared_words) + 1)
        return cost

class ASTARProblem:
    def __init__(self, internet: Internet):
        self.internet = internet

    def heuristic(self, current_page, goal):
        current_words = set(current_page.split('_'))
        goal_words = set(goal.split('_'))
        shared_words = current_words.intersection(goal_words)
        shared_char = sum(1 for char in current_page if char in goal)
        diff_wordlen = abs(len(current_words)-len(goal_words))
        return (shared_char+10*len(shared_words))/(diff_wordlen+1)

    def astar(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):
        aheap = [(0 + self.heuristic(source, goal), 0, source)]
        visited = set()
        visited.add(source)
        parents = {}

        while aheap:
            if source == goal:
                self.internet.get_page(source)
                return [source, goal]

            _, cost, current_page = heapq.heappop(aheap)

            page_html = self.internet.get_page(current_page)
            links_on_page = Parser.get_links_in_page(page_html)

            for link in links_on_page:
                if link not in visited:
                    visited.add(link)
                    parents[link] = current_page
                    new_cost = cost + 1
                    priority = new_cost + self.heuristic(link, goal)
                    heapq.heappush(aheap, (priority, new_cost, link))
                    if link == goal:
                        path = [link]
                        while current_page != source:
                            path.insert(0, current_page)
                            current_page = parents[current_page]
                        path.insert(0, source)
                        return path

        return None

class WikiracerProblem:
    def __init__(self, internet: Internet):
        self.internet = internet
        # use astar can pass wikiracer_basic_1 <= 8 and wikiracer_basic_2 <= 25

    def wikiracer(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):
        a_internet =Internet()
        a = ASTARProblem(a_internet)
        path = a.astar(source, goal)
        return path

# KARMA
class FindInPageProblem:
    def __init__(self, internet: Internet):
        self.internet = internet
    # This Karma problem is a little different. In this, we give you a source page, and then ask you to make up some heuristics that will allow you to efficiently
    #  find a page containing all of the words in `query`. Again, optimize for the fewest number of internet downloads, not for the shortest path.

    def find_in_page(self, source = "/wiki/Calvin_Li", query = ["ham", "cheese"]):

        raise NotImplementedError("Karma method find_in_page")

        path = [source]

        # find a path to a page that contains ALL of the words in query in any place within the page
        # path[-1] should be the page that fulfills the query.
        # YOUR CODE HERE

        return path # if no path exists, return None
