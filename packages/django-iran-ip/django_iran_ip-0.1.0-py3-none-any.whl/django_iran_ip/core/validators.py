import ipaddress
import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class IPValidator:
    """کلاس برای اعتبارسنجی و شناسایی نوع IP"""

    @staticmethod
    def is_valid_ipv4(ip: str) -> bool:
        """بررسی اعتبار IPv4"""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except (ipaddress.AddressValueError, ValueError):
            return False

    @staticmethod
    def is_valid_ipv6(ip: str) -> bool:
        """بررسی اعتبار IPv6"""
        try:
            ipaddress.IPv6Address(ip)
            return True
        except (ipaddress.AddressValueError, ValueError):
            return False

    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """بررسی اینکه IP خصوصی است یا عمومی"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False

    @staticmethod
    def is_reserved_ip(ip: str) -> bool:
        """بررسی اینکه IP رزرو شده است یا خیر"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_reserved or ip_obj.is_loopback
        except ValueError:
            return False

    @staticmethod
    def get_ip_type(ip: str) -> str:
        """تشخیص نوع IP"""
        try:
            ip_obj = ipaddress.ip_address(ip)

            if ip_obj.is_private:
                return "private"
            elif ip_obj.is_loopback:
                return "loopback"
            elif ip_obj.is_reserved:
                return "reserved"
            elif ip_obj.is_multicast:
                return "multicast"
            else:
                return "public"
        except ValueError:
            return "invalid"


