# ============================================================
# 👑 ULTIMATE GOLD AGENTIC AI - AGENTIC AI CORE
# ============================================================
# ይህ ሞጁል የAI ውሳኔ ሰጪ ስርዓት ነው
# - Reinforcement Learning (በሙከራ መማር)
# - የእውቀት መሰረት (Knowledge Base)
# - የስልት ማመንጫ (Strategy Generator)
# - የውጤት ትንተና (Outcome Analysis)
# - ራስ-መሻሻል (Self-Improvement)
# - የውሳኔ ሰጪ (Decision Engine)
# - ከኢንተርኔት መማር (Internet Learning)
# - የማህደረ ትውስታ (Memory System)
# - የተግባር እቅድ (Action Planning)
# - የስህተት ትንተና (Error Analysis)
# ============================================================

import json
import time
import random
import hashlib
import threading
import sqlite3
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import logging
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

# ============================================================
# የAI ሁኔታዎች (AI States)
# ============================================================

class AIState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    LEARNING = "learning"
    EVOLVING = "evolving"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class AIAction(Enum):
    RECON = "recon"
    SCAN = "scan"
    EXPLOIT = "exploit"
    EXFIL = "exfil"
    WIPE = "wipe"
    WORM = "worm"
    MODIFY = "modify"
    LEARN = "learn"
    EVOLVE = "evolve"
    PLAN = "plan"

# ============================================================
# የእውቀት መዋቅር (Knowledge Structure)
# ============================================================

@dataclass
class KnowledgeItem:
    """አንድ ነጠላ የእውቀት ክፍል"""
    key: str
    value: Any
    confidence: float = 0.5
    source: str = "internal"
    timestamp: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    related_to: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            'key': self.key,
            'value': str(self.value)[:200],
            'confidence': self.confidence,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'access_count': self.access_count,
            'related_to': self.related_to,
            'tags': self.tags
        }

@dataclass
class ActionResult:
    """የተግባር ውጤት"""
    action: str
    target: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    learning_score: float = 0.0
    reward: float = 0.0

    def to_dict(self):
        return {
            'action': self.action,
            'target': self.target,
            'success': self.success,
            'data': str(self.data)[:200] if self.data else None,
            'error': self.error,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat(),
            'learning_score': self.learning_score,
            'reward': self.reward
        }

# ============================================================
# የAI ማህደረ ትውስታ (Memory System)
# ============================================================

class AIMemory:
    """የAI ማህደረ ትውስታ ስርዓት"""
    def __init__(self, max_size: int = 10000):
        self._short_term = deque(maxlen=100)
        self._long_term = {}
        self._max_size = max_size
        self._lock = threading.Lock()
        self._db_path = "ai_memory.db"
        self._init_db()

    def _init_db(self):
        """የውሂብ ጎታ መፍጠር"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT,
                    confidence REAL,
                    source TEXT,
                    timestamp TEXT,
                    access_count INTEGER,
                    tags TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except:
            pass

    def add(self, key: str, value: Any, confidence: float = 0.5,
            source: str = "internal", tags: List[str] = None):
        """አዲስ ትውስታ መጨመር"""
        with self._lock:
            item = KnowledgeItem(
                key=key,
                value=value,
                confidence=confidence,
                source=source,
                tags=tags or []
            )
            self._short_term.append(item)
            self._long_term[key] = item
            self._save_to_db(item)

    def get(self, key: str) -> Optional[KnowledgeItem]:
        """ትውስታን በቁልፍ ማግኘት"""
        with self._lock:
            if key in self._long_term:
                item = self._long_term[key]
                item.access_count += 1
                item.last_accessed = datetime.now()
                return item
            return None

    def search(self, query: str, limit: int = 10) -> List[KnowledgeItem]:
        """ትውስታዎችን በጥያቄ መፈለግ"""
        results = []
        query_lower = query.lower()
        with self._lock:
            for item in self._long_term.values():
                if query_lower in item.key.lower():
                    results.append(item)
                elif item.tags:
                    for tag in item.tags:
                        if query_lower in tag.lower():
                            results.append(item)
                            break
                if len(results) >= limit:
                    break
        # በራስ መተማመን ደረጃ መደርደር
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results

    def get_recent(self, limit: int = 10) -> List[KnowledgeItem]:
        """የቅርብ ጊዜ ትውስታዎችን ማግኘት"""
        with self._lock:
            return sorted(self._short_term, key=lambda x: x.timestamp, reverse=True)[:limit]

    def update_confidence(self, key: str, success: bool):
        """የእውቀት መተማመን ደረጃ ማሻሻል"""
        item = self.get(key)
        if item:
            if success:
                item.confidence = min(1.0, item.confidence + 0.1)
            else:
                item.confidence = max(0.1, item.confidence - 0.05)
            self._save_to_db(item)

    def _save_to_db(self, item: KnowledgeItem):
        """ወደ ውሂብ ጎታ ማስቀመጥ"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO memories (key, value, confidence, source, timestamp, access_count, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.key,
                str(item.value)[:1000],
                item.confidence,
                item.source,
                item.timestamp.isoformat(),
                item.access_count,
                ','.join(item.tags)
            ))
            conn.commit()
            conn.close()
        except:
            pass

    def clear(self):
        """ማህደረ ትውስታን ማጽዳት"""
        with self._lock:
            self._short_term.clear()
            self._long_term.clear()

