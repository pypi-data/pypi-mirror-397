from abc import ABC, abstractmethod
from typing import Optional, Any

class BaseIPStrategy(ABC):
    """
    Abstract Base Class (ABC) برای تمام استراتژی‌های شناسایی IP.
    
    این کلاس تضمین می‌کند که تمام استراتژی‌های ما (مثل HeaderStrategy یا ServiceStrategy)
    دارای یک ساختار یکسان هستند.
    """

    @abstractmethod
    def get_ip(self, request: Optional[Any] = None) -> Optional[str]:
        """
        این متد باید در کلاس‌های فرزند پیاده‌سازی شود.
        
        ورودی: 
            request: شیء HttpRequest جنگو (اختیاری)
        خروجی:
            رشته IP یا None در صورتی که پیدا نشود.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"