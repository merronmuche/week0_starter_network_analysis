import unittest
from src.loader import SlackDataLoader

class TestSlackParser(unittest.TestCase):

    def test_slack_parser(self):
        real_columns = ['msg_type', 'msg_content', 'sender_name', 'msg_sent_time', 'msg_dist_type', 
                        'time_thread_start', 'reply_count', 'reply_users_count', 'reply_users', 
                        'tm_thread_end', 'channel']
        path_channel = 'D:/tenacademy/codes/week0_starter_network_analysis/data/anonymized/all-week1/'
        slack_loader = SlackDataLoader('D:/tenacademy/codes/week0_starter_network_analysis/data/anonymized/')
        
        df = slack_loader.slack_parser(path_channel=path_channel)
        columns = list(df.columns)
        
        self.assertEqual(columns, real_columns, 'columns are not equal to real columns!!!!!')

if __name__ == '__main__':
    unittest.main()
