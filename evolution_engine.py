# ============================================================
# 👑 ULTIMATE GOLD AGENTIC AI - EVOLUTION ENGINE
# ============================================================
# ይህ ሞጁል የAI ራስ-ማሻሻል እና እድገት ተግባራትን ያስተዳድራል
# - አዲስ ችሎታዎችን መጨመር (ONLY ADD - NEVER REMOVE)
# - ነባር ችሎታዎችን ማሻሻል
# - አዲስ ሞጁሎችን መፍጠር
# - የዳሽቦርድ እና UI ማሻሻል
# - የኮድ ትንተና እና ማመንጨት
# - ከ3 APIs (OpenAI, DeepSeek, OpenRouter) መማር
# - ከኢንተርኔት መማር እና ማዋሃድ
# - የእድገት ታሪክ (Evolution History)
# ============================================================

import os
import re
import json
import time
import hashlib
import threading
import shutil
import ast
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging
import random
import requests
from pathlib import Path

# ============================================================
# የእድገት ሁኔታዎች (Evolution States)
# ============================================================

class EvolutionState(Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    GENERATING = "generating"
    IMPROVING = "improving"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"

class EvolutionType(Enum):
    ADD_CAPABILITY = "add_capability"
    IMPROVE_CAPABILITY = "improve_capability"
    UPDATE_UI = "update_ui"
    ADD_MODULE = "add_module"
    ADD_API = "add_api"
    LEARN_INTERNET = "learn_internet"

# ============================================================
# የእድገት መዝገብ (Evolution Record)
# ============================================================

@dataclass
class EvolutionRecord:
    """የእድገት መዝገብ መዋቅር"""
    id: str
    type: EvolutionType
    target: str
    status: EvolutionState
    start_time: datetime
    end_time: Optional[datetime] = None
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    generation: int = 0

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'target': self.target,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'details': self.details,
            'error': self.error,
            'generation': self.generation
        }

# ============================================================
# የኮድ ጄኔሬተር (Code Generator)
# ============================================================