# ============================================================
# የውሳኔ ሰጪ ስርዓት (Decision Engine)
# ============================================================

class DecisionEngine:
    """የAI ውሳኔ ሰጪ ስርዓት"""
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.memory = AIMemory()
        self._state = AIState.IDLE
        self._current_plan = None
        self._action_history = []
        self._lock = threading.Lock()
        self._logger = logging.getLogger("agentic.decision")
        self._learning_rate = 0.1
        self._exploration_rate = 0.3
        self._successful_actions = []
        self._failed_actions = []

    def _log(self, msg: str, level: str = 'info'):
        if self.socketio:
            self.socketio.emit('log', {'msg': f'🧠 {msg}', 'type': level})
        self._logger.info(msg)

    def get_state(self) -> AIState:
        """የአሁኑን ሁኔታ መመለስ"""
        return self._state

    def set_state(self, state: AIState):
        """ሁኔታን መቀየር"""
        self._state = state
        self._log(f"State changed to: {state.value}", 'info')

    def analyze_situation(self, target: str, open_ports: List[int],
                          services: Dict[int, str], banners: Dict[int, str],
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        ሁኔታውን በመተንተን ምርጥ እርምጃ መምረጥ
        """
        self.set_state(AIState.THINKING)
        self._log(f"Analyzing situation for {target}", 'info')

        analysis = {
            'target': target,
            'open_ports': open_ports,
            'services': services,
            'banners': banners,
            'context': context or {},
            'recommended_action': None,
            'confidence': 0.0,
            'alternatives': [],
            'risk_score': 0.0
        }

        # 1. ከማህደረ ትውስታ መፈለግ
        memory_results = self.memory.search(target)
        if memory_results:
            analysis['memory_hits'] = len(memory_results)
            self._log(f"Found {len(memory_results)} memory matches", 'info')

        # 2. በፖርቶች መሰረት ውሳኔ
        if not open_ports:
            analysis['recommended_action'] = 'recon'
            analysis['confidence'] = 0.8
            analysis['risk_score'] = 0.1
            self._log("No open ports - recommending recon", 'info')
            return analysis

        # 3. አገልግሎቶችን በመለየት
        if 22 in open_ports:
            analysis['recommended_action'] = 'exploit_ssh'
            analysis['confidence'] = 0.7
            analysis['risk_score'] = 0.3
            self._log("SSH service detected - recommending SSH exploit", 'info')

        elif 80 in open_ports or 443 in open_ports:
            analysis['recommended_action'] = 'exploit_web'
            analysis['confidence'] = 0.8
            analysis['risk_score'] = 0.2
            self._log("Web service detected - recommending web exploit", 'info')

        elif 3306 in open_ports or 5432 in open_ports:
            analysis['recommended_action'] = 'exploit_database'
            analysis['confidence'] = 0.6
            analysis['risk_score'] = 0.4
            self._log("Database service detected - recommending database exploit", 'info')

        else:
            # በመረጃ ላይ ተመስርቶ መምረጥ
            analysis['recommended_action'] = 'scan_deep'
            analysis['confidence'] = 0.5
            analysis['risk_score'] = 0.3

        # 4. ተለዋጭ አማራጮች
        analysis['alternatives'] = self._generate_alternatives(open_ports, services)

        # 5. የተጋላጭነት መለየት
        vulnerabilities = self._detect_vulnerabilities(open_ports, services, banners)
        if vulnerabilities:
            analysis['vulnerabilities'] = vulnerabilities
            analysis['confidence'] = min(1.0, analysis['confidence'] + 0.2)

        return analysis

    def _generate_alternatives(self, open_ports: List[int],
                               services: Dict[int, str]) -> List[Dict]:
        """ተለዋጭ አማራጮችን መፍጠር"""
        alternatives = []
        for port in open_ports:
            service = services.get(port, 'unknown')
            if port == 22:
                alternatives.append({'action': 'ssh_bruteforce', 'port': port, 'confidence': 0.6})
                alternatives.append({'action': 'ssh_public_key', 'port': port, 'confidence': 0.3})
            elif port in [80, 443, 8080, 8443]:
                alternatives.append({'action': 'sql_injection', 'port': port, 'confidence': 0.7})
                alternatives.append({'action': 'xss_attack', 'port': port, 'confidence': 0.5})
                alternatives.append({'action': 'directory_traversal', 'port': port, 'confidence': 0.4})
            elif port == 3306:
                alternatives.append({'action': 'mysql_bruteforce', 'port': port, 'confidence': 0.5})
            elif port == 3389:
                alternatives.append({'action': 'rdp_attack', 'port': port, 'confidence': 0.4})
        return alternatives[:5]

    def _detect_vulnerabilities(self, open_ports: List[int],
                                services: Dict[int, str],
                                banners: Dict[int, str]) -> List[Dict]:
        """የተጋላጭነቶችን መለየት"""
        vulnerabilities = []
        for port in open_ports:
            banner = banners.get(port, '')
            service = services.get(port, '')
            banner_lower = banner.lower()
            service_lower = service.lower()

            # SSH
            if port == 22:
                if 'openssh' in service_lower or 'openssh' in banner_lower:
                    if '7.4' in banner or '7.2' in banner:
                        vulnerabilities.append({
                            'name': 'OpenSSH User Enumeration',
                            'cve': 'CVE-2018-15473',
                            'severity': 'medium',
                            'port': port
                        })
                    if '6.0' in banner or '5.9' in banner:
                        vulnerabilities.append({
                            'name': 'OpenSSH Remote Code Execution',
                            'cve': 'CVE-2016-6210',
                            'severity': 'high',
                            'port': port
                        })

            # HTTP
            if port in [80, 443, 8080, 8443]:
                if 'apache' in service_lower or 'apache' in banner_lower:
                    if '2.4.49' in banner or '2.4.50' in banner:
                        vulnerabilities.append({
                            'name': 'Apache Path Traversal',
                            'cve': 'CVE-2021-41773',
                            'severity': 'critical',
                            'port': port
                        })
                    if '2.2.' in banner:
                        vulnerabilities.append({
                            'name': 'Apache Remote Code Execution',
                            'cve': 'CVE-2017-15715',
                            'severity': 'high',
                            'port': port
                        })
                if 'nginx' in service_lower or 'nginx' in banner_lower:
                    if '1.18.0' in banner or '1.19.0' in banner:
                        vulnerabilities.append({
                            'name': 'Nginx Buffer Overflow',
                            'cve': 'CVE-2021-23017',
                            'severity': 'medium',
                            'port': port
                        })
                if 'iis' in service_lower or 'iis' in banner_lower:
                    vulnerabilities.append({
                        'name': 'IIS HTTP.sys Remote Code Execution',
                        'cve': 'CVE-2015-1635',
                        'severity': 'high',
                        'port': port
                    })

            # MySQL
            if port == 3306:
                if '5.7' in banner or '5.6' in banner:
                    vulnerabilities.append({
                        'name': 'MySQL Remote Root',
                        'cve': 'CVE-2016-6662',
                        'severity': 'high',
                        'port': port
                    })

            # PostgreSQL
            if port == 5432:
                if '9.6' in banner or '10.0' in banner:
                    vulnerabilities.append({
                        'name': 'PostgreSQL Remote Code Execution',
                        'cve': 'CVE-2019-10164',
                        'severity': 'high',
                        'port': port
                    })

        return vulnerabilities

    def decide_action(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        በትንተና ላይ ተመስርቶ ውሳኔ መስጠት
        """
        self.set_state(AIState.PLANNING)
        
        # 1. በራስ መተማመን
        confidence = analysis.get('confidence', 0.5)
        risk_score = analysis.get('risk_score', 0.3)

        # 2. ለሙከራ ዝግጁነት
        if random.random() < self._exploration_rate:
            # አዲስ ነገር መሞከር
            alternatives = analysis.get('alternatives', [])
            if alternatives:
                selected = random.choice(alternatives)
                self._log(f"Exploring alternative: {selected['action']} (exploration mode)", 'info')
                return {
                    'action': selected['action'],
                    'confidence': selected.get('confidence', 0.3),
                    'is_exploration': True,
                    'source': 'exploration'
                }

        # 3. የተጋላጭነት ቅድሚያ
        vulnerabilities = analysis.get('vulnerabilities', [])
        if vulnerabilities:
            # ከፍተኛ አደጋ ያላቸውን ቅድሚያ መስጠት
            critical = [v for v in vulnerabilities if v.get('severity') == 'critical']
            high = [v for v in vulnerabilities if v.get('severity') == 'high']
            if critical:
                vuln = critical[0]
                self._log(f"Critical vulnerability detected: {vuln['name']}", 'critical')
                return {
                    'action': 'exploit_vulnerability',
                    'target': vuln,
                    'confidence': 0.9,
                    'is_exploration': False,
                    'source': 'vulnerability_detection'
                }
            if high:
                vuln = high[0]
                self._log(f"High severity vulnerability: {vuln['name']}", 'warning')
                return {
                    'action': 'exploit_vulnerability',
                    'target': vuln,
                    'confidence': 0.8,
                    'is_exploration': False,
                    'source': 'vulnerability_detection'
                }

        # 4. የተጠቆመ እርምጃ
        recommended = analysis.get('recommended_action')
        if recommended and confidence > 0.5:
            self._log(f"Following recommended action: {recommended}", 'info')
            return {
                'action': recommended,
                'confidence': confidence,
                'is_exploration': False,
                'source': 'recommendation'
            }

        # 5. ነባር እርምጃ
        self._log("Using default action: scan_deep", 'info')
        return {
            'action': 'scan_deep',
            'confidence': 0.4,
            'is_exploration': False,
            'source': 'default'
        }

    def execute_action(self, action: Dict[str, Any], target: str,
                        open_ports: List[int]) -> ActionResult:
        """
        ውሳኔውን በመፈጸም ውጤቱን መመለስ
        """
        self.set_state(AIState.EXECUTING)
        action_name = action.get('action', 'unknown')
        start_time = time.time()

        self._log(f"Executing action: {action_name} on {target}", 'info')

        # እዚህ ላይ ትክክለኛውን የጥቃት አፈፃፀም ማስመሰል እንችላለን
        # በእውነተኛ ስርዓት ውስጥ ወደ ተመጣጣኝ ሞጁል ይላካል

        # ለሙከራ ዓላማ የተሳካ ወይም ያልተሳካ ውጤት ማስመሰል
        success = random.random() < 0.7  # 70% የስኬት መጠን
        if 'exploit' in action_name.lower():
            success = random.random() < 0.6
        elif 'scan' in action_name.lower():
            success = random.random() < 0.9

        duration = time.time() - start_time

        result = ActionResult(
            action=action_name,
            target=target,
            success=success,
            duration=duration,
            data={'open_ports': open_ports} if success else None,
            error=None if success else "Action failed"
        )

        # የትምህርት ነጥብ መስጠት
        if success:
            result.reward = 10.0
            result.learning_score = 0.8
            self._successful_actions.append(result)
            self.memory.add(
                key=f"success_{action_name}_{target}",
                value=result.data,
                confidence=0.8,
                source="execution",
                tags=[action_name, target]
            )
        else:
            result.reward = -5.0
            result.learning_score = 0.2
            self._failed_actions.append(result)
            self.memory.add(
                key=f"failure_{action_name}_{target}",
                value=result.error,
                confidence=0.6,
                source="execution",
                tags=[action_name, target, "failure"]
            )

        self.set_state(AIState.IDLE)
        return result

    def learn_from_result(self, result: ActionResult):
        """
        ከውጤት መማር እና የእውቀት መሰረትን ማሻሻል
        """
        self.set_state(AIState.LEARNING)
        
        # ስኬታማ ከሆነ የመማር መጠን መጨመር
        if result.success:
            self._learning_rate = min(1.0, self._learning_rate + 0.01)
            self._exploration_rate = max(0.1, self._exploration_rate - 0.02)
            self.memory.update_confidence(f"success_{result.action}_{result.target}", True)
            self._log(f"Learning from success: {result.action} (learning rate: {self._learning_rate:.2f})", 'success')
        else:
            self._learning_rate = max(0.01, self._learning_rate - 0.005)
            self._exploration_rate = min(0.5, self._exploration_rate + 0.01)
            self.memory.update_confidence(f"failure_{result.action}_{result.target}", False)
            self._log(f"Learning from failure: {result.action} (exploration: {self._exploration_rate:.2f})", 'warning')

        # ወደ ታሪክ መጨመር
        self._action_history.append(result)
        if len(self._action_history) > 1000:
            self._action_history = self._action_history[-500:]

        self.set_state(AIState.IDLE)

    def get_stats(self) -> Dict[str, Any]:
        """የAI ስታቲስቲክስ"""
        total_actions = len(self._action_history)
        successful = len(self._successful_actions)
        failed = len(self._failed_actions)
        return {
            'state': self._state.value,
            'learning_rate': self._learning_rate,
            'exploration_rate': self._exploration_rate,
            'total_actions': total_actions,
            'successful': successful,
            'failed': failed,
            'success_rate': f"{successful / max(1, total_actions) * 100:.1f}%",
            'memory_size': len(self.memory._long_term),
            'recent_actions': [a.to_dict() for a in self._action_history[-5:]]
        }

# ============================================================
# የAI እራስ-ማሻሻል ስርዓት (Self-Improvement System)
# ============================================================

class SelfImprovementEngine:
    """የAI ራስ-ማሻሻል ስርዓት"""
    def __init__(self, socketio=None, decision_engine: DecisionEngine = None):
        self.socketio = socketio
        self.decision_engine = decision_engine
        self._generation = 0
        self._improvements = []
        self._lock = threading.Lock()

    def _log(self, msg: str, level: str = 'info'):
        if self.socketio:
            self.socketio.emit('log', {'msg': f'🧬 {msg}', 'type': level})

    def analyze_performance(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """የAI አፈፃፀም ትንተና"""
        analysis = {
            'needs_improvement': False,
            'suggestions': [],
            'priority': 'low'
        }

        success_rate = float(stats.get('success_rate', '0%').rstrip('%'))

        if success_rate < 30:
            analysis['needs_improvement'] = True
            analysis['suggestions'].append('Increase learning rate - success rate is too low')
            analysis['priority'] = 'critical'
        elif success_rate < 50:
            analysis['needs_improvement'] = True
            analysis['suggestions'].append('Reduce exploration rate - too many failures')
            analysis['priority'] = 'high'
        elif success_rate < 70:
            analysis['needs_improvement'] = True
            analysis['suggestions'].append('Adjust action selection strategy')
            analysis['priority'] = 'medium'
        else:
            analysis['needs_improvement'] = False
            analysis['suggestions'].append('Performance is good, continue current strategy')
            analysis['priority'] = 'low'

        return analysis

    def apply_improvement(self, analysis: Dict[str, Any]):
        """የተጠቆሙ ማሻሻያዎችን መተግበር"""
        if not self.decision_engine:
            return

        self._generation += 1
        self._log(f"Applying improvements (Generation {self._generation})", 'info')

        suggestions = analysis.get('suggestions', [])
        for suggestion in suggestions:
            if 'learning rate' in suggestion.lower():
                self.decision_engine._learning_rate = min(1.0, self.decision_engine._learning_rate + 0.05)
                self._log(f"Adjusted learning rate to {self.decision_engine._learning_rate:.2f}", 'info')
            elif 'exploration rate' in suggestion.lower():
                self.decision_engine._exploration_rate = max(0.05, self.decision_engine._exploration_rate - 0.05)
                self._log(f"Adjusted exploration rate to {self.decision_engine._exploration_rate:.2f}", 'info')

        self._improvements.append({
            'generation': self._generation,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        })

    def get_evolution_history(self) -> List[Dict]:
        """የእድገት ታሪክ መመለስ"""
        return self._improvements

    def get_generation(self) -> int:
        """የአሁኑን ትውልድ ቁጥር መመለስ"""
        return self._generation

# ============================================================
# ዋናው Agentic AI Core
# ============================================================

class AgenticAICore:
    """
    ዋናው Agentic AI ስርዓት
    - የሁሉም ክፍሎች አስተባባሪ
    - አጠቃላይ የAI ባህሪን ያስተዳድራል
    """
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.decision_engine = DecisionEngine(socketio)
        self.improvement_engine = SelfImprovementEngine(socketio, self.decision_engine)
        self._lock = threading.Lock()
        self._is_running = True
        self._background_tasks = []
        self._logger = logging.getLogger("agentic.core")

    def _log(self, msg: str, level: str = 'info'):
        if self.socketio:
            self.socketio.emit('log', {'msg': f'🤖 {msg}', 'type': level})
        self._logger.info(msg)

    def process(self, target: str, open_ports: List[int],
                services: Dict[int, str], banners: Dict[int, str],
                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        ሙሉ የAI ሂደት: ትንተና → ውሳኔ → አፈፃፀም → ትምህርት
        """
        self._log(f"Processing target: {target}", 'info')

        # 1. ሁኔታ ትንተና
        analysis = self.decision_engine.analyze_situation(
            target, open_ports, services, banners, context
        )

        # 2. ውሳኔ መስጠት
        decision = self.decision_engine.decide_action(analysis)

        # 3. ውሳኔን መፈጸም
        result = self.decision_engine.execute_action(
            decision, target, open_ports
        )

        # 4. ከውጤት መማር
        self.decision_engine.learn_from_result(result)

        # 5. አፈፃፀም መተንተን (በየጊዜው)
        if len(self.decision_engine._action_history) % 10 == 0:
            stats = self.decision_engine.get_stats()
            analysis = self.improvement_engine.analyze_performance(stats)
            if analysis['needs_improvement']:
                self.improvement_engine.apply_improvement(analysis)

        return {
            'analysis': analysis,
            'decision': decision,
            'result': result.to_dict(),
            'stats': self.decision_engine.get_stats()
        }

    def get_status(self) -> Dict[str, Any]:
        """የስርዓት ሁኔታ መመለስ"""
        return {
            'state': self.decision_engine.get_state().value,
            'stats': self.decision_engine.get_stats(),
            'generation': self.improvement_engine.get_generation(),
            'evolution_history': self.improvement_engine.get_evolution_history()[-5:],
            'memory_stats': {
                'size': len(self.decision_engine.memory._long_term),
                'short_term_size': len(self.decision_engine.memory._short_term)
            }
        }

    def stop(self):
        """ስርዓትን ማቆም"""
        self._is_running = False
        self._log("Agentic AI Core stopped", 'info')

    def start_background_learning(self, interval: int = 60):
        """በዳራ ላይ የመማር ሂደት መጀመር"""
        def background_loop():
            while self._is_running:
                time.sleep(interval)
                stats = self.decision_engine.get_stats()
                analysis = self.improvement_engine.analyze_performance(stats)
                if analysis['needs_improvement']:
                    self.improvement_engine.apply_improvement(analysis)
                    self._log(f"Background learning applied (Gen {self.improvement_engine.get_generation()})", 'info')

        thread = threading.Thread(target=background_loop, daemon=True)
        thread.start()
        self._background_tasks.append(thread)

    def learn_from_internet(self, topic: str) -> Dict[str, Any]:
        """
        ከኢንተርኔት መማር (የድር መረጃ መሰብሰብ)
        """
        self._log(f"Learning from internet about: {topic}", 'info')
        
        try:
            # DuckDuckGo API
            resp = requests.get(
                f"https://api.duckduckgo.com/?q={topic}&format=json",
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                abstract = data.get('AbstractText', '')
                if abstract:
                    self.decision_engine.memory.add(
                        key=f"internet_{topic}",
                        value=abstract,
                        confidence=0.7,
                        source="internet",
                        tags=[topic, "internet_learning"]
                    )
                    self._log(f"Learned from internet: {abstract[:100]}...", 'success')
                    return {'status': 'success', 'data': abstract}

            # Fallback: Wikipedia
            wiki_resp = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}",
                timeout=5
            )
            if wiki_resp.status_code == 200:
                wiki_data = wiki_resp.json()
                extract = wiki_data.get('extract', '')
                if extract:
                    self.decision_engine.memory.add(
                        key=f"wikipedia_{topic}",
                        value=extract,
                        confidence=0.8,
                        source="wikipedia",
                        tags=[topic, "internet_learning"]
                    )
                    self._log(f"Learned from Wikipedia: {extract[:100]}...", 'success')
                    return {'status': 'success', 'data': extract}

        except Exception as e:
            self._log(f"Internet learning failed: {e}", 'error')
            return {'status': 'error', 'error': str(e)}

        return {'status': 'no_data', 'message': 'No information found'}

# ============================================================
# የአለም አቀፍ ኢንስታንስ
# ============================================================

_agentic_instance = None
_agentic_lock = threading.Lock()

def get_agentic_ai(socketio=None) -> AgenticAICore:
    """የአለም አቀፍ Agentic AI ኢንስታንስ መመለስ"""
    global _agentic_instance
    if _agentic_instance is None:
        with _agentic_lock:
            if _agentic_instance is None:
                _agentic_instance = AgenticAICore(socketio)
    return _agentic_instance

# ============================================================
# ሙከራ እና ማሳያ
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("👑 ULTIMATE GOLD AGENTIC AI - AGENTIC CORE TEST")
    print("=" * 60)

    core = get_agentic_ai()
    
    # ናሙና ሂደት
    print("\n📝 Testing Agentic AI Core...")
    
    result = core.process(
        target="192.168.1.1",
        open_ports=[22, 80, 443, 3306],
        services={22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL"},
        banners={22: "OpenSSH 7.4", 80: "Apache 2.4.49", 443: "nginx 1.18.0", 3306: "MySQL 5.7"},
        context={"type": "server"}
    )

    print("\n📊 Process Result:")
    print(json.dumps(result, indent=2, default=str))

    print("\n📊 System Status:")
    print(json.dumps(core.get_status(), indent=2, default=str))

    print("\n🧬 Testing Internet Learning...")
    learn_result = core.learn_from_internet("cybersecurity")
    print(json.dumps(learn_result, indent=2, default=str))

    print("\n✅ Agentic AI Core test complete!")
    print("=" * 60)

# ============================================================
# 🏆 ይህ ሙሉ የተሟላ የAgentic AI ስርዓት ነው
# ============================================================
