# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import subprocess
from copy import deepcopy

from unittest import TestCase
from src import process_scores
from src.process_scores import SoccerLeagueScoreProcessor, parse_input_line, calc_game_rank,\
                               _cmp_sort_rank, _add_format_info


class TestProcessScores(TestCase):
    """
    Test process_scores application
    """
    def test_parse_input_line(self):
        """
        Test parsing of a game score input line
        """
        test_cases = [
            {
                'input': '',
                'output': None
            },
            {
                'input': 'Lions 3, Snakes 3',
                'output': {'score_1': 3, 'score_2': 3, 'team_1': 'Lions', 'team_2': 'Snakes'}
            },
            {
                'input': ' Lions 3 , Snakes 3 ',
                'output': {'score_1': 3, 'score_2': 3, 'team_1': 'Lions', 'team_2': 'Snakes'}
            },
            {
                'input': 'Tarantulas 1, FC Awesome 0',
                'output': {'score_1': 1, 'score_2': 0, 'team_1': 'Tarantulas', 'team_2': 'FC Awesome'}
            }
        ]

        for data in test_cases:
            result = parse_input_line(data['input'])
            assert result == data['output'], "For input: {}, expected: {}, got: {}"\
                .format(data['input'], data['output'], result)

    def test_calc_game_rank(self):
        """
        Test the function calculating the rank from game score
        """
        test_cases = [
            {
                'input': {'score_1': 3, 'score_2': 3, 'team_1': 'Lions', 'team_2': 'Snakes'},
                'output': {'Lions': 1, 'Snakes': 1}
            },
            {
                'input': {'score_1': 2, 'score_2': 3, 'team_1': 'Lions', 'team_2': 'Snakes'},
                'output': {'Snakes': 3, 'Lions': 0}
            },
            {
                'input': {'score_1': 3, 'score_2': 2, 'team_1': 'Lions', 'team_2': 'Snakes'},
                'output': {'Lions': 3, 'Snakes': 0}
            },
        ]

        for data in test_cases:
            result = calc_game_rank(data['input'])
            assert result == data['output'], "For input: {}, expected: {}, got: {}"\
                .format(data['input'], data['output'], result)

    def test__update_league_rank(self):
        """
        Test the updating of the internal property holding the league ranks
        """
        test_cases = [
            {
                'preset': {},
                'input': {'Lions': 0, 'Snakes': 3},
                'output': {'Lions': 0, 'Snakes': 3},
            },
            {
                'preset': {'Lions': 2, 'Snakes': 3},
                'input': {'Lions': 3, 'Snakes': 0},
                'output': {'Snakes': 3, 'Lions': 5},
            },
            {
                'preset': {'Lions': 3, 'Snakes': 2},
                'input': {'Lions': 0, 'Snakes': 3},
                'output': {'Lions': 3, 'Snakes': 5},
            },
            {
                'preset': {'Lions': 3, 'Snakes': 2},
                'input': {'Lions': 0, 'FC Awesome': 3},
                'output': {'FC Awesome': 3, 'Lions': 3, 'Snakes': 2},
            },
        ]

        for data in test_cases:
            p = SoccerLeagueScoreProcessor(input_filename=None, output_filename=None)
            # Create new dict and assign to destination
            p._league_rank = deepcopy(data['preset'])
            p._update_league_rank(data['input'])
            assert p._league_rank == data['output'], "For preset: {}, input: {}, expected: {}, got: {}"\
                .format(data['preset'], data['input'], data['output'], p._league_rank)

    def test__cmp_sort_rank(self):
        """
        Test rank sort compare function
        """
        test_cases = [
            {
                'input': [{'name': 'FC Awesome', 'rank': 3}, {'name': 'Snakes', 'rank': 2}],
                'output': -1
            },
            {
                'input': [{'name': 'Snakes', 'rank': 2}, {'name': 'FC Awesome', 'rank': 3}],
                'output': 1
            },
            {
                'input': [{'name': 'Snakes', 'rank': 3}, {'name': 'FC Awesome', 'rank': 3}],
                'output': 1
            },
            {
                'input': [{'name': 'FC Awesome', 'rank': 3}, {'name': 'Snakes', 'rank': 3}],
                'output': -1
            },
            {
                'input': [{'name': 'bFC Awesome', 'rank': 3}, {'name': 'ASnakes', 'rank': 3}],
                'output': 1
            },
            {
                'input': [{'name': 'BFC Awesome', 'rank': 3}, {'name': 'aSnakes', 'rank': 3}],
                'output': 1
            },
        ]

        for data in test_cases:
            result = _cmp_sort_rank(*data['input'])
            assert result == data['output'], "For input: {}, expected: {}, got: {}"\
                .format(data['input'], data['output'], result)

    def test_process(self):
        """
        Test the input file processing
        """
        expected = [{'index': 1, 'unit': 'pts', 'name': 'Tarantulas', 'rank': 6},
                    {'index': 2, 'unit': 'pts', 'name': 'Lions', 'rank': 5},
                    {'index': 3, 'unit': 'pt', 'name': 'FC Awesome', 'rank': 1},
                    {'index': 3, 'unit': 'pt', 'name': 'Snakes', 'rank': 1},
                    {'index': 5, 'unit': 'pts', 'name': 'Grouches', 'rank': 0}]
        input_file = os.path.join(os.path.dirname(__file__), 'input.txt')
        p = SoccerLeagueScoreProcessor(input_filename=input_file, output_filename=None)
        result = p.process()
        assert result == expected, 'Expected: {}, got: {}'.format(expected, result)

    def test_application(self):
        """
        Test the application end to end
        """
        process_file = os.path.join(os.path.dirname(process_scores.__file__), 'process_scores.py')
        input_file = os.path.join(os.path.dirname(__file__), 'input.txt')
        output_file = os.path.join(os.path.dirname(__file__), 'output.txt')
        expected = ['1. Tarantulas, 6 pts',
                    '2. Lions, 5 pts',
                    '3. FC Awesome, 1 pt',
                    '3. Snakes, 1 pt',
                    '5. Grouches, 0 pts']


        # Check console output
        args = ['python', process_file, '-i', input_file]
        out = subprocess.check_output(args, stderr=subprocess.STDOUT).split(os.linesep)
        out = [item for item in out if item]
        assert out == expected, 'Expected: {}, got: {}'.format(expected, out)

        # Check file output
        args = ['python', process_file, '-i', input_file, '-o', output_file]
        out = subprocess.check_output(args, stderr=subprocess.STDOUT).split(os.linesep)
        result = []
        with open(output_file, 'r') as f:
            for line in f:
                result.append(line.strip(os.linesep))
        assert result == expected, 'Expected: {}, got: {}'.format(expected, result)
