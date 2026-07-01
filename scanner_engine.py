# ============================================================
# 👑 ULTIMATE GOLD AGENTIC AI - SCANNER ENGINE
# ============================================================
# ይህ ሞጁል ሁሉንም የቅኝት (Scanning) ተግባራት ያካትታል
# - ፖርት ቅኝት (Port Scanning)
# - አገልግሎት መለየት (Service Detection)
# - ኦፕሬቲንግ ሲስተም መለየት (OS Fingerprinting)
# - DNS ቅኝት (DNS Enumeration)
# - ንዑስ ጎራዎች መፈለግ (Subdomain Discovery)
# - አውታረ መረብ ቅኝት (Network Scanning)
# - ደመና (Cloud) መለየት
# - SSL/TLS ምርመራ
# - HTTP ራስጌዎች እና ቴክኖሎጂዎች
# - የድር ማውጫ ቅኝት (Directory Brute-forcing)
# ============================================================

import socket
import ssl
import ipaddress
import subprocess
import platform
import time
import threading
import concurrent.futures
from typing import List, Dict, Tuple, Optional, Any, Set
from urllib.parse import urlparse
import re
import dns.resolver
import requests
import json
import base64
import hashlib
from datetime import datetime
import random
from config import config

# ============================================================
# የቅኝት ውጤት ክፍል (ScanResult)
# ============================================================

class ScanResult:
    """የቅኝት ውጤት መዋቅር"""
    def __init__(self):
        self.target = None
        self.hostname = None
        self.ips = []
        self.open_ports = {}
        self.services = {}
        self.banners = {}
        self.os_guess = None
        self.headers = {}
        self.ssl_info = {}
        self.dns_records = {}
        self.subdomains = []
        self.technologies = []
        self.vulnerabilities = []
        self.scan_time = None
        self.raw_data = {}

    def to_dict(self):
        return {
            'target': self.target,
            'hostname': self.hostname,
            'ips': self.ips,
            'open_ports': self.open_ports,
            'services': self.services,
            'banners': self.banners,
            'os_guess': self.os_guess,
            'headers': self.headers,
            'ssl_info': self.ssl_info,
            'dns_records': self.dns_records,
            'subdomains': self.subdomains,
            'technologies': self.technologies,
            'vulnerabilities': self.vulnerabilities,
            'scan_time': self.scan_time.isoformat() if self.scan_time else None,
        }

    def __repr__(self):
        return f"<ScanResult(target={self.target}, open_ports={len(self.open_ports)})>"

# ============================================================
# የፖርት ቅኝት ክፍል (Port Scanner)
# ============================================================

