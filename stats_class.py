from functools import reduce
import global_state as glb


class BasicStats(object):
    def __init__(self, matches: list):
        self.matches = matches
        self.games = len(self.matches)
        if self.games:
            self.wins = self._sum_stat("winner")
            self.losses = self.games - self.wins
            self.win_rate = self.wins / self.games * 100
            self.kills = self._sum_stat("kills")
            self.deaths = self._sum_stat("deaths")
            self.assists = self._sum_stat("assists")
            self.kda = self._calc_kda()
            self.av_kills = self.kills / self.games
            self.av_deaths = self.deaths / self.games
            self.av_assists = self.assists / self.games

    def _sum_stat(self, stat):
        return reduce(lambda x, y: x + y, map(lambda m: m[stat], self.matches))

    def _calc_kda(self):
        if self.deaths:
            return (self.kills + self.assists) / self.deaths
        else:
            return self.kills + self.assists

    def __str__(self):
        str_ = "{} games played".format(self.games)
        if self.games:
            str_ += (": {} wins, {} losses\n".format(self.wins, self.losses) +
                     "{0:.0f}% win rate\n".format(self.win_rate) +
                     "KDA: {0:.2f}\n".format(self.kda) +
                     "Average K/D/A: {0:.1f}/".format(self.av_kills) + "{0:.1f}/".format(self.av_deaths) +
                     "{0:.1f}\n".format(self.av_assists) +
                     "Total K/D/A: {}/{}/{}".format(self.kills, self.deaths, self.assists)
                     )
        return str_


class FullStats(BasicStats):
    def __init__(self, matches: list):
        BasicStats.__init__(self, matches)
        self.primaryOpponentStats = self._process_opponents("primaryOpponent")
        self.secondaryOpponentStats = self._process_opponents("secondaryOpponent")

    def _process_opponents(self, opp_type):
        opp_stats = {}
        opps = set(map(lambda m: m[opp_type], self.matches))
        opps.discard(None)
        for opp in opps:
            opp_matches = list(filter(lambda m: m[opp_type] == opp, self.matches))
            opp_stats[str(opp)] = BasicStats(opp_matches)
        return opp_stats

    def __str__(self):
        str_ = BasicStats.__str__(self)
        opp_stats = lambda o: ("\n    vs {}: {} games, ".format(glb.champions[o]["name"], opps[o].games) +
                               "{0:.0f}% win rate, ".format(opps[o].win_rate) +
                               "{0:.2f} KDA".format(opps[o].kda))
        opps = self.primaryOpponentStats
        if len(opps):
            str_ += "\nPrimary Opponents:"
            str_ += reduce(lambda x, y: x + y, map(opp_stats, opps))

        opps = self.secondaryOpponentStats
        if len(opps):
            str_ += "\nSecondary Opponents:"
            str_ += reduce(lambda x, y: x + y, map(opp_stats, opps))

        return str_
