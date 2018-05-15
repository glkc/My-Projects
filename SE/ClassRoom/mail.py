import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from service import getMailService
from PeerReview.Logger import getLogger

log = getLogger("mail")

def SendMessage(credentials, sender, to, bcc, subject, msgHtml, msgPlain):
    """
    Sends message to the "to" and "bcc" list from sender.
    :param credentials: Required identity parameter to connect to Google Mail API services.
    :param sender: Sender of the mail
    :param to: Reciever/s of the mail
    :param bcc: BCC/s of the mail
    :param subject: Subject of the mail
    :param msgHtml: HTML message of the mail
    :param msgPlain: Plain messge of the mail
    :return: Result of the mail sending service.
    """
    service = getMailService(credentials)
    message1 = CreateMessageHtml(sender, to, bcc, subject, msgHtml, msgPlain)
    SendMessageInternal(service, "me", message1)

def SendMessageInternal(service, user_id, message):
    """
    Sends mail using Google Mail service
    :param service: Parameter to access Google Mail service
    :param user_id: UserId of the individual sending the mail. In our case, its "me".
    :param message: Message of the mail
    :return: None
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        log.info('Mail has been sent with message Id and user Id: %s', message[u'id'], user_id)
    except errors.HttpError, error:
        log.error('An error occurred while sending message : %s', error)

def CreateMessageHtml(sender, to, bcc, subject, msgHtml, msgPlain):
    """
    Generates the html message.
    :param sender: Sender of the mail
    :param to: Reciever/s of the mail
    :param bcc: BCC/s of the mail
    :param subject: Subject of the mail
    :param msgHtml: HTML message of the mail
    :param msgPlain: Plain message of the mail
    :return: The HTML message compatible with Google Mail service.
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['Bcc'] = bcc
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    return {'raw': base64.urlsafe_b64encode(msg.as_string())}