class PortScanner:
    """የፖርት ቅኝት ክፍል - TCP እና SYN (በጥንቃቄ)"""
    def __init__(self, timeout: float = None, max_workers: int = None):
        self.timeout = timeout or config.network.scan_timeout
        self.max_workers = max_workers or config.network.max_scan_workers
        self._open_ports = {}
        self._banners = {}

    def scan_ports(self, target: str, ports: List[int] = None, stealth: bool = False) -> Dict[int, str]:
        """
        ፖርቶችን መቃኘት
        - መደበኛ: TCP ግንኙነት
        - Stealth: ዘገምተኛ እና የዘፈቀደ የጊዜ ክፍተት (gold level)
        """
        if ports is None:
            ports = config.network.default_ports
        self._open_ports = {}
        self._banners = {}

        if stealth:
            self._scan_stealth(target, ports)
        else:
            self._scan_standard(target, ports)

        return self._open_ports

    def _scan_standard(self, target: str, ports: List[int]):
        """መደበኛ TCP ግንኙነት ቅኝት"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_port = {
                executor.submit(self._check_port, target, port): port
                for port in ports
            }
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result(timeout=self.timeout + 1)
                    if result:
                        self._open_ports[port] = result
                except Exception:
                    pass

    def _scan_stealth(self, target: str, ports: List[int]):
        """Stealth ቅኝት (Low & Slow) - ለGold Level"""
        # ፖርቶቹን በዘፈቀደ ቅደም ተከተል አድርግ
        shuffled = ports.copy()
        random.shuffle(shuffled)
        
        for port in shuffled:
            # የዘፈቀደ ማቆሚያ
            time.sleep(random.uniform(config.attack.gold_sleep_between - config.attack.gold_jitter,
                                      config.attack.gold_sleep_between + config.attack.gold_jitter))
            try:
                result = self._check_port(target, port)
                if result:
                    self._open_ports[port] = result
            except:
                pass

    def _check_port(self, target: str, port: int) -> Optional[str]:
        """አንድ ነጠላ ፖርት መፈተሽ"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            if result == 0:
                # አገልግሎቱን ለይ
                service = self._get_service_name(port)
                # ባነር ለማግኘት መሞከር
                banner = self._grab_banner(target, port)
                self._banners[port] = banner
                return service
        except:
            pass
        return None

    def _get_service_name(self, port: int) -> str:
        """በፖርት ቁጥር አገልግሎቱን መለየት"""
        try:
            return socket.getservbyport(port)
        except:
            return f"unknown-{port}"

    def _grab_banner(self, target: str, port: int, timeout: float = 3.0) -> Optional[str]:
        """ባነር መሰብሰብ (በተለይ ለHTTP, SSH, FTP)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((target, port))
            
            # ለተወሰኑ ፖርቶች ልዩ ጥያቄዎች
            if port == 80 or port == 443:
                if port == 443:
                    # SSL ሽፋን
                    ctx = ssl.create_default_context()
                    sock = ctx.wrap_socket(sock, server_hostname=target)
                sock.send(b"HEAD / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                data = sock.recv(1024)
                return data.decode('utf-8', errors='ignore')
            elif port == 22:
                # SSH ባነር
                data = sock.recv(1024)
                return data.decode('utf-8', errors='ignore')
            elif port == 21:
                # FTP
                data = sock.recv(1024)
                return data.decode('utf-8', errors='ignore')
            else:
                # አጠቃላይ ጥያቄ
                sock.send(b"\r\n")
                data = sock.recv(512)
                return data.decode('utf-8', errors='ignore')
            sock.close()
        except:
            return None

# ============================================================
# የአውታረ መረብ ቅኝት (Network Scanner)
# ============================================================

class NetworkScanner:
    """የአውታረ መረብ ቅኝት (Ping Sweep, CIDR)"""
    def __init__(self):
        self._live_hosts = []

    def ping_sweep(self, network: str) -> List[str]:
        """
        በአንድ አውታረ መረብ ውስጥ ሕያው ሆስቶችን መፈለግ
        ይህ መሰረታዊ የICMP ሙከራ ነው
        """
        live = []
        try:
            net = ipaddress.ip_network(network, strict=False)
            # የሚፈቀድ የጊዜ ገደብ ለማስቀረት የክሮች ብዛት መገደብ
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                future_to_ip = {
                    executor.submit(self._ping, str(ip)): str(ip)
                    for ip in net.hosts()
                }
                for future in concurrent.futures.as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    try:
                        if future.result():
                            live.append(ip)
                    except:
                        pass
        except Exception as e:
            pass
        self._live_hosts = live
        return live

    def _ping(self, ip: str) -> bool:
        """አንድ አይፒ መፈተሽ (ICMP)"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            result = subprocess.run(['ping', param, '1', ip], 
                                   capture_output=True, timeout=2)
            return result.returncode == 0
        except:
            return False

    def arp_scan(self, network: str) -> List[str]:
        """
        ARP በመጠቀም የአካባቢ አውታረ መረብ ላይ ያሉ መሳሪያዎችን መፈለግ
        (በጣም ውጤታማ ነው)
        """
        live = []
        try:
            # ለሊኑክስ
            if platform.system().lower() != 'windows':
                result = subprocess.run(['arp-scan', '--local', '--interface', 'eth0'], 
                                        capture_output=True, timeout=10)
                if result.returncode == 0:
                    for line in result.stdout.decode().split('\n'):
                        if '.' in line and 'Interface' not in line and 'Starting' not in line:
                            # የIP አድራሻ ማውጣት
                            match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                            if match:
                                live.append(match.group(1))
        except:
            pass
        return live

# ============================================================
# የDNS ቅኝት (DNS Scanner)
# ============================================================

