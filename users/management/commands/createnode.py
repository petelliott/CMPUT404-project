from django.core.management.base import BaseCommand, CommandError
from users.models import Node
import getpass

class Command(BaseCommand):
    help = 'create a new node account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str)
        parser.add_argument('--password', type=str)
        parser.add_argument('--api', type=str)

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        service = options['api']

        if username is None:
            username = input("Username: ")

        if service is None:
            service = input("Service url: ")

        if password is None:
            password = getpass.getpass()

        Node.signup(username, password, service)
