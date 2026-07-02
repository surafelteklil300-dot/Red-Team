# ============================================================
# 👑 ULTIMATE GOLD AGENTIC AI - MAIN APPLICATION SERVER
# ============================================================
# ይህ ፋይል ሁሉንም የስርዓት ክፍሎች አንድ ላይ ያስተባብራል
# - Flask Web Server
# - SocketIO Real-time Communication
# - ሁሉንም ሞጁሎች ማስጀመር እና ማስተዳደር
# - WebSocket ኢቨንቶች አያያዝ
# - የዳሽቦርድ አገልግሎት
# - በዳራ ሂደቶች (Background Tasks)
# - ስህተት አያያዝ
# - የስርዓት ህይወት አስተዳደር (Lifecycle Management)
# ============================================================

import os
import sys
import json
import time
import threading
import asyncio
import logging
import signal
import traceback
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import random
import base64
import hashlib

# ===== Flask Web Framework =====
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

# ===== Environment =====
from dotenv import load_dotenv

# ===== System Modules =====
from command_queue import CommandQueue
from config import config
from api_integration import APIIntegration, get_api
from scanner_engine import RealScanner, DiscoveryEngine, ScanReporter
from agentic_ai_core import get_agentic_ai
from attack_engine import get_attack_engine
from evolution_engine import get_evolution_engine
from planner_engine import DeepPlanningEngine

# ============================================================
# ሎግ ማዋቀር (Logging Setup)
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

# ============================================================
# የFlask አፕሊኬሽን መፍጠር
# ============================================================

load_dotenv()

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# CORS ማዋቀር
CORS(app, resources={r"/*": {"origins": "*"}})

# SocketIO ማዋቀር (ከተለዋዋጭ አካባቢ ጋር)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25,
    always_connect=True,
    logger=True,
    engineio_logger=True
)

# ============================================================
# የስርዓት ክፍሎች መጫን (System Components)
# ============================================================

# የትዕዛዝ ወረፋ
command_queue = CommandQueue()

# API ውህደት
api = get_api()

# Scanner ሞጁል
scanner = RealScanner(socketio)

# Agentic AI Core
agentic_ai = get_agentic_ai(socketio)

# Attack Engine
attack_engine = get_attack_engine(socketio)

# Evolution Engine
evolution_engine = get_evolution_engine(socketio)

# Planning Engine
planner = DeepPlanningEngine(socketio)

# ============================================================
# የስርዓት ሁኔታ አስተዳዳሪ (System State Manager)
# ============================================================