class DNSScanner:
    """DNS ቅኝት - A, MX, NS, TXT ሪከርዶች እና ንዑስ ጎራዎች"""
    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 2.0
        self.resolver.lifetime = 4.0

    def resolve_a(self, domain: str) -> List[str]:
        """A ሪከርድ ማግኘት"""
        ips = []
        try:
            answers = self.resolver.resolve(domain, 'A')
            for rdata in answers:
                ips.append(str(rdata))
        except:
            pass
        return ips

    def resolve_mx(self, domain: str) -> List[Tuple[str, int]]:
        """MX ሪከርዶች ማግኘት"""
        mx = []
        try:
            answers = self.resolver.resolve(domain, 'MX')
            for rdata in answers:
                mx.append((str(rdata.exchange), rdata.preference))
            mx.sort(key=lambda x: x[1])
        except:
            pass
        return mx

    def resolve_ns(self, domain: str) -> List[str]:
        """NS ሪከርዶች ማግኘት"""
        ns = []
        try:
            answers = self.resolver.resolve(domain, 'NS')
            for rdata in answers:
                ns.append(str(rdata))
        except:
            pass
        return ns

    def resolve_txt(self, domain: str) -> List[str]:
        """TXT ሪከርዶች ማግኘት"""
        txt = []
        try:
            answers = self.resolver.resolve(domain, 'TXT')
            for rdata in answers:
                txt.extend(rdata.strings)
        except:
            pass
        return txt

    def resolve_all(self, domain: str) -> Dict[str, Any]:
        """ሁሉንም ሪከርዶች አንድ ላይ ማግኘት"""
        return {
            'A': self.resolve_a(domain),
            'MX': self.resolve_mx(domain),
            'NS': self.resolve_ns(domain),
            'TXT': self.resolve_txt(domain)
        }

    def find_subdomains(self, domain: str, wordlist: List[str] = None) -> List[str]:
        """ንዑስ ጎራዎችን መፈለግ (የቃላት ዝርዝር በመጠቀም)"""
        if wordlist is None:
            # መሰረታዊ የቃላት ዝርዝር
            wordlist = [
                'www', 'api', 'mail', 'ftp', 'admin', 'dev', 'test', 'stage',
                'app', 'blog', 'shop', 'portal', 'secure', 'vpn', 'dns', 'smtp',
                'pop3', 'imap', 'mysql', 'db', 'backend', 'frontend', 'internal',
                'hr', 'finance', 'support', 'help', 'docs', 'wiki', 'cloud'
            ]
        found = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            future_to_sub = {
                executor.submit(self._check_subdomain, sub, domain): sub
                for sub in wordlist
            }
            for future in concurrent.futures.as_completed(future_to_sub):
                sub = future_to_sub[future]
                try:
                    if future.result():
                        found.append(f"{sub}.{domain}")
                except:
                    pass
        return found

    def _check_subdomain(self, sub: str, domain: str) -> bool:
        """አንድ ንዑስ ጎራ መፈተሽ"""
        try:
            self.resolver.resolve(f"{sub}.{domain}", 'A')
            return True
        except:
            return False

# ============================================================
# የSSL/TLS ቅኝት (SSL Scanner)
# ============================================================

class SSLScanner:
    """SSL/TLS ምስጠራ መረጃ መሰብሰብ"""
    def __init__(self):
        self._context = ssl.create_default_context()

    def scan_ssl(self, host: str, port: int = 443) -> Dict[str, Any]:
        """SSL የምስክር ወረቀት (Certificate) መረጃ ማግኘት"""
        info = {}
        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                with self._context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    info = {
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'serial_number': cert.get('serialNumber'),
                        'version': cert.get('version'),
                        'subjectAltName': cert.get('subjectAltName', []),
                        'cipher': ssock.cipher(),
                        'tls_version': ssock.version(),
                    }
        except Exception as e:
            info['error'] = str(e)
        return info

# ============================================================
# የድር ሰርቨር ቅኝት (Web Scanner)
# ============================================================

