from functools import reduce


def sum_stat(stat, matches: list):
    return reduce(lambda x, y: x + y, map(lambda m: m[stat], matches))


def calc_kda(k, d, a):
    if d:
        return (k + a) / d
    else:
        return k + a


class Stats(object):
    def __init__(self, matches: list):
        self.games = len(matches)
        if self.games:
            self.wins = sum_stat("winner", matches)
            self.losses = self.games - self.wins
            self.win_rate = self.wins / self.games * 100
            self.kills = sum_stat("kills", matches)
            self.deaths = sum_stat("deaths", matches)
            self.assists = sum_stat("assists", matches)
            self.kda = calc_kda(self.kills, self.deaths, self.assists)
            self.av_kills = self.kills / self.games
            self.av_deaths = self.deaths / self.games
            self.av_assists = self.assists / self.games

    def __str__(self):
        str_ = "{} games played".format(self.games)
        if self.games:
            str_ += (": {} wins, {} losses\n".format(self.games, self.wins, self.losses) +
                     "{0:.0f}% win rate\n".format(self.win_rate) +
                     "KDA: {0:.2f}\n".format(self.kda) +
                     "Average K/D/A: {0:.1f}/".format(self.av_kills) + "{0:.1f}/".format(self.av_deaths) +
                     "{0:.1f}\n".format(self.av_assists) +
                     "Total K/D/A: {}/{}/{}".format(self.kills, self.deaths, self.assists)
                     )
        return str_
