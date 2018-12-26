import os
import logging

import sendgrid


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


api_key = os.environ.get('SENDGRID_API_KEY')
email = os.environ.get('EMAIL_ADDRESS')

if api_key is None:
    logger.error('Unable to read SENDGRID_API_KEY environment variable')
elif email is None:
    logger.error('Unable to read EMAIL_ADDRESS environment variable')
else:
    mail_client = sendgrid.SendGridAPIClient(api_key=api_key)
    response = mail_client.client.mail.send.post(request_body={
        'personalizations': [
            {
                'to': [
                    {
                        'email': email
                    }
                ],
                'subject': 'Autelion Report'
            }
        ],
        'from': {
            'email': 'Autoautelion <autoautelion@herokuapp.com>'
        },
        'content': [
            {
                'type': 'text/html',
                'value': 'Hello, <b>Email</b>!'
            }
        ]
    })
    print(response.status_code)
    print(response.body)
    print(response.headers)
