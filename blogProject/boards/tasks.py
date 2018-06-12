from celery.decorators import task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect

logger = get_task_logger(__name__)


@task(name="send_email_with_post_to_user")
def send_email_with_post_to_user(url, post, email):
    subject = 'You create new post!'
    from_email = 'from@example.com'
    message = "Your post in " + str(url) + ' Message: ' + post
    send_mail(subject, message, from_email, [email], fail_silently=False)
