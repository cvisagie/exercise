"""
Application to process soccer scores to ranking list
"""
# Make all string literals unicode by default
from __future__ import unicode_literals
import os
import re
import argparse

INPUT_STRING_REGEX = '(\s)?(?P<team_1>.*[^ ])(\s+)?(?P<score_1>\d+)(\s+)?,(\s+)?(?P<team_2>.*[^ ])(\s+)?(?P<score_2>\d+)'


def parse_input_line(line):
    """
    Return game score entry

    :param line: Text as read from input file
    :return: Dict. Example:
        {'score_1': 3,
         'score_2': 3,
         'team_1': 'Lions',
         'team_2': 'Snakes'}
    """
    m = re.match(INPUT_STRING_REGEX, line)
    if m:
        game_score = m.groupdict(None)
        game_score['score_1'] = int(game_score['score_1'])
        game_score['score_2'] = int(game_score['score_2'])
        return game_score
    return None


def calc_game_rank(score_entry):
    """
    Calculates rank score

    :param score_entry: The game score
    :return: Dict keyed by team with rank score as value
        {'Lions': 1,
         'Snakes': 1}
    """
    game_rank = {score_entry['team_1']: 0,
                 score_entry['team_2']: 0}
    if score_entry['score_1'] < score_entry['score_2']:
        game_rank[score_entry['team_2']] = 3
    if score_entry['score_1'] > score_entry['score_2']:
        game_rank[score_entry['team_1']] = 3
    if score_entry['score_1'] == score_entry['score_2']:
        game_rank[score_entry['team_1']] = 1
        game_rank[score_entry['team_2']] = 1
    return game_rank


def _cmp_sort_rank(a, b):
    """
    Determine order for sort function. Handle the special case where rank is equal by sorting alphabetically.
    :return: return a positive value for less-than, return zero if rank are equal, or return negative value for greater
    """
    if a['rank'] < b['rank']:
        return 1
    if a['rank'] > b['rank']:
        return -1
    # If equal order by team name
    if a['rank'] == b['rank']:
        names = [a['name'].lower(), b['name'].lower()]
        names.sort()
        if names[0] == a['name'].lower():
            return -1
        else:
            return 1
    return 0


def _add_format_info(rank_list):
    """
    Enrich rank list with format
    :param rank_list: The sorted rank list
    """
    i = 1
    previous = i
    item = rank_list[0]
    rank = item['rank']
    item['index'] = i
    item['unit'] = 'pt' if item['rank'] == 1 else 'pts'
    for item in rank_list[1:]:
        i += 1
        item['index'] = i
        item['unit'] = 'pt' if item['rank'] == 1 else 'pts'
        if item['rank'] == rank:
            item['index'] = previous
        else:
            previous = i
        rank = item['rank']


def write_to_file(rank_list, filename):
    """
    Write rank _list to output file
    :param rank_list: Rank list of dicts
    :param filename:  File to write to
    """
    format_string = '{index}. {name}, {rank} {unit}\n'

    with open(filename, 'w') as f:
        for item in rank_list:
            formatted = format_string.format(**item)
            f.write(formatted.encode('utf8'))


def write_to_console(rank_list):
    """
    Write to console if given, else to console
    :param rank_list: Rank list of dicts
    """
    format_string = '{index}. {name}, {rank} {unit}'

    for item in rank_list:
        print(format_string.format(**item))


class SoccerLeagueScoreProcessor(object):
    """
    Process score data from a text file and outputs a ranking list in file
    """
    def __init__(self, input_filename, output_filename):
        """
        :param input_filename: Input file name
        :param output_filename: Output file name
        """
        self._input_filename = input_filename
        self._output_filename = output_filename
        self._league_rank = {}

    def _update_league_rank(self, game_rank):
        for team in game_rank:
            self._league_rank[team] = self._league_rank.get(team, 0) + game_rank[team]

    def process(self):
        """
        Process input file and write output file
        :return: The sorted rank list of dictionaries
        """
        with open(self._input_filename, 'r') as f:
            for line in f:
                score = parse_input_line(line=line)
                rank = calc_game_rank(score_entry=score)
                self._update_league_rank(game_rank=rank)
        rank_list = [{'name': name, 'rank': rank} for name, rank in self._league_rank.iteritems()]
        rank_list.sort(cmp=_cmp_sort_rank)
        _add_format_info(rank_list=rank_list)
        return rank_list


if __name__ == "__main__":
    # Process command line arguments
    parser = argparse.ArgumentParser(description='Process score data into ranking list')
    parser.add_argument(
        '-i',
        dest="input_filename",
        default=os.path.join('.', 'input.txt'),
        help="Input filename. Default: 'input.txt'")
    parser.add_argument(
        '-o',
        dest="output_filename",
        default=None,
        help="Output filename, optional. Output to console if not provided."
    )
    args = parser.parse_args()

    p = SoccerLeagueScoreProcessor(input_filename=args.input_filename, output_filename=args.output_filename)
    result = p.process()
    if args.output_filename:
        write_to_file(rank_list=result, filename=args.output_filename)
    else:
        write_to_console(result)