class WebScanner:
    """የድር ሰርቨር ራስጌዎች፣ ቴክኖሎጂዎች እና ማውጫዎች መፈለግ"""
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': config.network.default_user_agent
        })

    def get_headers(self, url: str) -> Dict[str, str]:
        """HTTP ራስጌዎች ማግኘት"""
        try:
            resp = self.session.head(url, timeout=5, allow_redirects=True)
            return dict(resp.headers)
        except:
            try:
                resp = self.session.get(url, timeout=5)
                return dict(resp.headers)
            except:
                return {}

    def detect_technologies(self, url: str) -> List[str]:
        """የቴክኖሎጂ ዓይነቶችን መለየት (በራስጌ እና በምላሽ ይዘት)"""
        techs = []
        try:
            resp = self.session.get(url, timeout=5)
            headers = resp.headers
            content = resp.text[:5000]

            # ከራስጌዎች
            server = headers.get('Server', '')
            if 'nginx' in server.lower():
                techs.append('nginx')
            elif 'apache' in server.lower():
                techs.append('apache')
            elif 'IIS' in server:
                techs.append('IIS')
            elif 'cloudflare' in server.lower() or 'cloudflare' in headers.get('CF-RAY', ''):
                techs.append('CloudFlare')

            # ከX-Powered-By
            powered = headers.get('X-Powered-By', '')
            if 'PHP' in powered:
                techs.append('PHP')
            if 'ASP.NET' in powered:
                techs.append('ASP.NET')
            if 'Express' in powered:
                techs.append('Express.js')
            if 'Flask' in powered:
                techs.append('Flask')

            # ከይዘት
            if 'wp-content' in content or 'wordpress' in content.lower():
                techs.append('WordPress')
            if 'drupal' in content.lower():
                techs.append('Drupal')
            if 'joomla' in content.lower():
                techs.append('Joomla')
            if 'react' in content.lower() or 'react-dom' in content:
                techs.append('React')
            if 'angular' in content.lower():
                techs.append('Angular')
            if 'vue' in content.lower():
                techs.append('Vue.js')
            if 'jquery' in content.lower():
                techs.append('jQuery')
            if 'bootstrap' in content.lower():
                techs.append('Bootstrap')

            # ከራስጌ እና ይዘት
            if 'X-Content-Type-Options' in headers:
                techs.append('X-Content-Type-Options')
            if 'X-Frame-Options' in headers:
                techs.append('X-Frame-Options')
            if 'Strict-Transport-Security' in headers:
                techs.append('HSTS')
            if 'Content-Security-Policy' in headers:
                techs.append('CSP')

        except:
            pass
        return list(set(techs))

    def directory_bruteforce(self, url: str, wordlist: List[str] = None) -> List[str]:
        """የድር ማውጫዎች እና ፋይሎች መፈለግ"""
        if wordlist is None:
            wordlist = [
                'admin', 'login', 'wp-admin', 'api', 'v1', 'v2', 'test',
                'dev', 'backup', 'old', 'new', 'data', 'assets', 'static',
                'images', 'js', 'css', 'includes', 'config', 'config.php',
                '.env', '.git', 'robots.txt', 'sitemap.xml', 'favicon.ico',
                'phpinfo.php', 'info.php', 'phpmyadmin', 'mysql'
            ]
        found = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            future_to_path = {
                executor.submit(self._check_path, url, path): path
                for path in wordlist
            }
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    if future.result():
                        found.append(path)
                except:
                    pass
        return found

    def _check_path(self, base_url: str, path: str) -> bool:
        """አንድ መንገድ (path) መፈተሽ"""
        url = base_url.rstrip('/') + '/' + path
        try:
            resp = self.session.head(url, timeout=3, allow_redirects=False)
            if resp.status_code < 400:
                return True
            return False
        except:
            return False

# ============================================================
# የመረጃ አስተዳዳሪ እና መለያ ማግኛ (Cloud & Geolocation)
# ============================================================

