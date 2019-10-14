from O365 import Connection, MSGraphProtocol, Account, FileSystemTokenBackend
from datetime import datetime
import secret_config
import boto3
import base64

#TODO -  Update this with IAM roles + STS request; I think I can do that when it`s running in a Lambda?
def login_to_aws():
    s3_client = boto3.client(
        's3',
        aws_access_key_id = secret_config.aws_access_key_id,
        aws_secret_access_key = secret_config.aws_secret_access_key
    )
    return s3_client


def get_o365_mail(emailfrom, start_date, end_date):
    scopes = ['basic', 'mailbox']
    token_backend = FileSystemTokenBackend(token_path='.', token_filename='o365_token.txt')
    account = Account(
        scopes=scopes,
        credentials=('8cccb04f-b409-4d04-888b-20321dcc14b7', secret_config.o365_secret),
        token_backend=token_backend
    )

    if not account.is_authenticated:  # will check if there is a token and has not expired
        # ask for a login
        # console based authentication See Authentication for other flows
        account.authenticate()

    if account.is_authenticated:
        account.connection.refresh_token()

    my_mailbox = account.mailbox()
    my_inbox = my_mailbox.inbox_folder()

    try:
        converted_start_date = datetime.strptime(start_date, '%Y-%m-%d')
        converted_end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except Exception as e:
        print("Could not convert start_date or end_date into a datetime.datetime ")
        raise e

    inbox_query = my_mailbox.new_query().on_attribute("from").contains(emailfrom)
    inbox_query = inbox_query.chain("and").on_attribute("created_date_time").greater_equal(converted_start_date)
    inbox_query = inbox_query.chain("and").on_attribute("created_date_time").less_equal(converted_end_date)

    messages = list()
    for message in my_inbox.get_messages(download_attachments=True,
                                         query=inbox_query):
        messages.append(message)
    return messages


    print("hammertime")


if __name__ == "__main__":
    s3 = login_to_aws()

    smartplug_mail = get_o365_mail(emailfrom="WemoExport", start_date="2019-10-11", end_date="2019-12-20")

    for message in smartplug_mail:
        received_date = datetime.strftime(message._Message__received, "%Y-%m-%d_%H:%M:%S")

        for nbr, attachment in enumerate(message._Message__attachments):
            #ignore non-csv attachments:
            if attachment.name.find(".csv") > -1:
                print(f"troenser_smartplug_data/wemoexport_{received_date}_attachment{nbr}.csv")
                s3.put_object(
                    Bucket="data-engineering-sandbox",
                    Key=f"troenser_smartplug_data/wemoexport_{received_date}_attachment{nbr}.csv",
                    Body=base64.b64decode(attachment.content)
                )

    sandbox_objects = s3.list_objects(
        Bucket="data-engineering-sandbox"
    )
    print("exiting..")
