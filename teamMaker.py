#!/bin/python3

import random
from classes import player as pl
from classes import team as t

# def parseDatabase(path: str) -> list[pl.Player]:
#     with open(path) as f:
#         l = []
#         while True:
#             line = f.readline()
#             if not line:
#                 break
#
#             [name, rank] = line.split(',')
#             l.append(pl.Player(name = name, rank = int(rank)))
#     return l

def mostDeviantTeam(teams: list[t.Team], negative: bool = False) -> t.Team:
    max = 0
    maxIndex = 0
    for i, t in enumerate(teams):
        if (t.deviation > max) ^ negative:
            max = t.deviation
            maxIndex = i
    return teams[maxIndex]

def mostDeviantPlayer(team: t.Team, negative: bool = False) -> pl.Player:
    max = 0
    maxIndex = 0
    for i, p in enumerate(team.players):
        if (p.rank > max) ^ negative:
            max = p.rank
            maxIndex = i
    return team.players[maxIndex]

playerList = [pl.Player("Winny",2000),pl.Player("Flo", 600),pl.Player("Anna", 300),pl.Player("Sogata", 1000),pl.Player("Winer", 0), pl.Player("test", 100)]

nPlayersPerTeam = int(input("Entrer nombre de joueurs par équipe : "))
nTeams = len(playerList) // nPlayersPerTeam
excludedPlayers = playerList[nPlayersPerTeam * nTeams:]

if not nTeams:
    print("Too many players per team")
    exit(1)

random.shuffle(playerList)

teams = [t.Team(players = playerList[i:i+nPlayersPerTeam]) for i in range(0, len(playerList) - len(excludedPlayers), nPlayersPerTeam)]
meanRank = sum([t.rankSum for t in teams]) / len(teams)
stdDeviation = (sum([t.rankSum ** 2 for t in teams]) / len(teams) - meanRank ** 2) ** 0.5
print(meanRank, stdDeviation)

for t in teams:
    t.deviation = t.rankSum - meanRank

print(teams)
print("Excluded Players : ", excludedPlayers, "\n")

for _ in range(10):
    bestTeam  = mostDeviantTeam(teams)
    worstTeam = mostDeviantTeam(teams, True)

    bestPlayerOfBestTeam = mostDeviantPlayer(bestTeam)
    worstPlayerOfWorstTeam = mostDeviantPlayer(worstTeam, True)

    bestTeam.players.remove(bestPlayerOfBestTeam)
    bestTeam.players.append(worstPlayerOfWorstTeam)
    bestTeam.update()
    worstTeam.players.remove(worstPlayerOfWorstTeam)
    worstTeam.players.append(bestPlayerOfBestTeam)
    worstTeam.update()

    meanRank = sum([t.rankSum for t in teams]) / len(teams)
    newStdDeviation = (sum([t.rankSum ** 2 for t in teams]) / len(teams) - meanRank ** 2) ** 0.5

    if newStdDeviation > stdDeviation:
        bestTeam.players.remove(worstPlayerOfWorstTeam)
        bestTeam.players.append(bestPlayerOfBestTeam)
        bestTeam.update()
        worstTeam.players.remove(bestPlayerOfBestTeam)
        worstTeam.players.append(worstPlayerOfWorstTeam)
        worstTeam.update()
        break

    stdDeviation = newStdDeviation
    print(meanRank, stdDeviation)

    for t in teams:
        t.deviation = t.rankSum - meanRank

print(teams)
print("Excluded Players : ", excludedPlayers, "\n")