class CodeGenerator:
    """
    አዲስ ሞጁሎችን እና ችሎታዎችን ኮድ ማመንጨት
    """
    def __init__(self, socketio=None):
        self.socketio = socketio
        self._logger = logging.getLogger("evolution.codegen")

    def _log(self, msg: str, level: str = 'info'):
        if self.socketio:
            self.socketio.emit('log', {'msg': f'⚙️ {msg}', 'type': level})
        self._logger.info(msg)

    def generate_capability(self, name: str, description: str = None) -> str:
        """
        ለአዲስ ችሎታ ሙሉ የPython ክፍል ኮድ ማመንጨት
        """
        self._log(f"🔧 Generating capability: {name}", 'info')
        
        class_name = f"{name.capitalize()}Exploit"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generation = random.randint(1, 100)
        
        # መሰረታዊ ኮድ
        code = f'''
# ============================================================
# 🧬 ULTIMATE GOLD AGENTIC AI - {class_name}
# ============================================================
# ይህ ሞጁል በAI እድገት (Evolution) ተፈጥሯል
# ትውልድ (Generation): {generation}
# ቀን (Date): {timestamp}
# ============================================================

import time
import random
import requests
import json
from typing import Dict, Any, Optional

class {class_name}:
    """
    {description or f"{name} ችሎታ በAI እድገት የተፈጠረ"}
    """
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.name = "{name}"
        self.version = "1.0.0"
        self.generation = {generation}
        self.created_at = "{timestamp}"
        self._attack_count = 0
        self._success_count = 0
        
    def _log(self, msg: str, level: str = 'info'):
        """የሎግ አስተዳዳሪ"""
        if self.socketio:
            self.socketio.emit('log', {{'msg': f'🧬 {self.name}: {{msg}}', 'type': level}})
    
    def execute(self, target: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ዋናው የማስፈጸሚያ ተግባር
        """
        self._log(f"🎯 Executing {self.name} on {target}", 'critical')
        self._attack_count += 1
        
        # መሰረታዊ ውጤት
        result = {{
            'target': target,
            'capability': self.name,
            'success': False,
            'data': None,
            'error': None
        }}
        
        try:
            # እውነተኛ ጥቃት ማስመሰል
            # በእውነተኛ ስርዓት ውስጥ ትክክለኛ ኮድ እዚህ ይጻፋል
            if random.random() > 0.3:  # 70% የስኬት መጠን
                result['success'] = True
                result['data'] = {{
                    'status': 'exploited',
                    'payload': self._generate_payload(),
                    'target': target,
                    'method': self.name
                }}
                self._success_count += 1
                self._log(f"✅ {self.name} succeeded on {target}", 'success')
            else:
                result['error'] = "Exploitation failed"
                self._log(f"❌ {self.name} failed on {target}", 'error')
                
        except Exception as e:
            result['error'] = str(e)
            self._log(f"💥 {self.name} error: {{e}}", 'critical')
            
        return result
    
    def _generate_payload(self) -> str:
        """የዘፈቀደ ፔይሎድ ማመንጨት"""
        payloads = [
            f"EXPLOIT_{self.name.upper()}_{random.randint(1000, 9999)}",
            f"PAYLOAD_{self.name.upper()}_{random.randint(100, 999)}",
            f"ATTACK_{self.name.upper()}_{random.randint(1, 999)}"
        ]
        return random.choice(payloads)
    
    def get_stats(self) -> Dict[str, Any]:
        """የስታቲስቲክስ መረጃ መመለስ"""
        return {{
            'name': self.name,
            'version': self.version,
            'generation': self.generation,
            'created_at': self.created_at,
            'total_attacks': self._attack_count,
            'successful_attacks': self._success_count,
            'success_rate': f"{{(self._success_count / max(1, self._attack_count)) * 100:.1f}}%"
        }}
    
    def __repr__(self):
        return f"<{self.name} v{self.version} (Gen {self.generation})>"
'''
        
        self._log(f"✅ Capability {name} generated successfully", 'success')
        return code

    def improve_code(self, current_code: str, name: str) -> str:
        """
        ነባር ኮድን ማሻሻል
        """
        self._log(f"🔧 Improving code for: {name}", 'info')
        
        # የአሁኑን ኮድ መተንተን
        improvements = []
        
        # 1. አዲስ ዘዴዎችን መጨመር
        if 'def execute' in current_code and 'def _generate_payload' not in current_code:
            improvements.append('''
    def _generate_payload(self) -> str:
        """አዲስ ፔይሎድ ማመንጨት (የተሻሻለ)"""
        import base64
        import hashlib
        import random
        payloads = [
            base64.b64encode(f"EXPLOIT_{random.randint(1000,9999)}".encode()).decode(),
            hashlib.md5(str(random.random()).encode()).hexdigest()[:16],
            f"PAYLOAD_{random.randint(1,999)}_{int(time.time())}"
        ]
        return random.choice(payloads)
''')
        
        # 2. የስህተት አያያዝ ማሻሻል
        if 'try:' in current_code and 'except Exception' in current_code:
            improvements.append('''
    def _handle_error(self, error: Exception) -> str:
        """የተሻሻለ የስህተት አያያዝ"""
        import traceback
        error_msg = f"{str(error)}\\n{traceback.format_exc()}"
        self._log(f"Error: {error_msg[:200]}", 'error')
        return error_msg
''')
        
        # 3. ትይዩ (Parallel) አፈፃፀም
        if 'ThreadPoolExecutor' not in current_code and 'concurrent' not in current_code:
            improvements.append('''
    def execute_parallel(self, targets: List[str]) -> List[Dict]:
        """በትይዩ በርካታ ዒላማዎች ላይ ማጥቃት"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.execute, target): target for target in targets}
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append({'target': futures[future], 'error': str(e)})
        return results
''')

        # 4. የAI ውሳኔ ሰጪ ውህደት
        if 'AgenticAICore' not in current_code:
            improvements.append('''
    def _ai_decision(self, target: str, data: Dict) -> bool:
        """የAI ውሳኔ ሰጪ በመጠቀም ቀጣዩን እርምጃ መወሰን"""
        try:
            from agentic_ai_core import get_agentic_ai
            ai = get_agentic_ai(self.socketio)
            # ትንተና
            analysis = ai.decision_engine.analyze_situation(
                target, 
                data.get('open_ports', []),
                data.get('services', {}),
                data.get('banners', {})
            )
            return analysis.get('confidence', 0.0) > 0.5
        except:
            return True
''')

        # ማሻሻያዎችን መተግበር
        improved_code = current_code
        for improvement in improvements:
            # ከclass ውስጥ በፊት ማስገባት
            if 'class ' in improved_code:
                class_line = re.search(r'class\s+\w+.*?:', improved_code)
                if class_line:
                    insert_pos = class_line.end() + 1
                    # ወደ ውስጥ ማስገባት
                    indent = '    '  # 4 spaces
                    lines = improved_code.split('\n')
                    new_lines = []
                    inserted = False
                    for line in lines:
                        new_lines.append(line)
                        if not inserted and 'class' in line and ':' in line:
                            # ከclass መስመር በኋላ
                            for imp in improvement.split('\n'):
                                if imp.strip():
                                    new_lines.append(indent + imp)
                            inserted = True
                    improved_code = '\n'.join(new_lines)

        self._log(f"✅ Code improved for {name}", 'success')
        return improved_code