class IPGeolocation:
    """کلاس برای شناسایی موقعیت جغرافیایی IP"""

    # سرویس‌های رایگان برای geolocation
    GEOLOCATION_SERVICES = [
        "https://ipapi.co/{ip}/json/",
        "https://ipwhois.app/json/{ip}",
        "http://ip-api.com/json/{ip}",
    ]

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def get_location(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات جغرافیایی IP

        Returns:
            دیکشنری حاوی country, city, isp و...
        """
        for service_url in self.GEOLOCATION_SERVICES:
            try:
                url = service_url.format(ip=ip)
                with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                    response = client.get(url)

                    if response.status_code == 200:
                        data = response.json()
                        return self._normalize_response(data, service_url)
            except Exception as e:
                logger.warning(f"Error getting geolocation from {service_url}: {str(e)}")
                continue

        return None

    def _normalize_response(self, data: Dict, service_url: str) -> Dict[str, Any]:
        """نرمال‌سازی پاسخ سرویس‌های مختلف"""
        normalized = {}

        # ipapi.co format
        if "ipapi.co" in service_url:
            normalized = {
                'country': data.get('country_name'),
                'country_code': data.get('country_code'),
                'city': data.get('city'),
                'region': data.get('region'),
                'isp': data.get('org'),
                'timezone': data.get('timezone'),
            }

        # ipwhois.app format
        elif "ipwhois.app" in service_url:
            normalized = {
                'country': data.get('country'),
                'country_code': data.get('country_code'),
                'city': data.get('city'),
                'region': data.get('region'),
                'isp': data.get('isp'),
                'timezone': data.get('timezone'),
            }

        # ip-api.com format
        elif "ip-api.com" in service_url:
            normalized = {
                'country': data.get('country'),
                'country_code': data.get('countryCode'),
                'city': data.get('city'),
                'region': data.get('regionName'),
                'isp': data.get('isp'),
                'timezone': data.get('timezone'),
            }

        return normalized

    def is_iran_ip(self, ip: str) -> bool:
        """
        بررسی اینکه IP از ایران است یا خیر

        Returns:
            True اگر IP از ایران باشد
        """
        location = self.get_location(ip)

        if location and location.get('country_code'):
            return location['country_code'].upper() == 'IR'

        return False


class IranIPChecker:
    """کلاس تخصصی برای بررسی IP‌های ایرانی"""

    # رنج‌های IP ایران (نمونه - باید کامل شود)
    IRAN_IP_RANGES = [
        "2.176.0.0/12",
        "5.22.0.0/16",
        "5.23.0.0/16",
        "5.52.0.0/16",
        "5.53.0.0/16",
        "5.56.0.0/16",
        "5.57.0.0/16",
        "5.61.16.0/21",
        "5.61.24.0/21",
        "5.63.8.0/21",
        "5.104.0.0/13",
        "5.112.0.0/12",
        "5.144.0.0/13",
        "5.160.0.0/11",
        "5.200.0.0/13",
        "5.208.0.0/12",
        "31.2.128.0/17",
        "31.7.64.0/18",
        "31.24.200.0/21",
        "37.32.0.0/13",
        "37.98.0.0/16",
        "37.99.0.0/16",
        "37.130.192.0/18",
        "37.156.0.0/14",
        "37.191.0.0/16",
        "37.228.131.0/24",
        "46.18.0.0/15",
        "46.32.0.0/11",
        "46.100.0.0/14",
        "46.104.0.0/13",
        "46.143.0.0/16",
        "46.148.0.0/15",
        "46.209.0.0/16",
        "46.224.0.0/12",
        "62.3.12.0/22",
        "77.36.128.0/17",
        "77.81.192.0/19",
        "77.81.230.0/23",
        "78.38.0.0/15",
        "79.127.0.0/17",
        "79.132.192.0/20",
        "79.143.84.0/22",
        "79.175.128.0/18",
        "80.66.176.0/20",
        "80.71.112.0/20",
        "80.75.0.0/20",
        "80.191.0.0/16",
        "80.242.0.0/20",
        "80.253.128.0/19",
        "81.12.0.0/17",
        "81.16.112.0/20",
        "81.28.32.0/19",
        "81.31.160.0/19",
        "81.31.192.0/19",
        "82.99.192.0/18",
        "83.120.0.0/14",
        "83.147.192.0/18",
        "85.15.0.0/18",
        "85.133.128.0/17",
        "85.185.0.0/16",
        "85.198.0.0/19",
        "85.198.48.0/20",
        "86.55.0.0/16",
        "86.104.32.0/20",
        "86.104.80.0/20",
        "86.104.96.0/20",
        "86.105.40.0/21",
        "86.105.128.0/20",
        "86.106.16.0/21",
        "86.106.24.0/21",
        "86.106.64.0/20",
        "86.106.80.0/21",
        "86.106.88.0/21",
        "86.106.136.0/21",
        "86.106.192.0/21",
        "86.107.0.0/20",
        "86.107.16.0/20",
        "86.107.80.0/20",
        "86.107.144.0/20",
        "86.107.172.0/22",
        "86.107.208.0/20",
        "87.107.0.0/16",
        "87.236.16.0/21",
        "87.236.166.0/23",
        "87.236.210.0/23",
        "87.247.152.0/21",
        "88.135.32.0/20",
        "89.32.0.0/16",
        "89.34.20.0/23",
        "89.34.88.0/21",
        "89.38.102.0/23",
        "89.39.186.0/23",
        "89.144.128.0/18",
        "89.165.0.0/17",
        "89.196.0.0/16",
        "89.198.0.0/15",
        "89.221.80.0/20",
        "91.92.104.0/21",
        "91.92.112.0/21",
        "91.92.121.0/24",
        "91.92.122.0/23",
        "91.92.124.0/22",
        "91.92.128.0/22",
        "91.92.132.0/24",
        "91.92.134.0/23",
        "91.92.145.0/24",
        "91.92.146.0/23",
        "91.92.148.0/22",
        "91.93.4.0/24",
        "91.93.18.0/23",
        "91.93.20.0/22",
        "91.93.24.0/21",
        "91.93.32.0/22",
        "91.93.36.0/23",
        "91.93.38.0/24",
        "91.93.40.0/21",
        "91.93.49.0/24",
        "91.93.51.0/24",
        "91.93.52.0/23",
        "91.93.54.0/24",
        "91.93.56.0/21",
        "91.93.119.0/24",
        "91.93.128.0/21",
        "91.93.180.0/22",
        "91.93.184.0/21",
        "91.93.192.0/21",
        "91.93.208.0/21",
        "91.93.216.0/21",
        "91.98.0.0/15",
        "91.106.64.0/19",
        "91.106.96.0/19",
        "91.109.104.0/21",
        "91.109.216.0/21",
        "91.147.64.0/20",
        "91.199.8.0/21",
        "91.199.27.0/24",
        "91.199.28.0/22",
        "91.199.109.0/24",
        "91.212.16.0/21",
        "91.212.168.0/21",
        "91.213.151.0/24",
        "91.213.157.0/24",
        "91.213.172.0/24",
        "91.220.79.0/24",
        "91.220.113.0/24",
        "91.220.163.0/24",
        "91.220.203.0/24",
        "91.220.220.0/24",
        "91.221.116.0/23",
        "91.221.232.0/23",
        "91.224.20.0/23",
        "91.224.110.0/23",
        "91.226.224.0/23",
        "91.227.84.0/22",
        "91.227.246.0/23",
        "91.228.22.0/23",
        "91.228.132.0/23",
        "91.228.168.0/23",
        "91.228.189.0/24",
        "91.230.32.0/24",
        "91.232.64.0/22",
        "91.232.68.0/23",
        "91.232.72.0/22",
        "91.233.56.0/22",
        "91.237.254.0/23",
        "91.238.0.0/24",
        "91.239.14.0/24",
        "91.239.148.0/23",
        "91.240.60.0/22",
        "91.242.44.0/23",
        "92.38.128.0/21",
        "92.114.16.0/22",
        "92.114.48.0/21",
        "92.114.64.0/19",
        "92.119.56.0/22",
        "92.119.68.0/22",
        "92.242.192.0/19",
        "92.249.96.0/19",
        "93.88.0.0/17",
        "93.93.204.0/24",
        "93.113.224.0/20",
        "93.114.16.0/20",
        "93.114.104.0/21",
        "93.115.120.0/21",
        "93.115.144.0/21",
        "93.115.216.0/21",
        "93.116.0.0/19",
        "93.117.0.0/19",
        "93.117.32.0/20",
        "93.117.96.0/19",
        "93.118.96.0/19",
        "93.119.32.0/19",
        "93.119.64.0/19",
        "93.119.208.0/20",
        "93.190.0.0/15",
        "94.101.128.0/20",
        "94.101.176.0/20",
        "94.101.240.0/20",
        "94.139.160.0/19",
        "94.182.0.0/15",
        "95.38.0.0/16",
        "95.80.128.0/18",
        "95.141.0.0/16",
        "95.156.252.0/22",
        "95.216.0.0/15",
    ]

    def __init__(self):
        self.iran_networks = [ipaddress.ip_network(cidr) for cidr in self.IRAN_IP_RANGES]

    def is_iran_ip(self, ip: str) -> bool:
        """
        بررسی اینکه IP در رنج‌های ایران است یا خیر

        Args:
            ip: آدرس IP

        Returns:
            True اگر IP ایرانی باشد
        """
        try:
            ip_obj = ipaddress.ip_address(ip)

            for network in self.iran_networks:
                if ip_obj in network:
                    return True

            return False
        except ValueError:
            return False

    def get_isp_info(self, ip: str) -> Optional[str]:
        """شناسایی ISP ایرانی"""
        # این قسمت نیاز به دیتابیس ISP دارد یا API
        # می‌توان از سرویس‌های geolocation استفاده کرد
        geolocation = IPGeolocation()
        location = geolocation.get_location(ip)

        if location:
            return location.get('isp')

        return None