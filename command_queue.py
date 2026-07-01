# ============================================================
# 👑 ULTIMATE GOLD AGENTIC AI - COMMAND QUEUE SYSTEM
# ============================================================
# ይህ ሞጁል ሁሉንም የትዕዛዝ አያያዝ ተግባራት ያስተዳድራል
# - የትዕዛዝ ወረፋ (Queue) አስተዳደር
# - ቅድሚያ (Priority) አስተዳደር
# - የትዕዛዝ ታሪክ (History) ማስቀመጥ
# - የተጠቃሚ ውሳኔ መመለስ
# - የትዕዛዝ መተርጎም (Parsing)
# - የትዕዛዝ ማረጋገጫ (Validation)
# ============================================================

import threading
import time
import json
import re
from collections import deque, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import uuid
import sqlite3
import os

class CommandPriority:
    """የትዕዛዝ ቅድሚያ ደረጃዎች"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

class CommandStatus:
    """የትዕዛዝ ሁኔታዎች"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class Command:
    """የአንድ ነጠላ ትዕዛዝ ውክልና"""
    def __init__(self, user_id: Union[str, int], command_text: str, priority: int = CommandPriority.NORMAL,
                 metadata: Optional[Dict] = None):
        self.id = str(uuid.uuid4())
        self.user_id = str(user_id)
        self.command_text = command_text
        self.priority = priority
        self.metadata = metadata or {}
        self.status = CommandStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.execution_time = 0.0

    def to_dict(self) -> Dict:
        """የትዕዛዝ መረጃን ወደ መዝገብ መለወጥ"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'command_text': self.command_text,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'error': self.error,
            'execution_time': self.execution_time
        }

    def __repr__(self):
        return f"<Command(id={self.id}, user={self.user_id}, text={self.command_text[:30]}..., status={self.status})>"

class CommandParser:
    """የትዕዛዝ ተርጓሚ - ጽሑፍን ወደ መዋቅር ይቀይራል"""
    
    # የተለያዩ የትዕዛዝ ዓይነቶች መለያ
    PATTERNS = {
        'strike': r'^strike\s+(.+?)(?:\s+(mobile|standard|gold))?(?:\s+(full|modify|recon_only))?$',
        'plan': r'^plan\s+(.+?)(?:\s+(mobile|standard|gold))?$',
        'add': r'^add\s+(\w+)$',
        'remove': r'^remove\s+(\w+)$',
        'improve': r'^improve\s+(\w+)$',
        'auto': r'^auto$',
        'status': r'^status$',
        'help': r'^help$',
        'stop': r'^stop(?:\s+(.+))?$',
        'learn': r'^learn\s+(.+)$',
        'focus': r'^focus\s+port\s+(\d+)$',
        'inject': r'^inject\s+(sql|xss|rce|lfi|ssti)$',
        'speed': r'^speed\s+(fast|slow|stealth)$',
        'modify': r'^modify\s+(.+)$',
        'export': r'^export\s+(json|pdf)$',
        'history': r'^history(?:\s+(\d+))?$',
        'clear': r'^clear$',
    }

    @classmethod
    def parse(cls, raw_command: str) -> Dict[str, Any]:
        """ጽሑፉን ተርጉሞ የተዋቀረ መረጃ ይመልሳል"""
        raw = raw_command.strip()
        if not raw:
            return {'type': 'empty', 'raw': raw}

        # ትዕዛዙ ከ '/' ይጀምራል እንደሆነ አስወግድ (Telegram ስታይል)
        if raw.startswith('/'):
            raw = raw[1:]

        for cmd_type, pattern in cls.PATTERNS.items():
            match = re.match(pattern, raw, re.IGNORECASE)
            if match:
                groups = match.groups()
                return {
                    'type': cmd_type,
                    'raw': raw,
                    'args': groups,
                    'params': {f'arg_{i}': val for i, val in enumerate(groups) if val is not None}
                }
        
        # ያልታወቀ ትዕዛዝ
        return {
            'type': 'unknown',
            'raw': raw,
            'args': (raw,),
            'params': {'arg_0': raw}
        }

class CommandHistory:
    """የትዕዛዝ ታሪክ ማስቀመጫ - SQLite ላይ ያስቀምጣል"""
    def __init__(self, db_path: str = "command_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """የውሂብ ጎታ ሰንጠረዥ መፍጠር"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                command_text TEXT NOT NULL,
                parsed_type TEXT,
                priority INTEGER,
                status TEXT,
                created_at TEXT,
                updated_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                result TEXT,
                error TEXT,
                execution_time REAL
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_id ON command_history(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at ON command_history(created_at)
        ''')
        conn.commit()
        conn.close()

    def save(self, command: Command):
        """ትዕዛዝን ወደ ታሪክ ማስቀመጥ"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO command_history (
                id, user_id, command_text, parsed_type, priority, status,
                created_at, updated_at, started_at, completed_at,
                result, error, execution_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            command.id,
            command.user_id,
            command.command_text,
            getattr(command, 'parsed_type', None),
            command.priority,
            command.status,
            command.created_at.isoformat(),
            command.updated_at.isoformat(),
            command.started_at.isoformat() if command.started_at else None,
            command.completed_at.isoformat() if command.completed_at else None,
            json.dumps(command.result) if command.result else None,
            command.error,
            command.execution_time
        ))
        conn.commit()
        conn.close()

    def get_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """ለአንድ ተጠቃሚ የታዘዙ ትዕዛዞችን መመለስ"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, command_text, parsed_type, priority, status,
                   created_at, updated_at, started_at, completed_at,
                   result, error, execution_time
            FROM command_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [{
            'id': r[0],
            'user_id': r[1],
            'command_text': r[2],
            'parsed_type': r[3],
            'priority': r[4],
            'status': r[5],
            'created_at': r[6],
            'updated_at': r[7],
            'started_at': r[8],
            'completed_at': r[9],
            'result': r[10],
            'error': r[11],
            'execution_time': r[12]
        } for r in rows]

    def clear_history(self, user_id: str):
        """የአንድን ተጠቃሚ ታሪክ ማጥፋት"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM command_history WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

class CommandQueue:
    """ዋናው የትዕዛዝ ወረፋ ሲስተም"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CommandQueue, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._lock = threading.Lock()
        self._queues = defaultdict(deque)  # በቅድሚያ የተከፋፈለ
        self._all_commands = []  # ሁሉንም ለማስተዳደር
        self._processing = False
        self._history = CommandHistory()
        self._command_map = {}  # id -> Command
        self._user_active_commands = defaultdict(set)
        self._stop_requests = defaultdict(bool)
        self._workers = {}
        self._max_workers = 10

    def add_command(self, user_id: Union[str, int], command_text: str,
                    priority: int = CommandPriority.NORMAL,
                    metadata: Optional[Dict] = None) -> Command:
        """አዲስ ትዕዛዝ ወደ ወረፋ መጨመር"""
        with self._lock:
            cmd = Command(user_id, command_text, priority, metadata)
            # ቅድሚያውን በመለየት ወደ ተመጣጣኝ ወረፋ መመደብ
            self._queues[priority].append(cmd)
            self._command_map[cmd.id] = cmd
            self._all_commands.append(cmd)
            self._user_active_commands[str(user_id)].add(cmd.id)
            # ወደ ታሪክ ማስቀመጥ
            self._history.save(cmd)
            # ሂደቱን ማስነሳት ካልሆነ
            if not self._processing:
                self._start_processing()
            return cmd

    def get_next_command(self) -> Optional[Command]:
        """ቀጣዩን ከፍተኛ ቅድሚያ ያለው ትዕዛዝ መውሰድ"""
        with self._lock:
            for priority in sorted(self._queues.keys()):
                if self._queues[priority]:
                    cmd = self._queues[priority].popleft()
                    cmd.status = CommandStatus.PROCESSING
                    cmd.started_at = datetime.now()
                    self._history.save(cmd)
                    return cmd
            return None

    def complete_command(self, command_id: str, result: Any = None, error: Optional[str] = None):
        """ትዕዛዝ ሲጠናቀቅ ማሳወቅ"""
        with self._lock:
            cmd = self._command_map.get(command_id)
            if not cmd:
                return
            cmd.status = CommandStatus.COMPLETED if error is None else CommandStatus.FAILED
            cmd.completed_at = datetime.now()
            cmd.result = result
            cmd.error = error
            cmd.execution_time = (cmd.completed_at - cmd.started_at).total_seconds() if cmd.started_at else 0
            self._history.save(cmd)
            # ከንቁ ትዕዛዞች ላይ ማስወገድ
            if cmd.user_id in self._user_active_commands:
                self._user_active_commands[cmd.user_id].discard(command_id)

    def cancel_command(self, command_id: str):
        """በመጠባበቅ ላይ ያለ ትዕዛዝ መሰረዝ"""
        with self._lock:
            cmd = self._command_map.get(command_id)
            if not cmd:
                return
            if cmd.status == CommandStatus.PENDING:
                # ከወረፋ ላይ ማስወገድ
                for queue in self._queues.values():
                    if cmd in queue:
                        queue.remove(cmd)
                        break
                cmd.status = CommandStatus.CANCELLED
                self._history.save(cmd)
                if cmd.user_id in self._user_active_commands:
                    self._user_active_commands[cmd.user_id].discard(command_id)

    def stop_user_commands(self, user_id: str):
        """ለአንድ ተጠቃሚ ሁሉንም ትዕዛዞች ማቆም"""
        self._stop_requests[str(user_id)] = True
        with self._lock:
            for cmd_id in list(self._user_active_commands.get(str(user_id), [])):
                cmd = self._command_map.get(cmd_id)
                if cmd and cmd.status in (CommandStatus.PENDING, CommandStatus.PROCESSING):
                    if cmd.status == CommandStatus.PENDING:
                        self.cancel_command(cmd_id)
                    else:
                        cmd.status = CommandStatus.CANCELLED
                        self._history.save(cmd)

    def get_user_active_commands(self, user_id: str) -> List[Command]:
        """በአሁን ጊዜ ንቁ የሆኑ የተጠቃሚ ትዕዛዞች ዝርዝር"""
        with self._lock:
            return [self._command_map[cmd_id] for cmd_id in self._user_active_commands.get(str(user_id), [])
                    if cmd_id in self._command_map]

    def get_command(self, command_id: str) -> Optional[Command]:
        return self._command_map.get(command_id)

    def _start_processing(self):
        """የትዕዛዝ ማቀነባበሪያ ክር መጀመር"""
        self._processing = True
        threading.Thread(target=self._process_loop, daemon=True).start()

    def _process_loop(self):
        """በዳራ ላይ የሚሰራ ማቀነባበሪያ loop"""
        while True:
            # ቀጣይ ትዕዛዝ ማግኘት
            cmd = self.get_next_command()
            if cmd is None:
                # ምንም ትዕዛዝ ከሌለ ትንሽ መቆየት
                time.sleep(0.1)
                continue

            # ትዕዛዙን ማስኬድ (ወደ ዋና ሲስተም መላክ)
            # እዚህ ጊዜያዊ ማስመሰል ብቻ ነው
            # በእውነተኛ ሲስተም ውስጥ ወደ ተመሳሳይ ሞጁል ይላካል
            try:
                # ምላሽ ለማስመሰል
                result = f"Processed: {cmd.command_text}"
                self.complete_command(cmd.id, result=result)
            except Exception as e:
                self.complete_command(cmd.id, error=str(e))

            # ትንሽ ማቆሚያ
            time.sleep(0.1)

    def get_metrics(self) -> Dict:
        """የወረፋ መለኪያዎች"""
        with self._lock:
            total_pending = sum(len(q) for q in self._queues.values())
            total_active = len(self._command_map)
            return {
                'total_commands': total_active,
                'pending': total_pending,
                'processing': sum(1 for c in self._command_map.values() if c.status == CommandStatus.PROCESSING),
                'completed': sum(1 for c in self._command_map.values() if c.status == CommandStatus.COMPLETED),
                'failed': sum(1 for c in self._command_map.values() if c.status == CommandStatus.FAILED),
                'cancelled': sum(1 for c in self._command_map.values() if c.status == CommandStatus.CANCELLED),
                'queues': {p: len(q) for p, q in self._queues.items()}
            }

    def clear_all(self):
        """ሁሉንም ትዕዛዞች ማጽዳት"""
        with self._lock:
            self._queues.clear()
            self._command_map.clear()
            self._all_commands.clear()
            self._user_active_commands.clear()

    # ===================== ለተጠቃሚ ምላሽ =====================
    def add_response(self, user_id: str, response: str):
        """ምላሽ ለተጠቃሚ መጨመር (ከሌላ ሞጁል ጋር ለመገናኘት)"""
        # በእውነተኛ ሲስተም ውስጥ ይህ ወደ Telegram bot ይላካል
        print(f"[RESPONSE to {user_id}] {response}")

# ============================================================
# 🏆 ይህ የትዕዛዝ ወረፋ ሲስተም ለGold Level AI ተስተካክሏል
# ============================================================