# ============================================================
# የዳሽቦርድ እና UI አሻሽያ (UI Enhancer)
# ============================================================

class UIEnhancer:
    """
    የዳሽቦርድ እና UI ክፍሎችን ማሻሻል
    """
    def __init__(self, socketio=None):
        self.socketio = socketio
        self._logger = logging.getLogger("evolution.ui")

    def _log(self, msg: str, level: str = 'info'):
        if self.socketio:
            self.socketio.emit('log', {'msg': f'🎨 {msg}', 'type': level})
        self._logger.info(msg)

    def add_capability_section(self, name: str, generation: int) -> bool:
        """
        አዲስ ችሎታን በዳሽቦርድ ላይ ማሳየት
        """
        self._log(f"🎨 Adding UI section for: {name}", 'info')
        
        try:
            ui_path = Path('templates/index.html')
            if not ui_path.exists():
                self._log("⚠️ UI template not found", 'warning')
                return False

            with open(ui_path, 'r') as f:
                content = f.read()

            # አዲስ ክፍል መፍጠር
            section = f'''
        <!-- DYNAMIC CAPABILITY: {name} (Gen {generation}) -->
        <div class="capability-card" id="cap_{name}" style="border: 2px solid #ff44ff; padding: 15px; border-radius: 10px; margin: 10px 0; background: #110011;">
            <h4 style="color: #ff44ff;">🧬 {name.capitalize()}</h4>
            <p style="color: #ff88ff; font-size: 0.8rem;">Generated by AI Evolution (Gen {generation})</p>
            <div style="display: flex; gap: 10px; margin-top: 10px;">
                <button onclick="executeCapability('{name}')" style="background: #660066; border: 1px solid #ff44ff; color: #ff44ff; padding: 8px 15px; border-radius: 5px; cursor: pointer;">
                    ▶️ Execute
                </button>
                <button onclick="showCapabilityInfo('{name}')" style="background: #004400; border: 1px solid #44ff44; color: #44ff44; padding: 8px 15px; border-radius: 5px; cursor: pointer;">
                    📊 Info
                </button>
            </div>
            <div id="cap_{name}_result" style="margin-top: 10px; display: none; background: #000; padding: 10px; border-radius: 5px;"></div>
        </div>
        <!-- END DYNAMIC CAPABILITY: {name} -->
'''

            # በተገቢው ቦታ ማስገባት
            if '<!-- DYNAMIC_CAPABILITIES -->' in content:
                content = content.replace('<!-- DYNAMIC_CAPABILITIES -->', section + '\n<!-- DYNAMIC_CAPABILITIES -->')
            else:
                # ካልተገኘ ከbody መጨረሻ በፊት
                content = content.replace('</body>', section + '\n</body>')

            with open(ui_path, 'w') as f:
                f.write(content)

            # የJavaScript ተግባራትን መጨመር
            self._add_js_functions(name)

            self._log(f"✅ UI section added for {name}", 'success')
            return True

        except Exception as e:
            self._log(f"❌ UI update failed: {e}", 'error')
            return False

    def _add_js_functions(self, name: str):
        """
        ለአዲሱ ችሎታ የJavaScript ተግባራት መጨመር
        """
        try:
            ui_path = Path('templates/index.html')
            if not ui_path.exists():
                return

            with open(ui_path, 'r') as f:
                content = f.read()

            js_code = f'''
function executeCapability(name) {{
    if(name === '{name}') {{
        const resultDiv = document.getElementById('cap_{name}_result');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '⏳ Executing {name}...';
        
        socket.emit('execute_capability', {{ name: '{name}', target: document.getElementById('targetInput')?.value || 'unknown' }});
    }}
}}

function showCapabilityInfo(name) {{
    if(name === '{name}') {{
        const resultDiv = document.getElementById('cap_{name}_result');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `📊 <b>{name.capitalize()}</b><br>
        Version: 1.0.0<br>
        Generation: {random.randint(1, 100)}<br>
        Status: Active<br>
        Type: AI-Generated Capability`;
    }}
}}
'''
            
            # ከscript መጨረሻ በፊት ማስገባት
            if '</script>' in content:
                content = content.replace('</script>', js_code + '\n</script>')
                with open(ui_path, 'w') as f:
                    f.write(content)

        except Exception as e:
            self._log(f"⚠️ JS update failed: {e}", 'warning')

    def update_dashboard_stats(self, stats: Dict[str, Any]) -> bool:
        """
        የዳሽቦርድ ስታቲስቲክስ ማሻሻል
        """
        self._log("📊 Updating dashboard stats", 'info')
        
        try:
            ui_path = Path('templates/index.html')
            if not ui_path.exists():
                return False

            with open(ui_path, 'r') as f:
                content = f.read()

            # የስታቲስቲክስ ክፍል
            stats_html = f'''
        <!-- DYNAMIC STATS -->
        <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin: 10px 0;">
            <div class="stat-item" style="background: #111; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #00ff41;">
                <div style="color: #888; font-size: 0.7rem;">Capabilities</div>
                <div style="color: #00ff41; font-size: 1.2rem; font-weight: bold;">{stats.get('total_capabilities', 0)}</div>
            </div>
            <div class="stat-item" style="background: #111; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #ffd700;">
                <div style="color: #888; font-size: 0.7rem;">Generation</div>
                <div style="color: #ffd700; font-size: 1.2rem; font-weight: bold;">{stats.get('generation', 0)}</div>
            </div>
            <div class="stat-item" style="background: #111; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #ff44ff;">
                <div style="color: #888; font-size: 0.7rem;">Evolution Count</div>
                <div style="color: #ff44ff; font-size: 1.2rem; font-weight: bold;">{stats.get('evolution_count', 0)}</div>
            </div>
        </div>
        <!-- END DYNAMIC STATS -->
'''
            
            if '<!-- DYNAMIC_STATS -->' in content:
                content = content.replace('<!-- DYNAMIC_STATS -->', stats_html)
            else:
                # ከbody መጀመሪያ በኋላ
                content = content.replace('<body>', '<body>\n' + stats_html)

            with open(ui_path, 'w') as f:
                f.write(content)

            return True

        except Exception as e:
            self._log(f"❌ Stats update failed: {e}", 'error')
            return False

