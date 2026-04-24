# okodi_agri/shop/management/commands/add_sample_products.py

from django.core.management.base import BaseCommand
from shop.models import Category, Product

class Command(BaseCommand):
    help = 'Adds sample products to the database'

    def handle(self, *args, **kwargs):
        # Create categories
        categories = {
            'seeds': Category.objects.create(name='Seeds', slug='seeds', description='High-quality seeds for various crops'),
            'fertilizers': Category.objects.create(name='Fertilizers', slug='fertilizers', description='Organic and chemical fertilizers'),
            'tools': Category.objects.create(name='Farm Tools', slug='tools', description='Modern farming equipment and tools'),
            'pesticides': Category.objects.create(name='Pesticides', slug='pesticides', description='Crop protection products'),
        }
        
        self.stdout.write('Categories created successfully')
        
        # Sample products
        products_data = [
            {
                'name': 'Maize Seeds (Hybrid)',
                'category': categories['seeds'],
                'description': 'High-yield hybrid maize seeds resistant to common diseases. Germination rate: 95%',
                'price': 25000,
                'stock_quantity': 500,
                'weight': 2.0,
                'measurement': '2kg pack',
                'supplier_name': 'Uganda Seed Centre',
                'supplier_location': 'Kampala, Uganda',
                'product_type': 'seeds',
            },
            {
                'name': 'Organic Fertilizer (10kg)',
                'category': categories['fertilizers'],
                'description': '100% organic compost fertilizer enriched with essential nutrients for healthy plant growth',
                'price': 45000,
                'stock_quantity': 200,
                'weight': 10.0,
                'measurement': '10kg bag',
                'supplier_name': 'Green Farm Supplies',
                'supplier_location': 'Jinja, Uganda',
                'product_type': 'fertilizers',
            },
            {
                'name': 'Farm Hoe (Heavy Duty)',
                'category': categories['tools'],
                'description': 'Durable farm hoe made from hardened steel. Perfect for weeding and tilling',
                'price': 35000,
                'stock_quantity': 150,
                'weight': 1.5,
                'measurement': 'Standard size',
                'supplier_name': 'AgriTools Uganda',
                'supplier_location': 'Mbale, Uganda',
                'product_type': 'tools',
            },
            {
                'name': 'Pesticide (Crop Guard)',
                'category': categories['pesticides'],
                'description': 'Broad-spectrum pesticide for controlling common crop pests. Safe for vegetables',
                'price': 55000,
                'stock_quantity': 100,
                'weight': 1.0,
                'measurement': '1 liter bottle',
                'supplier_name': 'Crop Protection Ltd',
                'supplier_location': 'Kampala, Uganda',
                'product_type': 'pesticides',
            },
            {
                'name': 'Tomato Seeds (FreshPro)',
                'category': categories['seeds'],
                'description': 'Premium tomato seeds producing large, sweet tomatoes. Harvest in 75 days',
                'price': 15000,
                'stock_quantity': 300,
                'weight': 0.1,
                'measurement': '100g pack',
                'supplier_name': 'Uganda Seed Centre',
                'supplier_location': 'Kampala, Uganda',
                'product_type': 'seeds',
            },
            {
                'name': 'Watering Can (15L)',
                'category': categories['tools'],
                'description': 'Galvanized steel watering can with rose shower head. Perfect for garden irrigation',
                'price': 65000,
                'stock_quantity': 80,
                'weight': 2.5,
                'measurement': '15 liters',
                'supplier_name': 'Garden Tools Uganda',
                'supplier_location': 'Kampala, Uganda',
                'product_type': 'tools',
            },
        ]
        
        for product_data in products_data:
            Product.objects.create(**product_data)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {len(products_data)} sample products'))