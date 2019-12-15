from threading import Thread
import os
import pika
from json import loads
from django.core.mail import EmailMessage
# from .django_blog import settings
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

def mail_thread():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare('email_queue')

    def callback(c, m, props, body):
        body = loads(body.decode('utf-8'))
        email = EmailMessage(
            body['subject'],
            body['message'],
            to=[body['email']])
        email.send()

    channel.basic_consume(queue='email_queue', auto_ack=1, on_message_callback=callback)
    channel.start_consuming()


t = Thread(target=mail_thread, daemon=True)
t.start()


os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'django_blog.settings')

application = get_wsgi_application()
call_command('runserver', '127.0.0.1:8000')