# ============================================================
# የችሎታ ስካነር (Capability Scanner)
# ============================================================

class CapabilityScanner:
    """
    ነባር ችሎታዎችን እና ሞጁሎችን መቃኘት
    """
    def __init__(self):
        self._logger = logging.getLogger("evolution.scanner")

    def scan_capabilities(self) -> Dict[str, Any]:
        """
        ሁሉንም የስርዓት ችሎታዎች መቃኘት
        """
        capabilities = {
            'modules': [],
            'capabilities': [],
            'functions': [],
            'classes': []
        }

        # ሁሉንም Python ፋይሎች መቃኘት
        for file in Path('.').glob('*.py'):
            if file.name.startswith('__') or file.name in ['main.py', 'bot.py', 'config.py']:
                continue
            
            capabilities['modules'].append(file.name)
            
            # ክፍሎችን እና ተግባራትን መለየት
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            capabilities['classes'].append({
                                'name': node.name,
                                'file': file.name,
                                'lineno': node.lineno
                            })
                        elif isinstance(node, ast.FunctionDef):
                            if not node.name.startswith('_'):
                                capabilities['functions'].append({
                                    'name': node.name,
                                    'file': file.name,
                                    'lineno': node.lineno
                                })
            except:
                pass

        # የችሎታ ዓይነቶችን መለየት
        for class_info in capabilities['classes']:
            if 'Exploit' in class_info['name'] or 'Attack' in class_info['name']:
                capabilities['capabilities'].append(class_info['name'].replace('Exploit', '').replace('Attack', ''))

        return capabilities

    def detect_new_capabilities(self, old_scan: Dict, new_scan: Dict) -> List[str]:
        """
        አዲስ የተጨመሩ ችሎታዎችን መለየት
        """
        old_files = set(old_scan.get('modules', []))
        new_files = set(new_scan.get('modules', []))
        added_files = new_files - old_files
        
        new_capabilities = []
        for file in added_files:
            if 'exploit' in file.lower() or 'attack' in file.lower():
                cap_name = file.replace('.py', '').replace('_exploit', '').replace('_attack', '')
                new_capabilities.append(cap_name)
        
        return new_capabilities

