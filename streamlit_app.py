import sys 
sys.path.append('../..') 
import streamlit as st 
import pandas as pd 
st.set_page_config(page_title='My app') 
import streamlit as st 
import matplotlib.pyplot as plt 
 
from src.utils import * 

st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        color:#FFA07A;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="big-font">Welcome to the Slack Analytics Dashboard!          Explore interactive insights from Slack data.</p>', unsafe_allow_html=True)
 
uploaded_file = st.file_uploader("Upload your files here...", type=['json']) 
 
if uploaded_file is not None: 
    dataframe = pd.read_json(uploaded_file) 
    st.write(dataframe) 
 
path_channel = 'data/anonymized/all-week1/' 
# path = 'D:/tenacademy/codes/week0_starter_network_analysis/data/anonymized/all-week1/' 
data = slack_parser(path_channel) 
 
# Who are the top 10 users by Message count? 
 
users = data.sender_name.value_counts() 
top_10_users_by_Message_count = users.head(10) 
bottom_10_users_df =top_10_users_by_Message_count.to_frame() 
bottom_10_users_df.columns = ['sender_name'] 
df =bottom_10_users_df.head(10) 
st.write("## Top 20 Users by Message Count")
st.markdown("This table shows the top 20 users ranked by the number of messages they have sent.")
st.dataframe(df, width=700, height=400)
 
 
def get_top_20_user(data, channel='Random'): 
    """Get user with the highest number of message sent to any channel""" 
    plt.figure(figsize=(15, 7.5)) 
    data['sender_name'].value_counts()[:20].plot.bar() 
    plt.title(f'Top 20 Message Senders in #{channel} Channel', size=30, fontweight='bold') 
    plt.xlabel("Sender Name", size=18) 
    plt.ylabel("Frequency", size=14) 
    plt.xticks(size=12) 
    plt.yticks(size=12) 
    st.pyplot(plt)  # Display the plot in Streamlit 
 
    # plt.figure(figsize=(15, 7.5)) 
    # data['sender_name'].value_counts()[-10:].plot.bar() 
    # plt.title(f'Bottom 10 Message Senders in #{channel} Channel', size=30, fontweight='bold') 
    # plt.xlabel("Sender Name", size=18) 
    # plt.ylabel("Frequency", size=14) 
    # plt.xticks(size=12) 
    # plt.yticks(size=12) 
    # st.pyplot(plt)  # Display the plot in Streamlit 
 
 
get_top_20_user(data, channel='all_week1') 

 
# Who are the top 10  users by reaction count? 
st.write("## User with the Most Reactions")
st.markdown("This table shows the User with the Most Reactions .")
comm_dict = get_community_participation(path_channel) 
df = pd.DataFrame(list(comm_dict.items()), columns=['user_id', 'reaction count']) 
df = df.sort_values(by='reaction count', ascending=False) 
top_10_users = df.head(10) 
st.dataframe(top_10_users, width=700, height=400)
 
 
def draw_user_reaction(data, channel='all_week1'): 
    plt.figure(figsize=(15, 7.5)) 
    data.groupby('sender_name')[['reply_count', 'reply_users_count']].sum().sort_values(by='reply_count', ascending=False)[:10].plot(kind='bar') 
     
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
st.write("## Average Number of Reply Count per Sender")
st.markdown("This table shows Average Number of Reply Count per Sender .")
st.dataframe(top_10_users, width=700, height=400)

 
def draw_avg_reply_count(data, channel='Random'): 
    """who commands many replies?""" 
    plt.figure(figsize=(15, 7.5)) 
    data.groupby('sender_name')['reply_count'].mean().sort_values(ascending=False)[:20].plot(kind='bar') 
 
    plt.title(f'Average Number of Reply Count per Sender in #{channel}', size=30, fontweight='bold') 
    plt.xlabel("Sender Name", size=18) 
    plt.ylabel("Frequency", size=18) 
    plt.xticks(size=14) 
    plt.yticks(size=14) 
 
    st.pyplot(plt)  # Display the plot in Streamlit 
 
 
draw_avg_reply_count(data, channel='all_week1')

