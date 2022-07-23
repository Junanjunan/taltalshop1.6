from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):

    help = "This command creates superuser"

    def handle(self, *args, **options):      
        try:        
            User.objects.get(username="taltal")
            self.stdout.write(self.style.SUCCESS(f"Superuser Exists"))
        except:
            User.objects.create_superuser("taltal", "taltalrealty@gmail.com", "a52848625@")
            self.stdout.write(self.style.SUCCESS(f"Superuser Created"))
        
        # try, except 어떤게 잘 실행되었는지는 eb logs --all -> cfn-init-cmd.log를 보면 된다