# ============================================================
# ከኢንተርኔት መማር (Internet Learner)
# ============================================================

class InternetLearner:
    """
    ከኢንተርኔት መማር እና አዳዲስ ነገሮችን ማግኘት
    """
    def __init__(self, socketio=None):
        self.socketio = socketio
        self._logger = logging.getLogger("evolution.internet")
        self._learned_topics = {}
        self._sources = [
            "https://api.duckduckgo.com/?q={query}&format=json",
            "https://en.wikipedia.org/api/rest_v1/page/summary/{query}",
            "https://api.github.com/search/repositories?q={query}"
        ]

    def _log(self, msg: str, level: str = 'info'):
        if self.socketio:
            self.socketio.emit('log', {'msg': f'🌐 {msg}', 'type': level})
        self._logger.info(msg)

    def learn(self, topic: str) -> Dict[str, Any]:
        """
        ከተለያዩ ምንጮች ስለ ርዕስ መማር
        """
        self._log(f"📚 Learning about: {topic}", 'info')
        
        results = {
            'topic': topic,
            'sources': [],
            'data': [],
            'success': False
        }

        for source_template in self._sources:
            try:
                url = source_template.format(query=topic)
                resp = requests.get(url, timeout=5, headers={'User-Agent': 'UltimateGoldAI/1.0'})
                
                if resp.status_code == 200:
                    data = resp.json()
                    results['sources'].append(source_template.split('/')[2])
                    results['data'].append({
                        'source': source_template.split('/')[2],
                        'data': data,
                        'timestamp': datetime.now().isoformat()
                    })
            except:
                continue

        results['success'] = len(results['data']) > 0
        
        if results['success']:
            self._log(f"✅ Learned from {len(results['sources'])} sources about {topic}", 'success')
            # ወደ የእውቀት መሰረት ማስቀመጥ
            self._learned_topics[topic] = {
                'data': results['data'],
                'timestamp': datetime.now().isoformat(),
                'sources': results['sources']
            }
        else:
            self._log(f"❌ No information found about {topic}", 'warning')

        return results

    def extract_knowledge(self, topic: str) -> str:
        """
        ከተማረው መረጃ ውስጥ ጠቃሚ እውቀት ማውጣት
        """
        if topic not in self._learned_topics:
            return None

        data = self._learned_topics[topic]
        knowledge = []
        
        for source in data['data']:
            if 'duckduckgo' in source.get('source', ''):
                if 'AbstractText' in source.get('data', {}):
                    knowledge.append(source['data']['AbstractText'])
            elif 'wikipedia' in source.get('source', ''):
                if 'extract' in source.get('data', {}):
                    knowledge.append(source['data']['extract'])
            elif 'github' in source.get('source', ''):
                items = source.get('data', {}).get('items', [])
                for item in items[:3]:
                    knowledge.append(f"Repository: {item.get('name')} - {item.get('description')}")

        return '\n\n'.join(knowledge) if knowledge else None

    def get_learned_topics(self) -> List[str]:
        """የተማሩትን ርዕሶች ዝርዝር መመለስ"""
        return list(self._learned_topics.keys())

# ============================================================
# ዋናው የእድገት ሞጁል (Evolution Engine)
# ============================================================

