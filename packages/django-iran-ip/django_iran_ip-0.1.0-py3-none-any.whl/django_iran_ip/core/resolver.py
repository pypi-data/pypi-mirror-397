from typing import Optional, List, Dict
from .base import BaseIPStrategy
from .strategies import HeaderStrategy, ServiceStrategy, CachedServiceStrategy
import logging

logger = logging.getLogger(__name__)


class IPResolver:
    """
    کلاس اصلی برای شناسایی IP با استفاده از استراتژی‌های مختلف
    """

    def __init__(self, strategies: Optional[List[BaseIPStrategy]] = None, enable_cache: bool = True):
        """
        Args:
            strategies: لیست استراتژی‌ها به ترتیب اولویت
            enable_cache: فعال‌سازی کش برای ServiceStrategy
        """
        if strategies:
            self.strategies = strategies
        else:
            # اولویت با هدر است چون هزینه‌ای ندارد، اگر نشد سراغ API می‌رود
            header_strategy = HeaderStrategy()

            if enable_cache:
                service_strategy = CachedServiceStrategy(
                    base_strategy=ServiceStrategy(use_iran_services=True),
                    cache_duration=3600  # 1 ساعت
                )
            else:
                service_strategy = ServiceStrategy(use_iran_services=True)

            self.strategies = [header_strategy, service_strategy]

    def get_client_ip(self, request=None) -> Optional[str]:
        """
        دریافت IP کلاینت با استفاده از استراتژی‌های تعریف شده

        Args:
            request: شیء HttpRequest جنگو

        Returns:
            IP address یا None
        """
        for strategy in self.strategies:
            try:
                ip = strategy.get_ip(request)
                if ip:
                    logger.debug(f"IP found using {strategy.__class__.__name__}: {ip}")
                    return ip
            except Exception as e:
                logger.warning(f"Error in {strategy.__class__.__name__}: {str(e)}")
                continue

        logger.warning("No IP address found using any strategy")
        return None

    def get_client_info(self, request=None) -> Dict[str, Optional[str]]:
        """
        دریافت اطلاعات کامل کلاینت شامل IP و استراتژی استفاده شده

        Returns:
            دیکشنری حاوی ip و strategy_used
        """
        for strategy in self.strategies:
            try:
                ip = strategy.get_ip(request)
                if ip:
                    return {
                        'ip': ip,
                        'strategy_used': strategy.__class__.__name__,
                        'is_valid': self._is_valid_ip(ip)
                    }
            except Exception as e:
                logger.warning(f"Error in {strategy.__class__.__name__}: {str(e)}")
                continue

        return {
            'ip': None,
            'strategy_used': None,
            'is_valid': False
        }

    def _is_valid_ip(self, ip: str) -> bool:
        """بررسی اعتبار IP address"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            return all(0 <= int(part) <= 255 for part in parts)
        except (ValueError, AttributeError):
            return False