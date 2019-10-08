import pandas as pd
import matplotlib.pyplot as plt

csv_path = ''
data = pd.read_csv(csv_path)
drafted = data[data["value"]>0]
drafted["fgperc"] = drafted["fgm"]/drafted["fga"]
drafted["ftperc"] = drafted["ftm"]/drafted["fta"]
averages = pd.DataFrame(drafted.mean()).transpose()
stdevs = pd.DataFrame(drafted.std()).transpose()

averages = averages.add_prefix('avg_')
averages = averages.drop(['avg_avg_value','avg_value'], axis=1)
stdevs = stdevs.add_prefix('avg_')
stdevs = stdevs.drop(['avg_avg_value','avg_value'], axis=1)

benchmarks = pd.DataFrame(13*averages.iloc[0]+13*stdevs.iloc[0]).transpose()
benchmarks["avg_fgperc"]=averages["avg_fgperc"]+stdevs["avg_fgperc"]
benchmarks["avg_ftperc"]=averages["avg_ftperc"]+stdevs["avg_ftperc"]



corrs = drafted.corr()
averages_columns = averages.columns.to_list()

column_rename = []
for i in range(len(averages_columns)):
    drafted[averages_columns[i][4:] + "_dif"] = drafted[averages_columns[i][4:]]-averages[averages_columns[i]][0]





corrs=corrs.drop(["fgm","ftm","gp","fta","fga","mpg","value","avg_value"])
corrs=corrs.drop(["fgm","ftm","gp","fta","fga","mpg","value","avg_value"],axis=1)

my_stats = ['rebounds','blocks','turnovers','steals']


class Team:
  def __init__(self, playerpool,benchmarks,target_stats):
    self.dollars = 100
    self.rebounds = 0
    self.blocks = 0
    self.tos = 0
    self.points = 0
    self.steals = 0
    self.threes = 0
    self.assists = 0
    self.pool = playerpool
    self.averages = pd.DataFrame(self.pool.mean()).transpose()
    self.players = pd.DataFrame()
    self.playercount = 0
    benchmarks.columns=benchmarks.columns.str.replace('avg_','')
    self.benchmarks = benchmarks
    self.target_stats = target_stats
    self.stat_values = (self.dollars/len(target_stats))/benchmarks[target_stats]
    stat_list=list(self.target_stats)
    self.calculate_value()


  def draft_player(self,playername, dollaramount):
    self.dollars = self.dollars-dollaramount
    player = self.pool[self.pool["name"]==playername]
    key = player.index[0]
    self.rebounds = self.rebounds+ player["rebounds"][key]
    self.blocks = self.blocks + player["blocks"][key]
    self.tos = self.tos + player["turnovers"][key]
    self.steals = self.steals+ player["steals"][key]
    self.assists = self.assists + player["assists"][key]
    self.threes = self.threes  + player["3prm"][key]
    self.points = self.points +player["points"][key]
    if len(self.players)>0:
        self.players = self.players.append(player)
    else:
        self.players = self.pool[self.pool["name"] == playername]
    self.pool = self.pool[self.pool["name"]!=playername]
    self.playercount=self.playercount+1
    self.benchmarks = self.benchmarks.iloc[0]-player.iloc[0][self.benchmarks.columns]
    self.stat_values = pd.DataFrame((self.dollars / len(self.target_stats)) / self.benchmarks[self.target_stats]).transpose()
    self.benchmarks = pd.DataFrame(self.benchmarks).transpose()
    self.calculate_value()

  def calculate_value(self):
    self.pool["auction_value"] = 0
    for i in range(len(self.target_stats)):
        self.pool[self.target_stats[i] + "_dif"] = self.pool[self.target_stats[i]] - self.averages[self.target_stats[i]][0]
    for i in range(len(self.target_stats)):
        if self.target_stats[i] != "turnovers":
          self.pool["auction_value"] = self.pool["auction_value"] + (self.stat_values[self.target_stats[i]][0] * (self.pool[self.target_stats[i]] + self.pool[self.target_stats[i] + "_dif"]))
        else:
          self.pool["auction_value"] = self.pool["auction_value"] +  -(((self.pool["turnovers_dif"]) * (13-self.playercount) / (self.dollars/len(self.target_stats))) / self.averages["turnovers"].iloc[0]) + ((13 - self.playercount) / (self.dollars/len(self.target_stats)))

    self.pool["auction_value"] = (100 / 10) - self.pool["auction_value"].mean() + self.pool["auction_value"]


  def player_drafted(self,playername):
      self.pool = self.pool = self.pool[self.pool["name"] != playername]

  def draft_board(self):
      print(self.pool.sort_values(by='auction_value', ascending=False).head(n=10))