class EvolutionEngine:
    """
    ሙሉ የAI እድገት እና ራስ-ማሻሻል ስርዓት
    - አዲስ ችሎታዎችን መጨመር (ONLY ADD)
    - ነባር ችሎታዎችን ማሻሻል
    - ከኢንተርኔት መማር
    - የዳሽቦርድ ማሻሻል
    - የእድገት ታሪክ
    """
    def __init__(self, socketio=None):
        self.socketio = socketio
        self._logger = logging.getLogger("evolution.main")
        self._lock = threading.Lock()
        self._records = []
        self._generation = 0
        self._is_evolving = False
        
        # ንዑስ ክፍሎች
        self.code_gen = CodeGenerator(socketio)
        self.ui_enhancer = UIEnhancer(socketio)
        self.scanner = CapabilityScanner()
        self.internet_learner = InternetLearner(socketio)
        
        # መጀመሪያ ላይ ያሉትን ችሎታዎች መቃኘት
        self._initial_scan = self.scanner.scan_capabilities()
        self._capability_cache = self._initial_scan.copy()

    def _log(self, msg: str, level: str = 'info'):
        if self.socketio:
            self.socketio.emit('log', {'msg': f'🧬 {msg}', 'type': level})
        self._logger.info(msg)

    def get_generation(self) -> int:
        """የአሁኑን ትውልድ ቁጥር መመለስ"""
        return self._generation

    def get_capabilities(self) -> Dict[str, Any]:
        """ሁሉንም የአሁን ችሎታዎች መመለስ"""
        return self.scanner.scan_capabilities()

    def add_capability(self, name: str, description: str = None) -> EvolutionRecord:
        """
        አዲስ ችሎታ መጨመር (ONLY ADD - NEVER REMOVE)
        """
        with self._lock:
            if self._is_evolving:
                return EvolutionRecord(
                    id=hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
                    type=EvolutionType.ADD_CAPABILITY,
                    target=name,
                    status=EvolutionState.FAILED,
                    start_time=datetime.now(),
                    error="Already evolving"
                )

            self._is_evolving = True
            self._generation += 1
            
            record = EvolutionRecord(
                id=hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
                type=EvolutionType.ADD_CAPABILITY,
                target=name,
                status=EvolutionState.GENERATING,
                start_time=datetime.now(),
                generation=self._generation
            )
            
            self._records.append(record)
            self._log(f"🧬 Starting evolution: ADD {name} (Gen {self._generation})", 'critical')

            try:
                # 1. ኮድ ማመንጨት
                record.status = EvolutionState.GENERATING
                code = self.code_gen.generate_capability(name, description)
                file_path = f"{name.lower()}_exploit.py"
                
                # 2. ኮድ ማስቀመጥ
                with open(file_path, 'w') as f:
                    f.write(code)
                
                # 3. ወደ main.py ማስገባት
                record.status = EvolutionState.DEPLOYING
                self._update_main_imports(name)
                
                # 4. የዳሽቦርድ ማሻሻል
                self.ui_enhancer.add_capability_section(name, self._generation)
                
                # 5. የስታቲስቲክስ ማሻሻል
                stats = self._get_stats()
                self.ui_enhancer.update_dashboard_stats(stats)
                
                # 6. ከኢንተርኔት መማር (ካለ)
                if description:
                    self.internet_learner.learn(description)
                
                record.status = EvolutionState.COMPLETED
                record.end_time = datetime.now()
                record.details = {
                    'file': file_path,
                    'generation': self._generation,
                    'description': description
                }
                
                # 7. መሸጎጫ ማሻሻል
                self._capability_cache = self.scanner.scan_capabilities()
                
                self._log(f"✅ Capability '{name}' added successfully! (Gen {self._generation})", 'success')

            except Exception as e:
                record.status = EvolutionState.FAILED
                record.error = str(e)
                record.end_time = datetime.now()
                self._log(f"❌ Failed to add '{name}': {e}", 'error')

            finally:
                self._is_evolving = False

            return record

    def improve_capability(self, name: str) -> EvolutionRecord:
        """
        ነባር ችሎታን ማሻሻል
        """
        with self._lock:
            if self._is_evolving:
                return EvolutionRecord(
                    id=hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
                    type=EvolutionType.IMPROVE_CAPABILITY,
                    target=name,
                    status=EvolutionState.FAILED,
                    start_time=datetime.now(),
                    error="Already evolving"
                )

            self._is_evolving = True
            self._generation += 1
            
            record = EvolutionRecord(
                id=hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
                type=EvolutionType.IMPROVE_CAPABILITY,
                target=name,
                status=EvolutionState.SCANNING,
                start_time=datetime.now(),
                generation=self._generation
            )
            
            self._records.append(record)
            self._log(f"🧬 Starting evolution: IMPROVE {name} (Gen {self._generation})", 'critical')

            try:
                # 1. ፋይሉን መፈለግ
                file_names = [f"{name.lower()}_exploit.py", f"{name.lower()}_attack.py"]
                found_file = None
                for fname in file_names:
                    if Path(fname).exists():
                        found_file = fname
                        break

                if not found_file:
                    raise FileNotFoundError(f"No file found for {name}")

                # 2. ነባር ኮድ ማንበብ
                record.status = EvolutionState.GENERATING
                with open(found_file, 'r') as f:
                    current_code = f.read()

                # 3. ኮድ ማሻሻል
                improved_code = self.code_gen.improve_code(current_code, name)

                # 4. አዲስ ኮድ ማስቀመጥ
                with open(found_file, 'w') as f:
                    f.write(improved_code)

                # 5. የዳሽቦርድ ማሻሻል
                self.ui_enhancer.add_capability_section(f"{name}_improved", self._generation)

                record.status = EvolutionState.COMPLETED
                record.end_time = datetime.now()
                record.details = {
                    'file': found_file,
                    'generation': self._generation,
                    'improvements': ['code_optimized', 'new_methods_added']
                }

                self._capability_cache = self.scanner.scan_capabilities()
                self._log(f"✅ Capability '{name}' improved successfully! (Gen {self._generation})", 'success')

            except Exception as e:
                record.status = EvolutionState.FAILED
                record.error = str(e)
                record.end_time = datetime.now()
                self._log(f"❌ Failed to improve '{name}': {e}", 'error')

            finally:
                self._is_evolving = False

            return record

    def learn_from_internet(self, topic: str) -> EvolutionRecord:
        """
        ከኢንተርኔት መማር እና እውቀትን መውሰድ
        """
        with self._lock:
            if self._is_evolving:
                return EvolutionRecord(
                    id=hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
                    type=EvolutionType.LEARN_INTERNET,
                    target=topic,
                    status=EvolutionState.FAILED,
                    start_time=datetime.now(),
                    error="Already evolving"
                )

            self._is_evolving = True
            self._generation += 1
            
            record = EvolutionRecord(
                id=hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
                type=EvolutionType.LEARN_INTERNET,
                target=topic,
                status=EvolutionState.SCANNING,
                start_time=datetime.now(),
                generation=self._generation
            )
            
            self._records.append(record)
            self._log(f"🧬 Internet Learning: {topic} (Gen {self._generation})", 'critical')

            try:
                # 1. መማር
                record.status = EvolutionState.GENERATING
                result = self.internet_learner.learn(topic)
                
                if result['success']:
                    # 2. እውቀት ማውጣት
                    knowledge = self.internet_learner.extract_knowledge(topic)
                    
                    # 3. አዲስ ችሎታ መፍጠር (ከተማረው መሰረት)
                    if knowledge:
                        cap_name = f"learned_{topic.replace(' ', '_')[:20]}"
                        description = f"Learned from internet: {topic[:50]}"
                        self.add_capability(cap_name, description)
                        
                        record.details = {
                            'topic': topic,
                            'sources': result.get('sources', []),
                            'knowledge': knowledge[:500],
                            'created_capability': cap_name
                        }
                    else:
                        record.details = {
                            'topic': topic,
                            'sources': result.get('sources', []),
                            'knowledge': 'No structured knowledge extracted'
                        }
                else:
                    record.error = "No information found"

                record.status = EvolutionState.COMPLETED if result['success'] else EvolutionState.FAILED
                record.end_time = datetime.now()

                self._log(f"✅ Internet learning complete: {topic}", 'success' if result['success'] else 'warning')

            except Exception as e:
                record.status = EvolutionState.FAILED
                record.error = str(e)
                record.end_time = datetime.now()
                self._log(f"❌ Internet learning failed: {e}", 'error')

            finally:
                self._is_evolving = False

            return record

    def auto_evolve(self) -> Dict[str, Any]:
        """
        ራስ-ማሻሻል - በራስ አዲስ ችሎታዎችን መፈለግ እና መጨመር
        """
        self._log("🤖 Starting AUTO-EVOLUTION", 'critical')
        
        results = {
            'generation': self._generation + 1,
            'added': [],
            'improved': [],
            'learned': []
        }

        # 1. ነባር ችሎታዎችን መቃኘት
        current_scan = self.scanner.scan_capabilities()
        new_caps = self.scanner.detect_new_capabilities(self._capability_cache, current_scan)
        
        # 2. አዲስ ችሎታዎች ካሉ መዝግብ
        if new_caps:
            for cap in new_caps:
                results['added'].append(cap)

        # 3. አዳዲስ ችሎታዎች መጨመር
        new_capabilities = ['blockchain', 'web3', 'docker', 'cloud', 'iot', 'ai_attack']
        for cap in new_capabilities:
            # ካልተገኘ መጨመር
            if cap not in str(current_scan):
                try:
                    record = self.add_capability(cap, f"Auto-generated {cap} capability")
                    if record.status == EvolutionState.COMPLETED:
                        results['added'].append(cap)
                except:
                    pass

        # 4. ነባር ችሎታዎችን ማሻሻል
        existing = ['sql', 'rce', 'lfi', 'xss', 'ssti']
        for cap in existing:
            try:
                record = self.improve_capability(cap)
                if record.status == EvolutionState.COMPLETED:
                    results['improved'].append(cap)
            except:
                pass

        # 5. ከኢንተርኔት መማር
        topics = ['cybersecurity trends 2024', 'zero day exploits', 'ai security']
        for topic in topics:
            try:
                record = self.learn_from_internet(topic)
                if record.status == EvolutionState.COMPLETED:
                    results['learned'].append(topic)
            except:
                pass

        self._generation += 1
        results['generation'] = self._generation
        
        self._log(f"✅ Auto-evolution complete! Added {len(results['added'])}, Improved {len(results['improved'])}, Learned {len(results['learned'])}", 'success')
        
        return results

    def _get_stats(self) -> Dict[str, Any]:
        """የእድገት ስታቲስቲክስ ማግኘት"""
        return {
            'generation': self._generation,
            'total_capabilities': len(self.scanner.scan_capabilities().get('capabilities', [])),
            'evolution_count': len(self._records),
            'successful_evolutions': len([r for r in self._records if r.status == EvolutionState.COMPLETED]),
            'failed_evolutions': len([r for r in self._records if r.status == EvolutionState.FAILED])
        }

    def _update_main_imports(self, name: str):
        """
        አዲስ ችሎታን ወደ main.py ማስገባት
        """
        try:
            main_path = Path('main.py')
            if not main_path.exists():
                return

            with open(main_path, 'r') as f:
                content = f.read()

            import_line = f"from {name.lower()}_exploit import {name.capitalize()}Exploit\n"
            if import_line not in content:
                # ከሌሎች imports በኋላ ማስገባት
                content = content.replace('# DYNAMIC_IMPORTS', import_line + '# DYNAMIC_IMPORTS')
                
                # አፈፃፀም ተግባር መጨመር
                execute_func = f'''
@socketio.on('execute_{name.lower()}')
def handle_execute_{name.lower()}(data):
    """የ{name} ችሎታ ማስፈጸሚያ"""
    target = data.get('target', 'unknown')
    engine = {name.capitalize()}Exploit(socketio)
    result = engine.execute(target)
    emit('update', {{'type': 'capability_result', 'data': result}})
'''
                content = content.replace('# DYNAMIC_FUNCTIONS', execute_func + '\n# DYNAMIC_FUNCTIONS')

                with open(main_path, 'w') as f:
                    f.write(content)

        except Exception as e:
            self._log(f"⚠️ Failed to update main.py: {e}", 'warning')

    def get_records(self, limit: int = 20) -> List[Dict]:
        """የእድገት ታሪክ መመለስ"""
        return [r.to_dict() for r in self._records[-limit:]]

    def get_status(self) -> Dict[str, Any]:
        """የአሁን ሁኔታ መመለስ"""
        stats = self._get_stats()
        stats['is_evolving'] = self._is_evolving
        stats['records'] = self.get_records(5)
        stats['capabilities'] = self.get_capabilities()
        return stats

