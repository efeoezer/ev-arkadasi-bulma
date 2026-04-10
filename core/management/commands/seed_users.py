from django.core.management.base import BaseCommand
from core.services import generate_bot_users

class Command(BaseCommand):
    help = 'Services katmanını kullanarak güvenli ve tam uyumlu bot kullanıcılar ekler'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Eklenecek kullanıcı sayısı')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        self.stdout.write(self.style.SUCCESS(f"{total} adet tam donanımlı bot oluşturuluyor..."))
        
        try:
            generate_bot_users(total)
            self.stdout.write(self.style.SUCCESS(f'--- {total} Bot Başarıyla Eklendi (MBTI, Foto ve Tercihler Dahil) ---'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Hata oluştu: {str(e)}"))