class SystemState:
    """የስርዓት አለም አቀፍ ሁኔታ አስተዳዳሪ"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SystemState, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.start_time = datetime.now()
        self.active_connections = set()
        self.active_attacks = {}
        self.active_scans = {}
        self.system_events = []
        self._lock = threading.Lock()

    def add_connection(self, sid: str):
        with self._lock:
            self.active_connections.add(sid)

    def remove_connection(self, sid: str):
        with self._lock:
            self.active_connections.discard(sid)

    def get_connections_count(self) -> int:
        with self._lock:
            return len(self.active_connections)

    def add_attack(self, attack_id: str, data: Dict):
        with self._lock:
            self.active_attacks[attack_id] = {
                'data': data,
                'started': datetime.now(),
                'status': 'running'
            }

    def update_attack(self, attack_id: str, status: str, result: Any = None):
        with self._lock:
            if attack_id in self.active_attacks:
                self.active_attacks[attack_id]['status'] = status
                if result is not None:
                    self.active_attacks[attack_id]['result'] = result
                    self.active_attacks[attack_id]['completed'] = datetime.now()

    def remove_attack(self, attack_id: str):
        with self._lock:
            self.active_attacks.pop(attack_id, None)

    def add_event(self, event: Dict):
        with self._lock:
            self.system_events.append({
                **event,
                'timestamp': datetime.now().isoformat()
            })
            if len(self.system_events) > 1000:
                self.system_events = self.system_events[-500:]

    def get_status(self) -> Dict:
        with self._lock:
            return {
                'uptime': str(datetime.now() - self.start_time),
                'connections': len(self.active_connections),
                'active_attacks': len(self.active_attacks),
                'active_scans': len(self.active_scans),
                'events_count': len(self.system_events)
            }

system_state = SystemState()

# ============================================================
# የድር መንገዶች (Web Routes)
# ============================================================

@app.route('/')
def index():
    """ዋናው የዳሽቦርድ ገፅ"""
    logger.info("Dashboard loaded")
    return render_template('index.html')

@app.route('/health')
def health():
    """የስርዓት ጤና ፍተሻ"""
    return jsonify({
        'status': 'healthy',
        'uptime': str(datetime.now() - system_state.start_time),
        'connections': system_state.get_connections_count(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """የስርዓት ሁኔታ API"""
    return jsonify({
        'system': system_state.get_status(),
        'attack': attack_engine.get_stats(),
        'evolution': evolution_engine.get_status(),
        'ai': agentic_ai.get_status(),
        'api': api.get_stats()
    })

@app.route('/api/capabilities')
def api_capabilities():
    """የችሎታዎች ዝርዝር API"""
    caps = evolution_engine.get_capabilities()
    return jsonify(caps)

@app.route('/api/attack/history')
def api_attack_history():
    """የጥቃት ታሪክ API"""
    limit = request.args.get('limit', 20, type=int)
    history = attack_engine.get_history(limit)
    return jsonify(history)

@app.route('/api/attack/stats')
def api_attack_stats():
    """የጥቃት ስታቲስቲክስ API"""
    return jsonify(attack_engine.get_stats())

@app.route('/api/evolution/records')
def api_evolution_records():
    """የእድገት ታሪክ API"""
    limit = request.args.get('limit', 20, type=int)
    records = evolution_engine.get_records(limit)
    return jsonify(records)

@app.route('/api/discover', methods=['POST'])
def api_discover():
    """ዒላማ ማግኛ API"""
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    
    result = DiscoveryEngine.discover_by_name(name)
    return jsonify(result)

@app.route('/api/attack', methods=['POST'])
def api_attack():
    """የጥቃት አፈፃፀም API"""
    data = request.json
    target = data.get('target', '').strip()
    level = data.get('level', 'standard')
    task = data.get('task', 'full')
    
    if not target:
        return jsonify({'error': 'Target required'}), 400
    
    # በዳራ ማስኬድ
    result = attack_engine.execute_attack(target, level, task)
    return jsonify(result)

@app.route('/api/evolve', methods=['POST'])
def api_evolve():
    """የእድገት አፈፃፀም API"""
    data = request.json
    action = data.get('action', '').strip()
    name = data.get('name', '').strip()
    
    if action == 'add':
        if not name:
            return jsonify({'error': 'Name required'}), 400
        result = evolution_engine.add_capability(name)
        return jsonify(result.to_dict())
    
    elif action == 'improve':
        if not name:
            return jsonify({'error': 'Name required'}), 400
        result = evolution_engine.improve_capability(name)
        return jsonify(result.to_dict())
    
    elif action == 'auto':
        result = evolution_engine.auto_evolve()
        return jsonify(result)
    
    elif action == 'learn':
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({'error': 'Topic required'}), 400
        result = evolution_engine.learn_from_internet(topic)
        return jsonify(result.to_dict())
    
    else:
        return jsonify({'error': 'Unknown action'}), 400

@app.route('/api/plan', methods=['POST'])
def api_plan():
    """የእቅድ ማውጫ API"""
    data = request.json
    target = data.get('target', '').strip()
    level = data.get('level', 'standard')
    
    if not target:
        return jsonify({'error': 'Target required'}), 400
    
    plan = planner.generate_deep_plan(target)
    summary = planner.get_plan_summary(plan)
    return jsonify({'plan': plan, 'summary': summary})

# ============================================================
# SocketIO ኢቨንቶች (Real-time Communication)
# ============================================================

@socketio.on('connect')
def handle_connect():
    """አዲስ ተጠቃሚ ሲገናኝ"""
    sid = request.sid
    system_state.add_connection(sid)
    logger.info(f"Client connected: {sid}")
    emit('system', {
        'event': 'connected',
        'message': 'Welcome to Ultimate Gold Agentic AI',
        'timestamp': datetime.now().isoformat(),
        'status': system_state.get_status()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """ተጠቃሚ ሲቋረጥ"""
    sid = request.sid
    system_state.remove_connection(sid)
    logger.info(f"Client disconnected: {sid}")

@socketio.on('join_room')
def handle_join_room(data):
    """ወደ ልዩ ክፍል መግባት"""
    room = data.get('room')
    if room:
        join_room(room)
        emit('system', {'event': 'joined', 'room': room})

@socketio.on('leave_room')
def handle_leave_room(data):
    """ከልዩ ክፍል መውጣት"""
    room = data.get('room')
    if room:
        leave_room(room)
        emit('system', {'event': 'left', 'room': room})

# ----- የትዕዛዝ አያያዝ (Command Handling) -----

@socketio.on('chat_command')
def handle_chat_command(data):
    """
    ከዳሽቦርድ ቻት የሚመጣ ትዕዛዝ ማስተናገድ
    """
    sid = request.sid
    command = data.get('command', '').strip()
    
    if not command:
        emit('chat_response', {'response': '❌ Empty command'})
        return
    
    logger.info(f"Chat command from {sid}: {command}")
    
    # ወደ ወረፋ መላክ
    command_queue.add_command(sid, command)
    
    # ምላሽ መላክ
    emit('chat_response', {'response': f'✅ Command sent: {command}'})
    
    # የስርዓት ክስተት
    system_state.add_event({
        'type': 'command',
        'source': 'chat',
        'sid': sid,
        'command': command
    })

# ----- የቅኝት ኢቨንቶች (Scanning) -----

@socketio.on('start_scan')
def handle_start_scan(data):
    """ቅኝት መጀመር"""
    sid = request.sid
    target = data.get('target', '').strip()
    ports = data.get('ports', None)
    stealth = data.get('stealth', False)
    
    if not target:
        emit('log', {'msg': '❌ Target required', 'type': 'error'})
        return
    
    emit('log', {'msg': f'🔍 Starting scan on {target}', 'type': 'info'})
    emit('log', {'msg': f'🕵️ Stealth mode: {"ON" if stealth else "OFF"}', 'type': 'info'})
    
    # ጀርባ ላይ ማስኬድ
    socketio.start_background_task(
        run_scan_task, target, ports, stealth, sid
    )

def run_scan_task(target: str, ports: List[int], stealth: bool, sid: str):
    """በዳራ ላይ የቅኝት ተግባር"""
    try:
        # ዒላማ መፍታት
        if not target.replace('.', '').isdigit():
            discovery = DiscoveryEngine.discover_by_name(target)
            if discovery['possible_targets']:
                target = discovery['possible_targets'][0]
                emit('log', {'msg': f'📍 Resolved to IP: {target}', 'type': 'success'})
            else:
                emit('log', {'msg': f'❌ Cannot resolve target: {target}', 'type': 'error'})
                return
        
        # ቅኝት ማስኬድ
        result = scanner.full_scan(target, ports, stealth, subdomain_scan=True, dir_scan=True)
        
        # ውጤት መላክ
        emit('update', {'type': 'scan_result', 'data': result.to_dict()})
        emit('log', {'msg': f'✅ Scan complete! {len(result.open_ports)} open ports found', 'type': 'success'})
        
        # ሪፖርት
        report = ScanReporter.generate_report(result)
        emit('update', {'type': 'scan_report', 'data': report})
        
        system_state.add_event({
            'type': 'scan_complete',
            'target': target,
            'open_ports': len(result.open_ports)
        })
        
    except Exception as e:
        logger.error(f"Scan error: {e}")
        emit('log', {'msg': f'❌ Scan error: {str(e)}', 'type': 'error'})

# ----- የጥቃት ኢቨንቶች (Attacks) -----

@socketio.on('start_attack')
def handle_start_attack(data):
    """ጥቃት መጀመር"""
    sid = request.sid
    target = data.get('target', '').strip()
    level = data.get('level', 'standard')
    task = data.get('task', 'full')
    open_ports = data.get('open_ports', None)
    
    if not target:
        emit('log', {'msg': '❌ Target required', 'type': 'error'})
        return
    
    attack_id = hashlib.md5(f"{target}_{time.time()}".encode()).hexdigest()[:8]
    
    emit('log', {'msg': f'⚔️ Starting {level} attack on {target} (Task: {task})', 'type': 'critical'})
    emit('update', {'type': 'attack_started', 'data': {'id': attack_id, 'target': target, 'level': level}})
    
    system_state.add_attack(attack_id, {'target': target, 'level': level, 'task': task})
    
    # ጀርባ ላይ ማስኬድ
    socketio.start_background_task(
        run_attack_task, target, level, task, open_ports, attack_id
    )

def run_attack_task(target: str, level: str, task: str, open_ports: List[int], attack_id: str):
    """በዳራ ላይ የጥቃት ተግባር"""
    try:
        # ዒላማ መፍታት
        if not target.replace('.', '').isdigit():
            discovery = DiscoveryEngine.discover_by_name(target)
            if discovery['possible_targets']:
                target = discovery['possible_targets'][0]
                emit('log', {'msg': f'📍 Resolved to IP: {target}', 'type': 'success'})
            else:
                emit('log', {'msg': f'❌ Cannot resolve target: {target}', 'type': 'error'})
                system_state.update_attack(attack_id, 'failed')
                return
        
        # ፖርቶች ካልተሰጡ መቃኘት
        if not open_ports:
            open_ports = scanner.scan_ports(target)
            emit('update', {'type': 'ports', 'data': open_ports})
        
        # ጥቃት ማስኬድ
        result = attack_engine.execute_attack(target, level, task, open_ports)
        
        # ውጤት መላክ
        if result:
            emit('update', {'type': 'attack_result', 'data': result})
            if result.get('success', False):
                emit('log', {'msg': f'🏆 Attack successful on {target}!', 'type': 'critical'})
                system_state.update_attack(attack_id, 'success', result)
            else:
                emit('log', {'msg': f'❌ Attack failed on {target}', 'type': 'error'})
                system_state.update_attack(attack_id, 'failed')
        else:
            emit('log', {'msg': f'❌ No result from attack on {target}', 'type': 'error'})
            system_state.update_attack(attack_id, 'failed')
        
        system_state.add_event({
            'type': 'attack_complete',
            'target': target,
            'level': level,
            'success': result.get('success', False)
        })
        
    except Exception as e:
        logger.error(f"Attack error: {e}")
        emit('log', {'msg': f'❌ Attack error: {str(e)}', 'type': 'error'})
        system_state.update_attack(attack_id, 'error', str(e))

# ----- የእድገት ኢቨንቶች (Evolution) -----

@socketio.on('evolve_ai')
def handle_evolve_ai(data):
    """AI እድገት ማስጀመር"""
    sid = request.sid
    action = data.get('action', '').strip()
    name = data.get('name', '').strip()
    topic = data.get('topic', '').strip()
    
    if action == 'add':
        if not name:
            emit('log', {'msg': '❌ Name required', 'type': 'error'})
            return
        emit('log', {'msg': f'🧬 Adding capability: {name}', 'type': 'critical'})
        result = evolution_engine.add_capability(name)
        emit('update', {'type': 'evolution_result', 'data': result.to_dict()})
        
    elif action == 'improve':
        if not name:
            emit('log', {'msg': '❌ Name required', 'type': 'error'})
            return
        emit('log', {'msg': f'🔧 Improving capability: {name}', 'type': 'info'})
        result = evolution_engine.improve_capability(name)
        emit('update', {'type': 'evolution_result', 'data': result.to_dict()})
        
    elif action == 'auto':
        emit('log', {'msg': '🤖 Starting auto-evolution...', 'type': 'critical'})
        result = evolution_engine.auto_evolve()
        emit('update', {'type': 'evolution_result', 'data': result})
        emit('log', {'msg': f'✅ Auto-evolution complete! Generation {result["generation"]}', 'type': 'success'})
        
    elif action == 'learn':
        if not topic:
            emit('log', {'msg': '❌ Topic required', 'type': 'error'})
            return
        emit('log', {'msg': f'🌐 Learning about: {topic}', 'type': 'info'})
        result = evolution_engine.learn_from_internet(topic)
        emit('update', {'type': 'evolution_result', 'data': result.to_dict()})
        
    else:
        emit('log', {'msg': f'❌ Unknown evolution action: {action}', 'type': 'error'})

# ----- የመረጃ ማውጫ (Data) ኢቨንቶች -----

@socketio.on('get_status')
def handle_get_status():
    """የስርዓት ሁኔታ መላክ"""
    status = {
        'system': system_state.get_status(),
        'attack': attack_engine.get_stats(),
        'evolution': evolution_engine.get_status(),
        'ai': agentic_ai.get_status(),
        'api': api.get_stats(),
        'timestamp': datetime.now().isoformat()
    }
    emit('update', {'type': 'status', 'data': status})

@socketio.on('get_capabilities')
def handle_get_capabilities():
    """የችሎታዎች ዝርዝር መላክ"""
    caps = evolution_engine.get_capabilities()
    emit('update', {'type': 'capabilities', 'data': caps})

@socketio.on('get_history')
def handle_get_history(data):
    """የታሪክ መላክ"""
    limit = data.get('limit', 20)
    history = attack_engine.get_history(limit)
    emit('update', {'type': 'history', 'data': history})

@socketio.on('discover_target')
def handle_discover_target(data):
    """ዒላማ ማግኘት"""
    name = data.get('name', '').strip()
    if not name:
        emit('log', {'msg': '❌ Name required', 'type': 'error'})
        return
    
    emit('log', {'msg': f'🔍 Discovering: {name}', 'type': 'info'})
    result = DiscoveryEngine.discover_by_name(name)
    emit('update', {'type': 'discovery', 'data': result})
    
    if result['possible_targets']:
        emit('log', {'msg': f'✅ Found {len(result["possible_targets"])} targets', 'type': 'success'})
    else:
        emit('log', {'msg': '❌ No targets found', 'type': 'warning'})

# ----- የAI ውሳኔ ኢቨንቶች -----

@socketio.on('ai_analyze')
def handle_ai_analyze(data):
    """AI ትንተና ማስኬድ"""
    target = data.get('target', '').strip()
    open_ports = data.get('open_ports', [])
    services = data.get('services', {})
    banners = data.get('banners', {})
    
    if not target:
        emit('log', {'msg': '❌ Target required', 'type': 'error'})
        return
    
    emit('log', {'msg': f'🧠 AI analyzing {target}...', 'type': 'info'})
    
    # ትንተና ማስኬድ
    analysis = agentic_ai.decision_engine.analyze_situation(
        target, open_ports, services, banners
    )
    
    emit('update', {'type': 'ai_analysis', 'data': analysis})
    emit('log', {'msg': f'✅ Analysis complete. Recommended: {analysis.get("recommended_action", "none")}', 'type': 'success'})

# ----- የስርዓት እንቅስቃሴ (Activity) -----

@socketio.on('get_activity')
def handle_get_activity():
    """የስርዓት እንቅስቃሴ መላክ"""
    emit('update', {'type': 'activity', 'data': system_state.system_events[-50:]})

# ============================================================
# የትዕዛዝ ወረፋ ማቀነባበሪያ (Command Queue Processor)
# ============================================================

class CommandProcessor:
    """የትዕዛዝ ወረፋ በዳራ ማቀነባበሪያ"""
    def __init__(self):
        self.is_running = False
        self.thread = None
        self._lock = threading.Lock()

    def start(self):
        """ማቀነባበሪያ መጀመር"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        logger.info("Command processor started")

    def stop(self):
        """ማቀነባበሪያ ማቆም"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Command processor stopped")

    def _process_loop(self):
        """ዋናው የማቀነባበሪያ ዑደት"""
        while self.is_running:
            try:
                cmd = command_queue.get_next_command()
                if cmd:
                    self._process_command(cmd)
                else:
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Command processor error: {e}")

    def _process_command(self, cmd: Dict):
        """አንድ ትዕዛዝ ማቀነባበር"""
        user_id = cmd.get('user_id', 'unknown')
        command = cmd.get('command', '').strip()
        
        if not command:
            return
        
        logger.info(f"Processing command from {user_id}: {command}")
        
        # ትዕዛዙን መለየት
        parts = command.lower().split()
        if not parts:
            return
        
        cmd_type = parts[0]
        
        # በSocketIO በኩል ምላሽ መላክ
        def send_response(msg):
            socketio.emit('chat_response', {'response': msg}, room=user_id)
        
        # የትዕዛዝ አፈፃፀም
        if cmd_type == 'strike':
            target = parts[1] if len(parts) > 1 else None
            level = parts[2] if len(parts) > 2 else 'standard'
            task = parts[3] if len(parts) > 3 else 'full'
            
            if target:
                send_response(f"⚔️ Attacking {target} ({level})")
                socketio.start_background_task(
                    run_attack_task, target, level, task, None, 
                    hashlib.md5(f"{target}_{time.time()}".encode()).hexdigest()[:8]
                )
            else:
                send_response("❌ Target required: strike <target>")
                
        elif cmd_type == 'scan':
            target = parts[1] if len(parts) > 1 else None
            stealth = 'stealth' in command.lower()
            
            if target:
                send_response(f"🔍 Scanning {target}")
                socketio.start_background_task(
                    run_scan_task, target, None, stealth, user_id
                )
            else:
                send_response("❌ Target required: scan <target>")
                
        elif cmd_type == 'add':
            name = parts[1] if len(parts) > 1 else None
            if name:
                send_response(f"🧬 Adding capability: {name}")
                result = evolution_engine.add_capability(name)
                send_response(f"✅ {result.to_dict()['status']}")
            else:
                send_response("❌ Name required: add <name>")
                
        elif cmd_type == 'improve':
            name = parts[1] if len(parts) > 1 else None
            if name:
                send_response(f"🔧 Improving: {name}")
                result = evolution_engine.improve_capability(name)
                send_response(f"✅ {result.to_dict()['status']}")
            else:
                send_response("❌ Name required: improve <name>")
                
        elif cmd_type == 'learn':
            topic = ' '.join(parts[1:]) if len(parts) > 1 else None
            if topic:
                send_response(f"🌐 Learning about: {topic}")
                result = evolution_engine.learn_from_internet(topic)
                send_response(f"✅ {result.to_dict()['status']}")
            else:
                send_response("❌ Topic required: learn <topic>")
                
        elif cmd_type == 'auto':
            send_response("🤖 Auto-evolving...")
            result = evolution_engine.auto_evolve()
            send_response(f"✅ Generation {result['generation']}: Added {len(result['added'])}, Improved {len(result['improved'])}")
            
        elif cmd_type == 'plan':
            target = parts[1] if len(parts) > 1 else None
            if target:
                send_response(f"📋 Generating plan for {target}...")
                plan = planner.generate_deep_plan(target)
                summary = planner.get_plan_summary(plan)
                send_response(f"📋 Plan:\n{summary}")
            else:
                send_response("❌ Target required: plan <target>")
                
        elif cmd_type == 'status':
            status = {
                'system': system_state.get_status(),
                'attack': attack_engine.get_stats(),
                'evolution': evolution_engine.get_status(),
                'ai': agentic_ai.get_status()
            }
            send_response(f"📊 Status:\n{json.dumps(status, indent=2, default=str)}")
            
        elif cmd_type == 'stop':
            send_response("🛑 Stopping all commands")
            command_queue.stop_user_commands(user_id)
            
        elif cmd_type == 'help':
            send_response("""
