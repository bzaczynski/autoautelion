"""
Mail sender backed by SendGrid.

Usage:
$ export SENDGRID_API_KEY=<your-api-key>
$ export EMAIL_ADDRESS=<your-email>
>>> import mailer
>>> mailer.send(Autelion(status={...}, updated_at=...))
"""

import os
import logging

import sendgrid
import jinja2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MailerException(Exception):
    """Raised when email message cannot be sent."""


def send(autelion):
    """Send Autelion report to the given email address."""

    logger.info('Sending email notification')

    try:
        api_key = os.environ.get('SENDGRID_API_KEY')
        email = os.environ.get('EMAIL_ADDRESS')

        if api_key is None:
            raise MailerException('Undefined SENDGRID_API_KEY variable')

        if email is None:
            raise MailerException('Undefined EMAIL_ADDRESS variable')

        request_body = {
            'personalizations': [
                {
                    'subject': 'Autelion Report',
                    'to': [
                        {
                            'email': email
                        }
                    ]
                }
            ],
            'from': {
                'email': 'Autoautelion <autoautelion@herokuapp.com>'
            },
            'content': [
                {
                    'type': 'text/html',
                    'value': render_email(autelion)
                }
            ]
        }

        mail_client = sendgrid.SendGridAPIClient(api_key=api_key)
        response = mail_client.client.mail.send.post(request_body=request_body)

        if response.status_code == 202:
            logger.info('Email sent successfully')
        else:
            logger.error('Failed to send email: %s', response.body)

    except (MailerException, IOError) as ex:
        logger.error('Failed to send email: %s', ex)


def render_email(autelion):
    """Return HTML representation of Autelion status."""
    with open('templates/email.html.j2', encoding='utf-8') as file_object:
        template = jinja2.Template(file_object.read())
        return template.render({
            'updated_at': autelion.updated_at,
            **autelion.status
        })