class CloudDetector:
    """የደመና አገልግሎት ሰጪዎችን መለየት (AWS, Azure, GCP)"""
    AWS_RANGES = [
        '54.0.0.0/8', '34.192.0.0/12', '35.0.0.0/8', '52.0.0.0/8',
        '13.32.0.0/12', '18.0.0.0/8'
    ]
    AZURE_RANGES = [
        '20.0.0.0/8', '40.0.0.0/10', '13.64.0.0/11', '52.96.0.0/12'
    ]
    GCP_RANGES = [
        '35.184.0.0/14', '35.188.0.0/14', '34.64.0.0/10',
        '130.211.0.0/16', '104.154.0.0/16'
    ]

    @classmethod
    def detect_cloud(cls, ip: str) -> Optional[str]:
        """የIP አድራሻ የደመና አገልግሎት ሰጪ መለየት"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            for network in cls.AWS_RANGES:
                if ip_obj in ipaddress.ip_network(network):
                    return 'AWS'
            for network in cls.AZURE_RANGES:
                if ip_obj in ipaddress.ip_network(network):
                    return 'Azure'
            for network in cls.GCP_RANGES:
                if ip_obj in ipaddress.ip_network(network):
                    return 'GCP'
        except:
            pass
        return None

class Geolocation:
    """የጂኦግራፊ መረጃ ማግኘት (ከIP)"""
    @staticmethod
    def get_location(ip: str) -> Dict[str, Any]:
        try:
            resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('status') == 'success':
                    return {
                        'country': data.get('country'),
                        'countryCode': data.get('countryCode'),
                        'region': data.get('region'),
                        'city': data.get('city'),
                        'timezone': data.get('timezone'),
                        'isp': data.get('isp'),
                        'lat': data.get('lat'),
                        'lon': data.get('lon')
                    }
        except:
            pass
        return {}

# ============================================================
# ዋናው የቅኝት አስተዳዳሪ (Main Scanner Engine)
# ============================================================

class ScannerEngine:
    """ሁሉንም የቅኝት ክፍሎች የሚያጠቃልል ዋና ክፍል"""
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.port_scanner = PortScanner()
        self.network_scanner = NetworkScanner()
        self.dns_scanner = DNSScanner()
        self.ssl_scanner = SSLScanner()
        self.web_scanner = WebScanner()
        self.results = []

    def _log(self, msg, type='info'):
        if self.socketio:
            self.socketio.emit('log', {'msg': f'🔎 {msg}', 'type': type})
        else:
            print(f"[SCAN] {msg}")

    def full_scan(self, target: str, ports: List[int] = None, 
                  stealth: bool = False, subdomain_scan: bool = False,
                  dir_scan: bool = False) -> ScanResult:
        """
        ሙሉ የቅኝት ሂደት አንድ ላይ
        - ፖርት ቅኝት
        - አገልግሎት መለየት
        - DNS
        - SSL (HTTPS)
        - የድር ቴክኖሎጂዎች
        - ንዑስ ጎራዎች
        - የድር ማውጫዎች
        - የደመና መለያ
        - ጂኦሎኬሽን
        """
        self._log(f"Starting full scan on {target} (stealth={stealth})")
        result = ScanResult()
        result.target = target
        result.scan_time = datetime.now()

        # 1. የሆስት መፍታት
        try:
            ips = socket.gethostbyname_ex(target)[2] if hasattr(socket, 'gethostbyname_ex') else [socket.gethostbyname(target)]
            result.ips = ips
            result.hostname = target
        except:
            result.ips = [target]

        # 2. ፖርት ቅኝት
        if ports is None:
            ports = config.network.default_ports
        open_ports = self.port_scanner.scan_ports(target, ports, stealth)
        result.open_ports = open_ports
        result.services = {port: self.port_scanner._get_service_name(port) for port in open_ports}
        result.banners = self.port_scanner._banners

        # 3. የደመና መለያ
        cloud_provider = CloudDetector.detect_cloud(target)
        if cloud_provider:
            result.technologies.append(f"Cloud: {cloud_provider}")

        # 4. SSL (በ443)
        if 443 in open_ports:
            ssl_info = self.ssl_scanner.scan_ssl(target, 443)
            result.ssl_info = ssl_info

        # 5. HTTP ራስጌዎች እና ቴክኖሎጂዎች (ለ80 ወይም 443)
        web_ports = [p for p in open_ports if p in (80, 443, 8080, 8443)]
        for port in web_ports:
            protocol = 'https' if port in (443, 8443) else 'http'
            url = f"{protocol}://{target}:{port}"
            headers = self.web_scanner.get_headers(url)
            if headers:
                result.headers[port] = headers
            techs = self.web_scanner.detect_technologies(url)
            result.technologies.extend(techs)

        # 6. DNS ቅኝት
        try:
            # ጎራ ከሆነ
            if not target.replace('.', '').isdigit():
                dns = self.dns_scanner.resolve_all(target)
                result.dns_records = dns
                # ንዑስ ጎራዎች
                if subdomain_scan:
                    subs = self.dns_scanner.find_subdomains(target)
                    result.subdomains = subs
        except:
            pass

        # 7. የድር ማውጫ ቅኝት
        if dir_scan and web_ports:
            for port in web_ports:
                protocol = 'https' if port in (443, 8443) else 'http'
                url = f"{protocol}://{target}:{port}"
                dirs = self.web_scanner.directory_bruteforce(url)
                if dirs:
                    result.technologies.extend(['dirs_found'])

        # 8. ጂኦሎኬሽን
        geo = Geolocation.get_location(target)
        if geo:
            result.raw_data['geolocation'] = geo

        # 9. የOS መገመት (በባነር)
        os_guess = self._guess_os(result)
        result.os_guess = os_guess

        self.results.append(result)
        self._log(f"Scan complete: {len(open_ports)} open ports, {len(result.technologies)} technologies")
        return result

    def _guess_os(self, result: ScanResult) -> Optional[str]:
        """በባነር እና ራስጌዎች ላይ ተመስርቶ ኦፕሬቲንግ ሲስተም መገመት"""
        banners = ' '.join([b for b in result.banners.values() if b])
        if 'linux' in banners.lower() or 'ubuntu' in banners.lower():
            return 'Linux'
        if 'windows' in banners.lower() or 'IIS' in str(result.headers):
            return 'Windows'
        if 'FreeBSD' in banners:
            return 'FreeBSD'
        if 'Darwin' in banners:
            return 'macOS'
        return None

# ============================================================
# የቅኝት ሂደት ውጤት መላኪያ እና ማስቀመጫ
# ============================================================

class ScanReporter:
    """የቅኝት ውጤት ሪፖርት አዘጋጅ"""
    @staticmethod
    def generate_report(result: ScanResult) -> str:
        """የቅኝት ውጤት በአማርኛ ሪፖርት መልክ"""
        report = []
        report.append("=" * 60)
        report.append("🔍 የቅኝት ሪፖርት (Scan Report)")
        report.append("=" * 60)
        report.append(f"🎯 ዒላማ (Target): {result.target}")
        report.append(f"📅 ጊዜ (Time): {result.scan_time}")
        report.append(f"🌐 አይፒዎች (IPs): {', '.join(result.ips)}")
        report.append("")
        
        if result.open_ports:
            report.append("📡 ክፍት ፖርቶች (Open Ports):")
            for port, service in result.open_ports.items():
                banner = result.banners.get(port, '')
                banner_short = banner[:50] + '...' if len(banner) > 50 else banner
                report.append(f"  - Port {port}: {service} ({banner_short})")
        else:
            report.append("❌ ምንም ክፍት ፖርቶች አልተገኙም.")
        report.append("")

        if result.technologies:
            report.append("🧩 የተገኙ ቴክኖሎጂዎች (Technologies):")
            for tech in result.technologies:
                report.append(f"  - {tech}")
        report.append("")

        if result.dns_records:
            report.append("🌐 DNS ሪከርዶች:")
            for rec_type, values in result.dns_records.items():
                if values:
                    report.append(f"  - {rec_type}: {values}")
        report.append("")

        if result.ssl_info:
            report.append("🔒 SSL/TLS መረጃ:")
            for key, val in result.ssl_info.items():
                if val:
                    report.append(f"  - {key}: {val}")
        report.append("")

        if result.os_guess:
            report.append(f"💻 የተገመተ ኦፕሬቲንግ ሲስተም: {result.os_guess}")
        
        if result.subdomains:
            report.append("📂 የተገኙ ንዑስ ጎራዎች:")
            for sub in result.subdomains[:10]:
                report.append(f"  - {sub}")

        report.append("=" * 60)
        return "\n".join(report)

# ============================================================
# ሙከራ እና ማሳያ
# ============================================================

if __name__ == "__main__":
    # ናሙና ቅኝት
    engine = ScannerEngine()
    result = engine.full_scan("scanme.nmap.org", stealth=True)
    print(ScanReporter.generate_report(result))
    print("\n📊 ውጤት በJSON:")
    print(json.dumps(result.to_dict(), indent=2, default=str))

# ============================================================
# 🏆 ይህ ሙሉ የተሟላ የቅኝት ሞጁል ነው
# ============================================================
