import os
import sys
import glob
import json
from collections import Counter

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
import re
import datetime

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from wordcloud import WordCloud


def break_combined_weeks(combined_weeks):
    """
    Breaks combined weeks into separate weeks.

    Args:
        combined_weeks: list of tuples of weeks to combine

    Returns:
        tuple of lists of weeks to be treated as plus one and minus one
    """
    plus_one_week = []
    minus_one_week = []

    for week in combined_weeks:
        if week[0] < week[1]:
            plus_one_week.append(week[0])
            minus_one_week.append(week[1])
        else:
            minus_one_week.append(week[0])
            plus_one_week.append(week[1])

    return plus_one_week, minus_one_week


def get_msgs_df_info(df):
    msgs_count_dict = df.user.value_counts().to_dict()
    replies_count_dict = dict(Counter([u for r in df.replies if r != None for u in r]))
    mentions_count_dict = dict(Counter([u for m in df.mentions if m != None for u in m]))
    links_count_dict = df.groupby("user").link_count.sum().to_dict()
    return msgs_count_dict, replies_count_dict, mentions_count_dict, links_count_dict


def get_messages_dict(msgs):
    msg_list = {
        "msg_id": [],
        "text": [],
        "attachments": [],
        "user": [],
        "mentions": [],
        "emojis": [],
        "reactions": [],
        "replies": [],
        "replies_to": [],
        "ts": [],
        "links": [],
        "link_count": []
    }

    for msg in msgs:
        if "subtype" not in msg:
            try:
                msg_list["msg_id"].append(msg["client_msg_id"])
            except:
                msg_list["msg_id"].append(None)

            msg_list["text"].append(msg["text"])
            msg_list["user"].append(msg["user"])
            msg_list["ts"].append(msg["ts"])

            if "reactions" in msg:
                msg_list["reactions"].append(msg["reactions"])
            else:
                msg_list["reactions"].append(None)

            if "parent_user_id" in msg:
                msg_list["replies_to"].append(msg["ts"])
            else:
                msg_list["replies_to"].append(None)

            if "thread_ts" in msg and "reply_users" in msg:
                msg_list["replies"].append(msg["replies"])
            else:
                msg_list["replies"].append(None)

            if "blocks" in msg:
                emoji_list = []
                mention_list = []
                link_count = 0
                links = []

                for blk in msg["blocks"]:
                    if "elements" in blk:
                        for elm in blk["elements"]:
                            if "elements" in elm:
                                for elm_ in elm["elements"]:

                                    if "type" in elm_:
                                        if elm_["type"] == "emoji":
                                            emoji_list.append(elm_["name"])

                                        if elm_["type"] == "user":
                                            mention_list.append(elm_["user_id"])

                                        if elm_["type"] == "link":
                                            link_count += 1
                                            links.append(elm_["url"])

                msg_list["emojis"].append(emoji_list)
                msg_list["mentions"].append(mention_list)
                msg_list["links"].append(links)
                msg_list["link_count"].append(link_count)
            else:
                msg_list["emojis"].append(None)
                msg_list["mentions"].append(None)
                msg_list["links"].append(None)
                msg_list["link_count"].append(0)

    return msg_list


def from_msg_get_replies(msg):
    replies = []
    if "thread_ts" in msg and "replies" in msg:
        try:
            for reply in msg["replies"]:
                reply["thread_ts"] = msg["thread_ts"]
                reply["message_id"] = msg["client_msg_id"]
                replies.append(reply)
        except:
            pass
    return replies


def msgs_to_df(msgs):
    msg_list = get_messages_dict(msgs)
    df = pd.DataFrame(msg_list)
    return df


def process_msgs(msg):
    '''
    select important columns from the message
    '''

    keys = ["client_msg_id", "type", "text", "user", "ts", "team",
            "thread_ts", "reply_count", "reply_users_count"]
    msg_list = {k: msg[k] for k in keys}
    rply_list = from_msg_get_replies(msg)

    return msg_list, rply_list


def get_messages_from_channel(channel_path):
    '''
    get all the messages from a channel        
    '''
    channel_json_files = os.listdir(channel_path)
    channel_msgs = [json.load(open(channel_path + "/" + f)) for f in channel_json_files]

    df = pd.concat([pd.DataFrame(get_messages_dict(msgs)) for msgs in channel_msgs])
    print(f"Number of messages in channel: {len(df)}")

    return df


def convert_2_timestamp(column, data):
    """convert from unix time to readable timestamp
        args: column: columns that needs to be converted to timestamp
                data: data that has the specified column
    """
    if column in data.columns.values:
        timestamp_ = []
        for time_unix in data[column]:
            if time_unix == 0:
                timestamp_.append(0)
            else:
                a = datetime.datetime.fromtimestamp(float(time_unix))
                timestamp_.append(a.strftime('%Y-%m-%d %H:%M:%S'))
        return timestamp_
    else:
        print(f"{column} not in data")