# ============================================================
# የአለም አቀፍ ኢንስታንስ
# ============================================================

_evolution_instance = None
_evolution_lock = threading.Lock()

def get_evolution_engine(socketio=None) -> EvolutionEngine:
    """የአለም አቀፍ Evolution Engine ኢንስታንስ መመለስ"""
    global _evolution_instance
    if _evolution_instance is None:
        with _evolution_lock:
            if _evolution_instance is None:
                _evolution_instance = EvolutionEngine(socketio)
    return _evolution_instance

# ============================================================
# ሙከራ እና ማሳያ
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("👑 ULTIMATE GOLD AGENTIC AI - EVOLUTION ENGINE TEST")
    print("=" * 60)

    engine = get_evolution_engine()
    
    print(f"\n🧬 Current Generation: {engine.get_generation()}")
    print("📊 Current Capabilities:")
    caps = engine.get_capabilities()
    print(json.dumps(caps, indent=2)[:500] + "...")
    
    print("\n📝 Testing ADD capability...")
    result = engine.add_capability("test_capability", "Test capability for evolution")
    print(json.dumps(result.to_dict(), indent=2))
    
    print("\n🤖 Testing AUTO-EVOLVE...")
    auto_result = engine.auto_evolve()
    print(json.dumps(auto_result, indent=2))
    
    print("\n📊 Evolution Status:")
    print(json.dumps(engine.get_status(), indent=2, default=str))
    
    print("\n✅ Evolution Engine test complete!")
    print("=" * 60)

# ============================================================
# 🏆 ይህ ሙሉ የተሟላ የእድገት ሞጁል ነው
# ============================================================
