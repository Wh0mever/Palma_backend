from src.product.models import Product, Category


def delete_industry(industry):
    industry.is_deleted = True
    industry.save()
    categories = Category.objects.filter(industry=industry)
    products = Product.objects.filter(category__in=categories)
    categories.update(is_deleted=True)
    products.update(is_deleted=True)


def delete_category(category):
    category.is_deleted = True
    category.save()
    products = Product.objects.filter(category=category)
    products.update(is_deleted=True)
