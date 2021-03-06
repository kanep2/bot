import pandas as pd 
import numpy as np
import datetime as dt
from datetime import datetime as dt
from collections import defaultdict 
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.grid_search import GridSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder
import statsmodels.api as sm
from sklearn.metrics import f1_score, make_scorer, classification_report
from sklearn.feature_extraction import DictVectorizer

import csv

teams = []
teams_all = []
ranks = {}	
match_dfs = {}
teams_all = []

months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
r_months = ['jan', 'feb', 'mar']
mTypes = ['onl', 'lan', 'both']
fieldnames = ['date', 'team1', 'score1', 'team2', 'score2']

print '>'

#>>> teams <<<
with open('../data/teams/teams_all.csv', mode='r') as f:
	reader = csv.reader(f)
	#teams = dict((row[0], True) for row in reader)
	for row in reader:
		teams.append(row[0])  

#>>> ranks <<<
for m in r_months:
	with open('../data/ranks/ranks_' + m + '.csv', mode='r') as f:
		data = {}
		reader = csv.reader(f)
		data = dict((row[0], row[1]) for row in reader)	
		ranks[m] = defaultdict(lambda: 31, data)

#>>> matches <<<
for t in mTypes:
	tdf = pd.read_csv('../data/matches/' + t + '_matches_all.csv', parse_dates=['date'])
	tdf = tdf[tdf.date >= np.datetime64('2016-02-01')] 
	match_dfs[t] = tdf




# def removekey(d, key):
#     r = dict(d)
#     del r[key]
#     return r

## find teams that are always in rankings
# always_ranked_teams = list(teams)
# for m in r_months:
# 	for t in always_ranked_teams:
# 				if t not in data:
# 					always_ranked_teams = removekey(always_ranked_teams, t)





#>>>>>>>>>>>>>>>>>>>>>>>>>
currentSet = 'lan'
print currentSet
#>>>>>>>>>>>>>>>>>>>>>>>>>

#chose data set
df = match_dfs[currentSet].copy()

#trim teams
df = df[df.team1.isin(teams)]
df = df[df.team2.isin(teams)]



#find what teams are in data set
teamDict = {}
for index, row in df.iterrows():	
	print row['team1'], row['team2']
	teamDict[row['team1']] = True
	teamDict[row['team2']] = True 
print '-----'
for t in teamDict:
	teams_all.append(t)
	print t


#create winner column
df['1wins'] = df['score2'] < df['score1']

#>>>>>> create features <<<<<<<
won_last = defaultdict(int)
df['team1LastWin'] = 0
df['team2LastWin'] = 0
last_match_winner = defaultdict(int)
df['t1WonLast'] = 0
#df['team1RanksHigher'] = 0
df['t1RankHigher'] = 0
df['t2RankHigher'] = 0
last_rounds = defaultdict(int)
df['t1LastRounds'] = 0
df['t2LastRounds'] = 0
df['t1Rank'] = 0
df['t2Rank'] = 0
df['numDate'] = 0

for index, row in df.iterrows():	
	t1 = row['team1']
	t2 = row['team2']
	#won_last
	row['team1LastWin'] = won_last[t1]
	row['team2LastWin'] = won_last[t2]
	won_last[t1] = row['1wins']
	won_last[t2] = not row['1wins']
	#last_match_winner
	teams = tuple(sorted([t1, t2]))
	row['t1WonLast'] = 1 if last_match_winner[teams] == row['team1'] else 0
	winner = row['team1'] if row['1wins'] else row['team2']
	last_match_winner[teams] = winner
	#last_rank_higher
	date = row['date']
	month = months[date.month-2 % 12]
	t1_rank = ranks[month][t1] 
	t2_rank = ranks[month][t2]
	row['t1Rank'] = t1_rank
	row['t2Rank'] = t2_rank
	row['t1RankHigher'] = int(t1_rank) < int(t2_rank)
	row['t2RankHigher'] = int(t2_rank) < int(t1_rank)
	#last_rounds
	row['t1LastRounds'] = last_rounds[t1]
	row['t2LastRounds'] = last_rounds[t2]
	t1_rounds = row['score1'] if row['score1'] < 17 else 16
	t2_rounds = row['score2'] if row['score2'] < 17 else 16
	last_rounds[t1] = t1_rounds
	last_rounds[t2] = t2_rounds
	#dates as number
	row['numDate'] = row['date'].to_pydatetime()
	row['numDate'] = row['numDate'].toordinal()
	
	df.ix[index] = row   


# for index, row in df.iterrows():
# 	print row

  

# X = df[['t1WonLast', 't1RankHigher', 't2RankHigher']].values ## <<65%
# #X = df[['t1WonLast', 't1Rank', 't2Rank']].values 
# clf = RandomForestClassifier(random_state=14)
# scores = cross_val_score(clf, X, y_true, scoring='accuracy')
# print('Accuracy: {0:.1f}%'.format(np.mean(scores) * 100))


#X = df[['team1', 'team2', 't1WonLast', 't1RankHigher', 't2RankHigher']].values
#X.columns = ['team1', 'team2', 't1WonLast', 't1RankHigher', 't2RankHigher']



#------------------

#separate training and testing
#<<<<<<<<<<<<<<<<<<<<<<<
X_train = df[df.date < np.datetime64('2016-04-01')]	
X_test = df[df.date >= np.datetime64('2016-04-01')]
X_all = pd.DataFrame(df)

#>>>>> encode teams <<<<<
encoding = LabelEncoder()
encoding.fit(teams_all)
#for d in [X_train, X_test]:

#for d in [X_train, X_test, X_all]:
d = X_all	
t1s = encoding.transform(d["team1"].values)
t2s = encoding.transform(d["team2"].values)
X_teams = np.vstack([t1s, t2s]).T
onehot = OneHotEncoder()
X_teams = onehot.fit_transform(X_teams).todense()
X_team_df = pd.DataFrame(X_teams)
d = pd.concat([X_team_df, d], axis=1)

#get output columns
y_train = X_train['1wins'].values
y_test = X_test['1wins'].values
y_all = X_all['1wins'].values

#drop rows not being used
colToDrop = ['date','team1', 'score1', 'team2', 'score2', '1wins', 't1WonLast', 't1RankHigher', 't2RankHigher']
X_train = X_train.drop(colToDrop, axis = 1)   
X_test = X_test.drop(colToDrop, axis = 1)   
X_all =  X_all.drop(colToDrop, axis = 1)   
X_df = df.drop(colToDrop, axis = 1) 
#>>>>> model <<<<<                              
nb_est = GaussianNB()
# nb_est.fit(X_train, y_train)
# pred = nb_est.predict(X_test)
# print pred[0:8]

# scores = cross_val_score(nb_est, X_df, y_all, scoring='accuracy')
# print("Accuracy: {0:.1f}%".format(np.mean(scores) * 100))


#parameter space for random forest
# parameter_space = {
# 	"max_features": [2, 10, 50, 'auto'],
# 	"n_estimators": [50,100,200],
# 	"criterion": ["gini", "entropy"],
# 	"min_samples_leaf": [1, 2, 4, 6],
# }
# clf = RandomForestClassifier(random_state=14)
# grid = GridSearchCV(clf, parameter_space)
# grid.fit(X_teams, y_all)

# clf = RandomForestClassifier(random_state=14)
# print("Accuracy: {0:.1f}%".format(grid.best_score_ * 100))
#scorer = make_scorer(f1_score, pos_label=None, average='weighted')
# scores = cross_val_score(clf, X_all, y_all, scoring='accuracy')
# print("Accuracy: {0:.1f}%".format(np.mean(scores) * 100))