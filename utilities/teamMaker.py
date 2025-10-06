import itertools

from classes.player import Player
from classes.team import Team

def convert_string(string):
    return [val.split(":") for val in string.replace(" ", "").split(",")]

def min_gap(players: list[Player], team: Team, power: int) -> Player:
    best_choice = Player("lambda", 5000)
    ecart = abs(power - (best_choice.power + team.power))
    for player in players[1:]:
        if abs(ecart > power - (player.power + team.power)) and player.team is None:
            best_choice = player
            ecart = abs(power - (player.power + team.power))

    return best_choice


def all_full(teams: list[Team]) -> bool:
    for team in teams:
        if len(team.players) < team.limit:
            return False
    return True


def make_teams(players: list[Player], limit: int = 3) -> tuple[list[Team], list[Player]]:
    teams = [Team(limit) for _ in range(len(players) // limit)]
    exclude_players = []
    treated = []

    players.sort(reverse=True, key=lambda x: x.power)

    teams[0].add_player(players[0])
    treated.append(players[0])

    while len(treated) != len(players):
        teams.sort(reverse=True, key=lambda x: x.power)
        min_team = teams[-1]
        max_team = teams[0]

        if min_team.power == max_team.power or min_team.is_full() and not max_team.is_full():
            while not max_team.is_full():
                best_choice = min_gap(players, max_team, min_team.power)
                max_team.add_player(best_choice)
                treated.append(best_choice)
        else:
            while not min_team.is_full() and min_team.power < max_team.power:
                best_choice = min_gap(players, min_team, max_team.power)
                min_team.add_player(best_choice)
                treated.append(best_choice)

        if all_full(teams):
            for player in players:
                if player.team is None:
                    exclude_players.append(player)
                    treated.append(player)

    return teams, exclude_players

def make_teams_by_kk(players: list[Player], limit: int = 3) -> tuple[list[Team], list[Player]]:
    best = None
    teams = [Team(limit) for _ in range(0, len(players) // limit)]
    for combo in itertools.combinations(players, limit):
        print(combo)
        power = sum(map(int, combo),start=0)
        print(power)


if __name__ == "__main__":
    make_teams_by_kk([Player("test", 1000), Player("test2", 1300), Player("test3", 1700), Player("test4", 2000), Player("test5", 1100), Player("test6", 1500)])