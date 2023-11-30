
from src.utils import slack_parser
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm

from src.utils import *

sia = SentimentIntensityAnalyzer()

path = path_channel = 'D:/tenacademy/codes/week0_starter_network_analysis/data/anonymized/all-week1/'
df = slack_parser(path_channel)
res = {}
for i, row in tqdm(df.iterrows(), total=len(df)):
    text = row['Text']
    myid = row['Id']
    res[myid] = sia.polarity_scores(text)


vaders = pd.DataFrame(res).T
vaders = vaders.reset_index().rename(columns={'index': 'Id'})
vaders = vaders.merge(df, how='left')
print(vaders.head())