################### migrated form notebook
# combine all json file in all-weeks8-9
def slack_parser(path_channel):
    """ parse slack data to extract useful informations from the json file
        step of execution
        1. Import the required modules
        2. read all json file from the provided path
        3. combine all json files in the provided path
        4. extract all required informations from the slack data
        5. convert to dataframe and merge all
        6. reset the index and return dataframe
    """

    # specify path to get json files
    combined = []
    files = glob.glob(f'{path_channel}*.json')
    for json_file in files:
        with open(json_file, 'r', encoding="utf8") as slack_data:
            combined.append(json.loads(slack_data.read()))
    # loop through all json files and extract required informations
    dflist = []
    for slack_data in combined:

        msg_type, msg_content, sender_id, time_msg, msg_dist, time_thread_st, reply_users, \
            reply_count, reply_users_count, tm_thread_end = [], [], [], [], [], [], [], [], [], []

        for row in slack_data:
            if 'bot_id' in row.keys():
                continue
            else:
                msg_type.append(row['type'])
                msg_content.append(row['text'])
                if 'user_profile' in row.keys():
                    sender_id.append(row['user_profile']['real_name'])
                else:
                    sender_id.append('Not provided')
                time_msg.append(row['ts'])
                if 'blocks' in row.keys() and len(row['blocks'][0]['elements'][0]['elements']) != 0 :
                    msg_dist.append(row['blocks'][0]['elements'][0]['elements'][0]['type'])
                else:
                    msg_dist.append('reshared')
                if 'thread_ts' in row.keys():
                    time_thread_st.append(row['thread_ts'])
                else:
                    time_thread_st.append(0)
                if 'reply_users' in row.keys():
                    reply_users.append(",".join(row['reply_users']))
                else:
                    reply_users.append(0)
                if 'reply_count' in row.keys():
                    reply_count.append(row['reply_count'])
                    reply_users_count.append(row['reply_users_count'])
                    tm_thread_end.append(row['latest_reply'])
                else:
                    reply_count.append(0)
                    reply_users_count.append(0)
                    tm_thread_end.append(0)
        data = zip(msg_type, msg_content, sender_id, time_msg, msg_dist, time_thread_st,
                   reply_count, reply_users_count, reply_users, tm_thread_end)
        columns = ['msg_type', 'msg_content', 'sender_name', 'msg_sent_time', 'msg_dist_type',
                   'time_thread_start', 'reply_count', 'reply_users_count', 'reply_users', 'tm_thread_end']

        df = pd.DataFrame(data=data, columns=columns)
        df = df[df['sender_name'] != 'Not provided']
        dflist.append(df)

    dfall = pd.concat(dflist, ignore_index=True)
    dfall['channel'] = path_channel.split('/')[-1].split('.')[0]
    dfall = dfall.reset_index(drop=True)

    return dfall


def parse_slack_reaction(path, channel):
    """get reactions"""
    dfall_reaction = pd.DataFrame()
    combined = []
    for json_file in glob.glob(f"{path}*.json"):
        with open(json_file, 'r') as slack_data:
            combined.append(slack_data)
            text = slack_data.read()

    reaction_name, reaction_count, reaction_users, msg, user_id = [], [], [], [], []

    for k in combined:
        slack_data = json.load(open(k.name, 'r', encoding="utf-8"))

        for i_count, i in enumerate(slack_data):
            if 'reactions' in i.keys():
                for j in range(len(i['reactions'])):
                    msg.append(i['text'])
                    user_id.append(i['user'])
                    reaction_name.append(i['reactions'][j]['name'])
                    reaction_count.append(i['reactions'][j]['count'])
                    reaction_users.append(",".join(i['reactions'][j]['users']))

    data_reaction = zip(reaction_name, reaction_count, reaction_users, msg, user_id)
    columns_reaction = ['reaction_name', 'reaction_count', 'reaction_users_count', 'message', 'user_id']
    df_reaction = pd.DataFrame(data=data_reaction, columns=columns_reaction)
    df_reaction['channel'] = channel
    return df_reaction


def get_community_participation(path):
    """ specify path to get json files"""
    combined = []
    comm_dict = {}
    for json_file in glob.glob(f"{path}*.json"):
        with open(json_file, 'r') as slack_data:
            combined.append(slack_data)
    # print(f"Total json files is {len(combined)}")
    for i in combined:
        a = json.load(open(i.name, 'r', encoding='utf-8'))

        for msg in a:
            if 'replies' in msg.keys():
                for i in msg['replies']:
                    comm_dict[i['user']] = comm_dict.get(i['user'], 0) + 1
    return comm_dict


def get_tagged_users(df):
    """get all @ in the messages"""

    res = []
    for msg in df['msg_content']:
        tagged_user = re.findall(r'@U\w+', msg)
        res.append(tagged_user)

    return pd.Series(res)


    
