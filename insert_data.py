from Mongo import Message,UserProfile,Reaction
import json


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    


data = read_json_file('data/anonymized/all-week2/2022-08-28.json')

# Function to insert messages
def insert_messages(data):
    for item in data:
        # Creating a Message object for each item in the data
        message = Message(
            client_msg_id=item.get('client_msg_id'),
            type=item['type'],
            text=item.get('text'),
            user=item['user'],
            ts=item['ts'],
            blocks=item.get('blocks'),
            team=item.get('team'),
            user_team=item.get('user_team'),
            source_team=item.get('source_team'),
            subtype=item.get('subtype'),
            inviter=item.get('inviter')
        )

        # Handle nested UserProfile and Reactions if present
        if 'user_profile' in item:
            message.user_profile = UserProfile(**item['user_profile'])
        if 'reactions' in item:
            message.reactions = [Reaction(**reaction) for reaction in item['reactions']]

        # Save the message object to MongoDB
        message.save()

# Call the function with the provided data
insert_messages(data)