from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Set up Google OAuth application for testing'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, help='Google OAuth Client ID')
        parser.add_argument('--client-secret', type=str, help='Google OAuth Client Secret')
        parser.add_argument('--name', type=str, default='Google OAuth', help='Application name')

    def handle(self, *args, **options):
        if not options['client_id'] or not options['client_secret']:
            self.stdout.write(
                self.style.ERROR(
                    'Please provide both --client-id and --client-secret arguments\n'
                    'Example: python manage.py setup_google_oauth --client-id "your-id" --client-secret "your-secret"'
                )
            )
            return

        # Get or create the default site
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={'domain': 'localhost:8000', 'name': 'localhost:8000'}
        )

        # Create or update Google OAuth app
        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': options['name'],
                'client_id': options['client_id'],
                'secret': options['client_secret'],
            }
        )

        if not created:
            app.client_id = options['client_id']
            app.secret = options['client_secret']
            app.name = options['name']
            app.save()

        # Add the site to the app
        app.sites.add(site)

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully created Google OAuth application: {app.name}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully updated Google OAuth application: {app.name}')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nGoogle OAuth Configuration:\n'
                f'  Provider: google\n'
                f'  Client ID: {app.client_id}\n'
                f'  Secret: {"*" * len(app.secret)}\n'
                f'  Sites: {", ".join([s.domain for s in app.sites.all()])}\n\n'
                f'📋 Next Steps:\n'
                f'1. Add this redirect URI to Google Console:\n'
                f'   http://localhost:8000/accounts/google/login/callback/\n'
                f'2. Test OAuth at: http://localhost:8000/login/\n'
            )
        )