def map_userid_2_realname(user_profile: dict, comm_dict: dict, plot=False):
    """
    map slack_id to realnames
    user_profile: a dictionary that contains users info such as real_names
    comm_dict: a dictionary that contains slack_id and total_message sent by that slack_id
    """
    user_dict = {} # to store the id
    real_name = [] # to store the real name
    ac_comm_dict = {} # to store the mapping
    count = 0
    # collect all the real names
    for i in range(len(user_profile['profile'])):
        real_name.append(dict(user_profile['profile'])[i]['real_name'])

    # loop the slack ids
    for i in user_profile['id']:
        user_dict[i] = real_name[count]
        count += 1

    # to store mapping
    for i in comm_dict:
        if i in user_dict:
            ac_comm_dict[user_dict[i]] = comm_dict[i]

    ac_comm_dict = pd.DataFrame(data= zip(ac_comm_dict.keys(), ac_comm_dict.values()),
    columns=['LearnerName', '# of Msg sent in Threads']).sort_values(by='# of Msg sent in Threads', ascending=False)
    
    if plot:
        ac_comm_dict.plot.bar(figsize=(15, 7.5), x='LearnerName', y='# of Msg sent in Threads')
        plt.title('Student based on Message sent in thread', size=20)
        
    return ac_comm_dict

def get_message_replies(path):

    combined = []
    for json_file in glob.glob(f"{path}*.json"):
        with open(json_file, 'r') as slack_data:
            combined.append(slack_data)
    
    replies = {}
    for k in combined:
        messages = json.load(open(k.name, 'r', encoding="utf-8"))
        for message in messages:
            if 'reply_count' in message.keys():
                replies[message['text']] = message['reply_count']
            
    return replies


def get_message_reactions(path):

    combined = []
    for json_file in glob.glob(f"{path}*.json"):
        with open(json_file, 'r') as slack_data:
            combined.append(slack_data)
    
    reactions = {}
    for k in combined:
        messages = json.load(open(k.name, 'r', encoding="utf-8"))
        for message in messages:
            if 'reactions' in message.keys():
                msg_reactions = message['reactions']
                for reaction in msg_reactions:
                    if message['text'] in reaction.keys():
                        reactions[message['text']] += reaction['count']
                    else:
                        reactions[message['text']] = reaction['count']
            
    return reactions

def scatter_2d_channels(path='D:/tenacademy/codes/week0_starter_network_analysis/data/anonymized/'):

    channels = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    columns = ['channels', 'messges', 'replies', 'reactions']
    messages_list = []
    replies_list = []
    reactions_list = []
    for channel in channels:
        full_path = os.path.join(path, channel) + '/'
        df = slack_parser(full_path)
        n_messages = len(df)

        replies = get_message_replies(full_path)
        df = pd.DataFrame(list(replies.items()), columns=['message text', 'reply_count'])
        n_replies = df.reply_count.values.sum()
        reactions = get_message_reactions(full_path)
        df = pd.DataFrame(list(reactions.items()), columns=['message text', 'reactions'])
        n_reactions = df.reactions.values.sum()

        messages_list.append(n_messages)
        replies_list.append(n_replies)
        reactions_list.append(n_reactions)
    
    data = zip(channels, messages_list, replies_list, reactions_list)
    out_df = pd.DataFrame(data, columns= columns)
    out_df['reactions_replies'] = out_df['replies'] + out_df['reactions']
    return out_df


if __name__ == '__main__':
    path_channel = 'D:/tenacademy/codes/week0_starter_network_analysis/data/anonymized/all-week1/'
    channel = 'all-week1'

    ################################ TEST parse_slack_reaction functions################################
    # reactions = parse_slack_reaction(path_channel, 'week1')
    ################################ TEST convert_2_timestamp functions################################
    # get_community_participation(path_channel)
    ################################ TEST convert_2_timestamp functions################################
    data = slack_parser(path_channel)
    # comm_dict = get_community_participation(path_channel)
    # df = pd.DataFrame(list(comm_dict.items()), columns=['user_id', 'reply_count'])
    # df = df.sort_values(by='reply_count', ascending=False)
    # top_10_users = df.head(10)
    # bottom_10_users = df.tail(10)
    # print(comm_dict)

    
    
    time_column = convert_2_timestamp('time_thread_start', data)
    time_column_end = convert_2_timestamp('time_thread_end', data)
    data['time_thread_start'] = time_column
    data['time_thread_end'] = time_column_end
    res = get_tagged_users(data)
    print(res)

    

    replies = get_message_replies(path_channel)
    # convert to dataframe
    df = pd.DataFrame(list(replies.items()), columns=['message text', 'reply_count'])
    df = df.sort_values(by='reply_count', ascending=False)
    top_10_messages = df.head(10)
    print(replies)

    data = slack_parser(path_channel)
    # time = convert_2_timestamp('msg_sent_time', data)
    # data['time'] = time
    # print(data)

    
    
    

