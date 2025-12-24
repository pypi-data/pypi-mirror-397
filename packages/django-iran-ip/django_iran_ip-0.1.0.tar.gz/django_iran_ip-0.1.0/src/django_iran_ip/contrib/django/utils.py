from django_iran_ip.core.resolver import IPResolver

def get_client_ip(request) -> str:
    """
    تابع کمکی برای گرفتن آی‌پی در Viewها بدون نیاز به Middleware
    """
    resolver = IPResolver()
    return resolver.get_client_ip(request)