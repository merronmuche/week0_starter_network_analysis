
import sys
sys.path.append('../..')
import streamlit as st
import pandas as pd
st.set_page_config(page_title='My app')
import streamlit as st
import matplotlib.pyplot as plt

from src.utils import *
st.write('Welcome')


uploaded_file = st.file_uploader("Upload your files here...", type=['json'])

if uploaded_file is not None:
    dataframe = pd.read_json(uploaded_file)
    st.write(dataframe)

path_channel = 'D:/tenacademy/codes/week0_starter_network_analysis/data/anonymized/all-week1/'
# path = 'D:/tenacademy/codes/week0_starter_network_analysis/data/anonymized/all-week1/'
data = slack_parser(path_channel)

# Who are the top 10 users by Message count?

users = data.sender_name.value_counts()
top_10_users_by_Message_count = users.head(10)
bottom_10_users_df =top_10_users_by_Message_count.to_frame()
bottom_10_users_df.columns = ['sender_name']
df =bottom_10_users_df.head(10)

st.write(df)


def get_top_20_user(data, channel='Random'):
    """Get user with the highest number of message sent to any channel"""
    plt.figure(figsize=(15, 7.5))
    data['sender_name'].value_counts()[:20].plot.bar()
    plt.title(f'Top 20 Message Senders in #{channel} Channel', size=15, fontweight='bold')
    plt.xlabel("Sender Name", size=18)
    plt.ylabel("Frequency", size=14)
    plt.xticks(size=12)
    plt.yticks(size=12)
    st.pyplot(plt)  # Display the plot in Streamlit

    plt.figure(figsize=(15, 7.5))
    data['sender_name'].value_counts()[-10:].plot.bar()
    plt.title(f'Bottom 10 Message Senders in #{channel} Channel', size=15, fontweight='bold')
    plt.xlabel("Sender Name", size=18)
    plt.ylabel("Frequency", size=14)
    plt.xticks(size=12)
    plt.yticks(size=12)
    st.pyplot(plt)  # Display the plot in Streamlit


get_top_20_user(data, channel='all_week1')


# Who are the top 10  users by reaction count?

comm_dict = get_community_participation(path_channel)
df = pd.DataFrame(list(comm_dict.items()), columns=['user_id', 'reaction count'])
df = df.sort_values(by='reaction count', ascending=False)
top_10_users = df.head(10)
st.write(top_10_users)



def draw_user_reaction(data, channel='all_week1'):
    plt.figure(figsize=(15, 7.5))
    data.groupby('sender_name')[['reply_count', 'reply_users_count']].sum()\
        .sort_values(by='reply_count', ascending=False)[:10].plot(kind='bar')
    
    plt.title(f'User with the Most Reactions in #{channel}', size=25)
    plt.xlabel("Sender Name", size=18)
    plt.ylabel("Frequency", size=18)
    plt.xticks(size=14)
    plt.yticks(size=14)

    st.pyplot(plt)  # Display the plot in Streamlit

draw_user_reaction(data, channel='all_week1')


# which user has the highest number of reply counts?

comm_dict = get_community_participation(path_channel)
df = pd.DataFrame(list(comm_dict.items()), columns=['user_id', 'reply_count'])
df = df.sort_values(by='reply_count', ascending=False)
top_10_users = df.head(10)

st.write(top_10_users)

def draw_avg_reply_count(data, channel='Random'):
    """who commands many replies?"""
    plt.figure(figsize=(15, 7.5))
    data.groupby('sender_name')['reply_count'].mean().sort_values(ascending=False)[:20]\
        .plot(kind='bar')

    plt.title(f'Average Number of Reply Count per Sender in #{channel}', size=20, fontweight='bold')
    plt.xlabel("Sender Name", size=18)
    plt.ylabel("Frequency", size=18)
    plt.xticks(size=14)
    plt.yticks(size=14)

    st.pyplot(plt)  # Display the plot in Streamlit


draw_avg_reply_count(data, channel='all_week1')


# What are the top 10 messages by Reactions?
path = 'D:/tenacademy/codes/week0_starter_network_analysis/data/anonymized/all-week1/'
reactions = get_message_reactions(path)
# convert to dataframe
df = pd.DataFrame(list(reactions.items()), columns=['message text', 'reactions'])
df = df.sort_values(by='reactions', ascending=False)
top_10_messages_by_Reactions = df.head(10)


st.write(top_10_messages_by_Reactions)



















