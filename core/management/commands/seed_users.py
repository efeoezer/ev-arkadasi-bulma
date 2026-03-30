import requests
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile  # Model adın farklıysa (örn: UserProfile) burayı düzelt

class Command(BaseCommand):
    help = 'RandomUser API kullanarak sisteme rastgele bot kullanıcılar ekler'

    def add_arguments(self, parser):
        # Komutu çalıştırırken sayı girmemizi sağlar: python manage.py seed_users 10
        parser.add_argument('total', type=int, help='Eklenecek kullanıcı sayısı')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        url = f'https://randomuser.me/api/?results={total}&nat=tr,en' # Türkiye ve İngiltere odaklı
        
        self.stdout.write(f"{total} adet kullanıcı çekiliyor...")
        
        try:
            response = requests.get(url)
            data = response.json()['results']
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"API hatası: {e}"))
            return

        for person in data:
            username = person['login']['username']
            email = person['email']

            # Kullanıcı daha önce eklenmiş mi kontrol et
            if not User.objects.filter(username=username).exists():
                # 1. Standart Django User oluştur
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123', # Test için standart şifre
                    first_name=person['name']['first'],
                    last_name=person['name']['last']
                )

                # 2. Senin Profile modeline verileri işle
                # Not: Profile modelindeki alan adlarını kendi models.py dosyana göre güncelle!
                Profile.objects.create(
                    user=user,
                    city=person['location']['city'],
                    profile_photo=person['picture']['large'], # URL olarak kaydeder
                    bio=f"Merhaba, ben {person['location']['city']} şehrinde yaşıyorum.",
                    # Algoritman için rastgele 0-1 arası "yaşam tarzı" puanları:
                    cleanliness=round(random.uniform(0, 1), 2),
                    social=round(random.uniform(0, 1), 2),
                    noise_level=round(random.uniform(0, 1), 2)
                )
                
                self.stdout.write(self.style.SUCCESS(f"Eklendi: {username}"))
            else:
                self.stdout.write(self.style.WARNING(f"Atlandı (Zaten var): {username}"))

        self.stdout.write(self.style.SUCCESS('--- İşlem Tamamlandı ---'))


aaaa
