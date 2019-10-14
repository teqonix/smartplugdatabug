from O365 import Connection, MSGraphProtocol, Account, FileSystemTokenBackend
from O365.message import Message
from O365.mailbox import MailBox
import os
import secret_config


scopes = ['https://graph.microsoft.com/Mail.Read', 'offline_access']

# One time setup below - needs to be run in a Python console to get the token.txt file
account = Account(
    scopes=['https://graph.microsoft.com/Mail.Read'],
    credentials=('8cccb04f-b409-4d04-888b-20321dcc14b7', secret_config.o365_secret)
)
account.authenticate()

exit()