def send_outlook_mail(account, to, subject, body, attachment_path=None):
    mailbox = account.mailbox()
    m = mailbox.new_message()
    m.to.add(to)
    m.subject = subject
    m.body = body
    if attachment_path:
        m.attachments.add(attachment_path)
    m.send()
