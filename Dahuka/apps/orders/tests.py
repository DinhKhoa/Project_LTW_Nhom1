from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.products.models import Product, ProductImage
from apps.categories.models import Category
from apps.orders.models import Order, OrderItem
from apps.orders.services import OrderService


class OrderModelTests(TestCase):
    """Test Order model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.category = Category.objects.create(
            name='Test Category',
            code='TEST001'
        )
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=100000,
            stock=50
        )
    
    def test_order_creation(self):
        """Test basic order creation"""
        order = Order.objects.create(
            customer=self.user,
            full_name='John Doe',
            phone='0123456789',
            address='123 Test Street',
            total_amount=100000,
        )
        self.assertEqual(order.customer, self.user)
        self.assertEqual(order.status, 'pending')
        self.assertTrue(order.id)
    
    def test_order_item_creation(self):
        """Test OrderItem creation"""
        order = Order.objects.create(
            customer=self.user,
            full_name='John Doe',
            phone='0123456789',
            address='123 Test Street',
            total_amount=100000,
        )
        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=100000,
        )
        self.assertEqual(item.order, order)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)


class ProductSlugTests(TestCase):
    """Test Product slug generation and uniqueness"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            code='TEST001'
        )
    
    def test_slug_generation(self):
        """Test that slug is auto-generated from name"""
        product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=100000,
            stock=50
        )
        self.assertEqual(product.slug, 'test-product')
    
    def test_slug_uniqueness_collision(self):
        """Test slug uniqueness when there's a collision"""
        # Create first product
        product1 = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=100000,
            stock=50,
            sku='SKU001'
        )
        self.assertEqual(product1.slug, 'test-product')
        
        # Create second product with same name - should get unique slug
        product2 = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=100000,
            stock=50,
            sku='SKU002'
        )
        self.assertEqual(product2.slug, 'test-product-1')
    
    def test_slug_uniqueness_multiple_collisions(self):
        """Test slug uniqueness with multiple collisions"""
        # Create 3 products with same name
        for i in range(3):
            product = Product.objects.create(
                name='Test Product',
                category=self.category,
                price=100000,
                stock=50,
                sku=f'SKU{i:03d}'
            )
            if i == 0:
                self.assertEqual(product.slug, 'test-product')
            else:
                self.assertEqual(product.slug, f'test-product-{i}')


class CategorySlugTests(TestCase):
    """Test Category slug generation"""
    
    def test_category_slug_generation(self):
        """Test that category slug is auto-generated"""
        category = Category.objects.create(
            name='Test Category',
            code='TEST001'
        )
        self.assertEqual(category.slug, 'test-category')
    
    def test_category_slug_uniqueness(self):
        """Test category slug uniqueness"""
        category1 = Category.objects.create(
            name='Test Category',
            code='TEST001'
        )
        category2 = Category.objects.create(
            name='Test Category',
            code='TEST002'
        )
        self.assertEqual(category1.slug, 'test-category')
        self.assertEqual(category2.slug, 'test-category-1')
