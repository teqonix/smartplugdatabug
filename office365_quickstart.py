from O365 import Connection, MSGraphProtocol, Account, FileSystemTokenBackend
from O365.message import Message
from O365.mailbox import MailBox
import os
import secret_config


scopes = ['https://graph.microsoft.com/Mail.Read', 'offline_access']

# One time setup below - needs to be run in a Python console to get the token.txt file
# account = Account(
#     scopes=['https://graph.microsoft.com/Mail.Read'],
#     credentials=('8cccb04f-b409-4d04-888b-20321dcc14b7', 'Ai6LdAgW1VprbqJIfi@cUtpzqMJ0=8_:')
# )
# account.authenticate()

token_backend = FileSystemTokenBackend(token_path='.', token_filename='o365_token.txt')
account = Account(
    scopes=scopes,
    credentials=('8cccb04f-b409-4d04-888b-20321dcc14b7', secret_config.o365_secret),
    token_backend=token_backend
)
# account.authenticate()

account.connection.refresh_token()

my_mailbox = account.mailbox()
my_inbox = my_mailbox.inbox_folder()
for message in my_inbox.get_messages():
    print(message)



# protocol = MSGraphProtocol()
# scopes = ['mailbox']
# con = Connection(('8cccb04f-b409-4d04-888b-20321dcc14b7', 'Ai6LdAgW1VprbqJIfi@cUtpzqMJ0=8_:'), scopes=scopes)
#
# mailbox = MailBox(con=con, protocol=protocol)

print("hammertime")