📚 Commands:
strike <target> [level] - Full attack
scan <target> - Scan target
add <name> - Add capability
improve <name> - Improve capability
learn <topic> - Learn from internet
auto - Auto-evolve
plan <target> - Generate plan
status - System status
stop - Stop all
help - This message
""")
            
        else:
            send_response(f"❌ Unknown command: {cmd_type}")

# ============================================================
# የአፕሊኬሽን ህይወት አስተዳደር (Application Lifecycle)
# ============================================================

class Application:
    """ዋናው አፕሊኬሽን አስተዳዳሪ"""
    def __init__(self):
        self.command_processor = CommandProcessor()
        self.is_running = False
        self.background_tasks = []

    def start(self):
        """አፕሊኬሽኑን ማስጀመር"""
        logger.info("🚀 Starting Ultimate Gold Agentic AI Application")
        
        # የትዕዛዝ ማቀነባበሪያ መጀመር
        self.command_processor.start()
        
        # የበላይ ተመልካች (Monitor) መጀመር
        self._start_monitor()
        
        # የስርዓት መረጃ መጫን
        self._load_system_info()
        
        self.is_running = True
        logger.info("✅ Application started successfully")

    def stop(self):
        """አፕሊኬሽኑን ማቆም"""
        logger.info("🛑 Stopping application...")
        self.is_running = False
        self.command_processor.stop()
        logger.info("✅ Application stopped")

    def _start_monitor(self):
        """በዳራ የሚሰራ ተመልካች"""
        def monitor_loop():
            while self.is_running:
                try:
                    # የስርዓት ጤና ምርመራ
                    connections = system_state.get_connections_count()
                    active_attacks = len(system_state.active_attacks)
                    
                    if connections > 0:
                        logger.debug(f"System: {connections} connections, {active_attacks} active attacks")
                    
                    time.sleep(60)  # በየደቂቃው
                except Exception as e:
                    logger.error(f"Monitor error: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        self.background_tasks.append(thread)

    def _load_system_info(self):
        """የስርዓት መረጃ መጫን"""
        logger.info(f"📊 System Version: {config.app_version}")
        logger.info(f"📊 Environment: {config.environment}")
        logger.info(f"📊 API Providers: {api.get_available_providers()}")
        logger.info(f"📊 Capabilities: {len(evolution_engine.get_capabilities().get('capabilities', []))}")

# ============================================================
# የሲግናል አያያዥ (Signal Handlers)
# ============================================================

def signal_handler(sig, frame):
    """የማቆሚያ ሲግናል አያያዥ"""
    logger.info(f"Received signal {sig}, shutting down...")
    if hasattr(app, 'application'):
        app.application.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ============================================================
# ዋናው የማስኬጃ ነጥብ (Main Entry Point)
# ============================================================

def main():
    """ዋና የማስጀመሪያ ተግባር"""
    # አፕሊኬሽኑን መጫን
    app.application = Application()
    app.application.start()
    
    # የማዕድ መረጃ
    print("=" * 60)
    print("👑 ULTIMATE GOLD AGENTIC AI")
    print(f"📦 Version: {config.app_version}")
    print(f"🌐 Environment: {config.environment}")
    print(f"🔌 WebSocket: SocketIO (eventlet)")
    print(f"📊 Dashboard: http://localhost:5000")
    print("=" * 60)
    
    # ሰርቨሩን ማስኬድ
    try:
        socketio.run(
            app,
            host='0.0.0.0',
            port=int(os.environ.get("PORT", 5000))
            debug=config.debug,
            allow_unsafe_werkzeug=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        app.application.stop()
    except Exception as e:
        logger.error(f"Server error: {e}")
        app.application.stop()
        sys.exit(1)

# ============================================================
# ለሙከራ እና ለገብ አጠቃቀም (Testing & Standalone)
# ============================================================

if __name__ == "__main__":
    # ሙከራ እና ማሳያ
    if '--test' in sys.argv:
        print("=" * 60)
        print("🧪 Running System Test...")
        print("=" * 60)
        
        # የስርዓት ክፍሎች ሙከራ
        print("✅ Config loaded")
        print(f"✅ API Providers: {api.get_available_providers()}")
        print(f"✅ Agentic AI: {agentic_ai.get_status().get('state', 'unknown')}")
        print(f"✅ Attack Engine: {attack_engine.get_stats()}")
        print(f"✅ Evolution Engine: {evolution_engine.get_status().get('generation', 0)}")
        
        # ቀላል የጥቃት ሙከራ
        print("\n📝 Testing attack engine...")
        result = attack_engine.execute_attack("127.0.0.1", "standard", "recon_only", [80, 443])
        print(f"Result: {result}")
        
        print("\n✅ All tests passed!")
        print("=" * 60)
    else:
        main()

# ============================================================
# 🏆 ይህ ሙሉ የተሟላ ዋና ሰርቨር አፕሊኬሽን ነው
# ============================================================
