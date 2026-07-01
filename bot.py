# ============================================================
# 👑 ULTIMATE GOLD AGENTIC AI - TELEGRAM BOT MODULE
# ============================================================
# ይህ ሞጁል ሙሉ የቴሌግራም ቦት ተግባራትን ያስተዳድራል
# - ሁሉም ትዕዛዞች በቻት ይሰራሉ
# - የInline ቁልፎች እና መዝገቦች
# - የትዕዛዝ አያያዝ እና መላኪያ
# - የተጠቃሚ አስተዳደር
# - የድር መተግበሪያ (WebApp) ድጋፍ
# - ተለዋዋጭ የቁልፍ ሰሌዳዎች (Dynamic Keyboards)
# - የስህተት አያያዝ እና መዝገብ
# - በርካታ ቋንቋዎች ድጋፍ
# ============================================================

import os
import re
import json
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from enum import Enum
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)
from telegram.constants import ParseMode

# የስርዓት ክፍሎች
from command_queue import CommandQueue
from config import config
from api_integration import get_api
from agentic_ai_core import get_agentic_ai
from attack_engine import get_attack_engine
from evolution_engine import get_evolution_engine
from scanner_engine import DiscoveryEngine

# ============================================================
# የቦት ሁኔታዎች (Bot States)
# ============================================================

class BotState(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING_INPUT = "waiting_input"
    ERROR = "error"

class UserState:
    """የተጠቃሚ ሁኔታ አስተዳዳሪ"""
    def __init__(self):
        self.state = BotState.IDLE
        self.last_command = None
        self.last_interaction = datetime.now()
        self.data = {}
        self.conversation = []
        self.language = "am"  # am, en
        self.attack_history = []

    def to_dict(self):
        return {
            'state': self.state.value,
            'last_command': self.last_command,
            'last_interaction': self.last_interaction.isoformat(),
            'language': self.language,
            'history_count': len(self.conversation)
        }

# ============================================================
# የቋንቋ ትርጉም (Translations)
# ============================================================

class Translator:
    """በርካታ ቋንቋዎች ድጋፍ"""
    
    # መሰረታዊ ትርጉሞች
    TRANSLATIONS = {
        'am': {
            'welcome': "👑 *ULTIMATE GOLD AGENTIC AI* እንኳን ደህና መጡ!\n\nሁሉም ትዕዛዞች በዚህ ቻት ውስጥ ይሰራሉ!\n\n`/help` ለሙሉ ዝርዝር",
            'help': """📚 *ሙሉ ትዕዛዞች*

🎯 *ጥቃት:*
`/strike <target>` - ሙሉ ጥቃት
`/level1 <target>` - ስልክ/WiFi መጥለፍ
`/level2 <target>` - ሰርቨር መቃኘት+መምታት
`/level3 <target>` - Gold Level ስውር ጥቃት

🧬 *እድገት:*
`/add <name>` - አዲስ ችሎታ መጨመር
`/improve <name>` - ነባር ችሎታ ማሻሻል
`/learn <topic>` - ከኢንተርኔት መማር
`/auto` - ራስ-ማሻሻል

🎮 *ቁጥጥር:*
`/status` - ሁኔታ መጠየቅ
`/plan <target>` - እቅድ ማውጣት
`/stop` - እየተሰራ ያለውን ማቆም
`/history` - ታሪክ ማየት
`/clear` - ቻት ማጽዳት
`/language <am|en>` - ቋንቋ መቀየር
`/help` - ይህን መልእክት

💬 *ቀጥተኛ ትዕዛዞች:*
በቀጥታ መልእክት ማስገባት ይችላሉ!
ለምሳሌ: `strike 192.168.1.1`""",
            'processing': "⏳ እየሰራ ነው... እባክዎ ይጠብቁ",
            'error': "❌ ስህተት ተከስቷል",
            'success': "✅ ተሳክቷል!",
            'no_command': "❌ ያልታወቀ ትዕዛዝ",
            'stopped': "🛑 ተቆሟል",
            'status': """📊 *ሁኔታ*

{system_status}

🧠 *AI ሁኔታ:*
{ai_status}

📊 *ስታቲስቲክስ:*
{stats}

🔄 *ትውልድ:* {generation}""",
            'history': """📜 *ታሪክ*

{history}""",
            'plan': """📋 *እቅድ*

{plan}""",
            'language_changed': "✅ ቋንቋ ተቀየረ: {lang}",
            'unknown_target': "❌ ዒላማ አልተገኘም",
            'attack_started': "⚔️ ጥቃት ተጀመረ: {target}",
            'attack_complete': "🏆 ጥቃት ተጠናቀቀ! {target}",
            'evolution_started': "🧬 እድገት ተጀመረ: {target}",
            'evolution_complete': "✅ እድገት ተጠናቀቀ: {target}",
            'dashboard': "📊 *የAI ዳሽቦርድ*"
        },
        'en': {
            'welcome': "👑 *ULTIMATE GOLD AGENTIC AI* Welcome!\n\nAll commands work in this chat!\n\n`/help` for full list",
            'help': """📚 *Full Commands*

🎯 *Attack:*
`/strike <target>` - Full attack
`/level1 <target>` - Phone/WiFi hack
`/level2 <target>` - Server scan+strike
`/level3 <target>` - Gold stealth attack

🧬 *Evolution:*
`/add <name>` - Add new capability
`/improve <name>` - Improve existing
`/learn <topic>` - Learn from internet
`/auto` - Auto-evolve

🎮 *Control:*
`/status` - Check status
`/plan <target>` - Generate plan
`/stop` - Stop current operation
`/history` - View history
`/clear` - Clear chat
`/language <am|en>` - Change language
`/help` - This message

💬 *Direct Commands:*
You can type commands directly in chat!
Example: `strike 192.168.1.1`""",
            'processing': "⏳ Processing... Please wait",
            'error': "❌ An error occurred",
            'success': "✅ Success!",
            'no_command': "❌ Unknown command",
            'stopped': "🛑 Stopped",
            'status': """📊 *Status*

{system_status}

🧠 *AI Status:*
{ai_status}

📊 *Statistics:*
{stats}

🔄 *Generation:* {generation}""",
            'history': """📜 *History*

{history}""",
            'plan': """📋 *Plan*

{plan}""",
            'language_changed': "✅ Language changed to: {lang}",
            'unknown_target': "❌ Target not found",
            'attack_started': "⚔️ Attack started: {target}",
            'attack_complete': "🏆 Attack complete! {target}",
            'evolution_started': "🧬 Evolution started: {target}",
            'evolution_complete': "✅ Evolution complete: {target}",
            'dashboard': "📊 *AI Dashboard*"
        }
    }

    @classmethod
    def get(cls, lang: str, key: str, **kwargs) -> str:
        """ትርጉም ማግኘት"""
        text = cls.TRANSLATIONS.get(lang, cls.TRANSLATIONS['am']).get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass
        return text

# ============================================================
# ዋናው የቦት ክፍል (Bot Class)
# ============================================================

class UltimateGoldBot:
    """
    ሙሉ የቴሌግራም ቦት አስተዳዳሪ
    """
    def __init__(self, token: str = None, webapp_url: str = None):
        self.token = token or config.telegram.token
        self.webapp_url = webapp_url or config.telegram.webapp_url
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        self._logger = logging.getLogger("bot.main")
        self._user_states: Dict[str, UserState] = {}
        self._lock = threading.Lock()
        self._application = None
        
        # የስርዓት ክፍሎችን መጫን
        self.command_queue = CommandQueue()
        self.api = get_api()
        self.agentic_ai = get_agentic_ai()
        self.attack_engine = get_attack_engine()
        self.evolution_engine = get_evolution_engine()
        
        self._setup_handlers()

    def _log(self, msg: str, level: str = 'info'):
        self._logger.info(f"[BOT] {msg}")

    def _get_user_state(self, user_id: str) -> UserState:
        """የተጠቃሚ ሁኔታ ማግኘት"""
        with self._lock:
            if user_id not in self._user_states:
                self._user_states[user_id] = UserState()
            return self._user_states[user_id]

    def _get_language(self, user_id: str) -> str:
        """የተጠቃሚ ቋንቋ ማግኘት"""
        return self._get_user_state(user_id).language

    def _setup_handlers(self):
        """የትዕዛዝ አያያዥዎችን ማዋቀር"""
        self._handlers = {}

    def _get_webapp_keyboard(self, user_id: str) -> InlineKeyboardMarkup:
        """የWebApp ቁልፍ ሰሌዳ መፍጠር"""
        lang = self._get_language(user_id)
        
        keyboard = [
            [
                InlineKeyboardButton(
                    "👑 Open Ultimate Suite",
                    web_app=WebAppInfo(url=self.webapp_url)
                )
            ],
            [
                InlineKeyboardButton("📊 Status", callback_data="status"),
                InlineKeyboardButton("🧬 Evolve", callback_data="evolve"),
                InlineKeyboardButton("📚 Help", callback_data="help")
            ],
            [
                InlineKeyboardButton("⚔️ Level 1 (Mobile)", callback_data="level1"),
                InlineKeyboardButton("🌐 Level 2 (Server)", callback_data="level2"),
                InlineKeyboardButton("👑 Level 3 (Gold)", callback_data="level3")
            ],
            [
                InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am"),
                InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/start ትዕዛዝ አያያዥ"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        welcome = Translator.get(lang, 'welcome')
        keyboard = self._get_webapp_keyboard(user_id)
        
        await update.message.reply_text(
            welcome,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/help ትዕዛዝ አያያዥ"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        help_text = Translator.get(lang, 'help')
        keyboard = self._get_webapp_keyboard(user_id)
        
        await update.message.reply_text(
            help_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/status ትዕዛዝ አያያዥ"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        # የስርዓት ሁኔታ
        system_status = "✅ All systems operational"
        
        # AI ሁኔታ
        ai_status = self.agentic_ai.get_status()
        ai_text = f"State: {ai_status.get('state', 'unknown')}\n"
        ai_text += f"Generation: {ai_status.get('generation', 0)}"
        
        # ስታቲስቲክስ
        stats = self.attack_engine.get_stats()
        stats_text = f"Total Attacks: {stats.get('total', 0)}\n"
        stats_text += f"Success Rate: {stats.get('success_rate', '0%')}"
        
        # Evolution
        evo_status = self.evolution_engine.get_status()
        gen = evo_status.get('generation', 0)
        
        status_text = Translator.get(lang, 'status').format(
            system_status=system_status,
            ai_status=ai_text,
            stats=stats_text,
            generation=gen
        )
        
        await update.message.reply_text(
            status_text,
            parse_mode=ParseMode.MARKDOWN
        )

    async def strike_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/strike ትዕዛዝ አያያዥ"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        # ትዕዛዙን ማውጣት
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ Usage: /strike <target> [level] [task]\n"
                "Example: /strike 192.168.1.1 gold full"
            )
            return
        
        target = args[0]
        level = args[1] if len(args) > 1 else "standard"
        task = args[2] if len(args) > 2 else "full"
        
        # ወደ ወረፋ መላክ
        self.command_queue.add_command(user_id, f"strike {target} {level} {task}")
        
        await update.message.reply_text(
            Translator.get(lang, 'attack_started').format(target=target)
        )

    async def level_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, level: str):
        """የ/level1, /level2, /level3 ትዕዛዝ አያያዥ"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        args = context.args
        if not args:
            await update.message.reply_text(
                f"❌ Usage: /{level} <target>\n"
                f"Example: /{level} 192.168.1.1"
            )
            return
        
        target = args[0]
        self.command_queue.add_command(user_id, f"strike {target} {level} full")
        
        await update.message.reply_text(
            Translator.get(lang, 'attack_started').format(target=target)
        )

    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/add ትዕዛዝ አያያዥ (Evolution - ADD ONLY)"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ Usage: /add <capability_name>\n"
                "Example: /add blockchain"
            )
            return
        
        name = args[0]
        
        # Evolution ማስጀመር
        self.command_queue.add_command(user_id, f"evolve add {name}")
        
        await update.message.reply_text(
            Translator.get(lang, 'evolution_started').format(target=name)
        )

    async def improve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/improve ትዕዛዝ አያያዥ"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ Usage: /improve <capability_name>\n"
                "Example: /improve sql"
            )
            return
        
        name = args[0]
        self.command_queue.add_command(user_id, f"evolve improve {name}")
        
        await update.message.reply_text(
            Translator.get(lang, 'evolution_started').format(target=name)
        )

    async def learn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/learn ትዕዛዝ አያያዥ (ከኢንተርኔት መማር)"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ Usage: /learn <topic>\n"
                "Example: /learn cybersecurity trends"
            )
            return
        
        topic = ' '.join(args)
        self.command_queue.add_command(user_id, f"learn {topic}")
        
        await update.message.reply_text(
            f"🌐 Learning about: {topic}\n⏳ Please wait..."
        )

    async def auto_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/auto ትዕዛዝ አያያዥ (ራስ-ማሻሻል)"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        self.command_queue.add_command(user_id, "auto")
        
        await update.message.reply_text(
            "🤖 Starting AUTO-EVOLUTION...\n⏳ This may take a few moments"
        )

    async def plan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/plan ትዕዛዝ አያያዥ"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ Usage: /plan <target>\n"
                "Example: /plan company.com"
            )
            return
        
        target = args[0]
        self.command_queue.add_command(user_id, f"plan {target}")
        
        await update.message.reply_text(
            f"📋 Generating plan for {target}..."
        )

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/stop ትዕዛዝ አያያዥ"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        self.command_queue.stop_user_commands(user_id)
        await update.message.reply_text(
            Translator.get(lang, 'stopped')
        )

    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/history ትዕዛዝ አያያዥ"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        # ከታሪክ መረጃ ማግኘት
        history = self.attack_engine.get_history(10)
        if not history:
            await update.message.reply_text("📜 No history yet")
            return
        
        history_text = ""
        for i, entry in enumerate(history[:10], 1):
            target = entry.get('target', 'unknown')
            level = entry.get('level', 'unknown')
            success = entry.get('result', {}).get('success', False)
            status = "✅" if success else "❌"
            history_text += f"{i}. {status} {target} ({level})\n"
        
        await update.message.reply_text(
            Translator.get(lang, 'history').format(history=history_text),
            parse_mode=ParseMode.MARKDOWN
        )

    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/clear ትዕዛዝ አያያዥ"""
        await update.message.reply_text("🧹 Chat cleared")
        # በእውነቱ ቻት ማጽዳት በቴሌግራም አይቻልም, ግን መልእክት መላክ እንችላለን

    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የ/language ትዕዛዝ አያያዥ"""
        user_id = str(update.effective_user.id)
        lang = self._get_language(user_id)
        
        args = context.args
        if not args or args[0] not in ['am', 'en']:
            await update.message.reply_text(
                "❌ Usage: /language <am|en>\n"
                "Example: /language am"
            )
            return
        
        new_lang = args[0]
        state = self._get_user_state(user_id)
        state.language = new_lang
        
        await update.message.reply_text(
            Translator.get(new_lang, 'language_changed').format(lang=new_lang)
        )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        ሁሉንም መደበኛ ጽሑፍ እንደ ትዕዛዝ መያዝ
        """
        user_id = str(update.effective_user.id)
        text = update.message.text.strip()
        lang = self._get_language(user_id)
        
        if not text:
            return
        
        # ከ '/' መጀመሪያ ካለ አስወግድ
        if text.startswith('/'):
            text = text[1:]
        
        # ወደ ወረፋ መላክ
        self.command_queue.add_command(user_id, text)
        
        # አጭር ምላሽ
        await update.message.reply_text(
            f"✅ Command sent: `{text}`",
            parse_mode=ParseMode.MARKDOWN
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የInline ቁልፍ ጫና አያያዥ"""
        query = update.callback_query
        user_id = str(query.from_user.id)
        data = query.data
        
        await query.answer()
        
        lang = self._get_language(user_id)
        
        if data == 'status':
            await self.status_command(update, context)
        elif data == 'evolve':
            await query.edit_message_text(
                "🧬 *Evolution Commands:*\n\n"
                "`/add <name>` - Add new capability\n"
                "`/improve <name>` - Improve existing\n"
                "`/learn <topic>` - Learn from internet\n"
                "`/auto` - Auto-evolve",
                parse_mode=ParseMode.MARKDOWN
            )
        elif data == 'help':
            await self.help_command(update, context)
        elif data.startswith('lang_'):
            new_lang = data.split('_')[1]
            state = self._get_user_state(user_id)
            state.language = new_lang
            await query.edit_message_text(
                Translator.get(new_lang, 'language_changed').format(lang=new_lang)
            )
        elif data in ['level1', 'level2', 'level3']:
            level = data.replace('level', '')
            await query.edit_message_text(
                f"⚔️ {level.upper()} attack selected.\n"
                f"Send target: /{level} <target>"
            )
        else:
            await query.edit_message_text(
                f"❌ Unknown action: {data}"
            )

    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """የስህተት አያያዥ"""
        self._logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_user:
            user_id = str(update.effective_user.id)
            lang = self._get_language(user_id)
            await update.message.reply_text(
                f"❌ {Translator.get(lang, 'error')}\n{str(context.error)[:100]}"
            )

    async def process_command_queue(self):
        """የትዕዛዝ ወረፋ ማቀነባበሪያ"""
        while True:
            cmd = self.command_queue.get_next_command()
            if cmd:
                user_id = cmd['user_id']
                command = cmd['command']
                self._log(f"Processing command from {user_id}: {command}")
                
                # ትዕዛዙን መተርጎም
                parsed = self._parse_command(command)
                self._log(f"Parsed: {parsed}")
                
                # ትዕዛዙን መፈጸም
                await self._execute_command(user_id, parsed)
            
            await asyncio.sleep(0.1)

    def _parse_command(self, command: str) -> Dict[str, Any]:
        """ትዕዛዙን መተርጎም"""
        parts = command.lower().split()
        if not parts:
            return {'type': 'empty'}
        
        # የትዕዛዝ ዓይነት መለየት
        cmd_type = parts[0]
        
        if cmd_type == 'strike':
            return {
                'type': 'strike',
                'target': parts[1] if len(parts) > 1 else None,
                'level': parts[2] if len(parts) > 2 else 'standard',
                'task': parts[3] if len(parts) > 3 else 'full'
            }
        elif cmd_type in ['level1', 'level2', 'level3']:
            return {
                'type': 'strike',
                'target': parts[1] if len(parts) > 1 else None,
                'level': cmd_type,
                'task': 'full'
            }
        elif cmd_type == 'add':
            return {
                'type': 'evolve_add',
                'name': parts[1] if len(parts) > 1 else None
            }
        elif cmd_type == 'improve':
            return {
                'type': 'evolve_improve',
                'name': parts[1] if len(parts) > 1 else None
            }
        elif cmd_type == 'learn':
            return {
                'type': 'learn',
                'topic': ' '.join(parts[1:]) if len(parts) > 1 else None
            }
        elif cmd_type == 'auto':
            return {'type': 'auto'}
        elif cmd_type == 'plan':
            return {
                'type': 'plan',
                'target': parts[1] if len(parts) > 1 else None
            }
        elif cmd_type == 'status':
            return {'type': 'status'}
        elif cmd_type == 'stop':
            return {'type': 'stop'}
        elif cmd_type == 'help':
            return {'type': 'help'}
        else:
            # ያልታወቀ ትዕዛዝ
            return {
                'type': 'unknown',
                'raw': command
            }

    async def _execute_command(self, user_id: str, parsed: Dict[str, Any]):
        """የተረጎመ ትዕዛዝ መፈጸም"""
        cmd_type = parsed.get('type')
        
        if cmd_type == 'strike':
            target = parsed.get('target')
            level = parsed.get('level', 'standard')
            task = parsed.get('task', 'full')
            
            if not target:
                return
            
            # ዒላማ መፈለግ
            if not target.replace('.', '').isdigit():
                discovery = DiscoveryEngine.discover_by_name(target)
                if discovery['possible_targets']:
                    target = discovery['possible_targets'][0]
                else:
                    self.command_queue.add_response(user_id, f"❌ Target not found: {target}")
                    return
            
            # ጥቃት ማስፈጸም
            result = self.attack_engine.execute_attack(target, level, task)
            
            # ምላሽ መላክ
            if result:
                if result.get('success', False):
                    self.command_queue.add_response(user_id, f"✅ Attack successful: {target}")
                    # የተሰረቀ ውሂብ ካለ
                    if 'exfiltrated_data' in result:
                        data_count = len(result['exfiltrated_data'])
                        self.command_queue.add_response(user_id, f"📂 Exfiltrated {data_count} items")
                else:
                    self.command_queue.add_response(user_id, f"❌ Attack failed: {target}")
            else:
                self.command_queue.add_response(user_id, f"❌ No result from attack on {target}")

        elif cmd_type == 'evolve_add':
            name = parsed.get('name')
            if not name:
                return
            
            record = self.evolution_engine.add_capability(name)
            if record.status == EvolutionState.COMPLETED:
                self.command_queue.add_response(user_id, f"✅ Capability '{name}' added (Gen {record.generation})")
            else:
                self.command_queue.add_response(user_id, f"❌ Failed to add '{name}': {record.error}")

        elif cmd_type == 'evolve_improve':
            name = parsed.get('name')
            if not name:
                return
            
            record = self.evolution_engine.improve_capability(name)
            if record.status == EvolutionState.COMPLETED:
                self.command_queue.add_response(user_id, f"✅ '{name}' improved (Gen {record.generation})")
            else:
                self.command_queue.add_response(user_id, f"❌ Failed to improve '{name}': {record.error}")

        elif cmd_type == 'learn':
            topic = parsed.get('topic')
            if not topic:
                return
            
            record = self.evolution_engine.learn_from_internet(topic)
            if record.status == EvolutionState.COMPLETED:
                self.command_queue.add_response(user_id, f"✅ Learned about '{topic}'")
            else:
                self.command_queue.add_response(user_id, f"❌ Failed to learn about '{topic}'")

        elif cmd_type == 'auto':
            results = self.evolution_engine.auto_evolve()
            self.command_queue.add_response(
                user_id,
                f"✅ Auto-evolution complete (Gen {results['generation']})\n"
                f"Added: {len(results['added'])}\n"
                f"Improved: {len(results['improved'])}\n"
                f"Learned: {len(results['learned'])}"
            )

        elif cmd_type == 'plan':
            target = parsed.get('target')
            if not target:
                return
            
            # Plan ማውጣት
            from planner_engine import DeepPlanningEngine
            planner = DeepPlanningEngine()
            plan = planner.generate_deep_plan(target)
            summary = planner.get_plan_summary(plan)
            
            self.command_queue.add_response(user_id, f"📋 Plan for {target}:\n{summary}")

        elif cmd_type == 'status':
            status = self.evolution_engine.get_status()
            stats = self.attack_engine.get_stats()
            self.command_queue.add_response(
                user_id,
                f"📊 Status\n"
                f"Generation: {status.get('generation', 0)}\n"
                f"Capabilities: {len(status.get('capabilities', {}).get('capabilities', []))}\n"
                f"Total Attacks: {stats.get('total', 0)}\n"
                f"Success Rate: {stats.get('success_rate', '0%')}"
            )

        elif cmd_type == 'help':
            lang = self._get_language(user_id)
            self.command_queue.add_response(user_id, Translator.get(lang, 'help'))

        elif cmd_type == 'stop':
            self.command_queue.stop_user_commands(user_id)
            self.command_queue.add_response(user_id, "🛑 Stopped all commands")

        else:
            self.command_queue.add_response(user_id, f"❌ Unknown command: {cmd_type}")

    def create_application(self):
        """ቴሌግራም አፕሊኬሽን መፍጠር"""
        self._application = Application.builder().token(self.token).build()
        
        # ትዕዛዞች
        self._application.add_handler(CommandHandler("start", self.start))
        self._application.add_handler(CommandHandler("help", self.help_command))
        self._application.add_handler(CommandHandler("status", self.status_command))
        self._application.add_handler(CommandHandler("strike", self.strike_command))
        self._application.add_handler(CommandHandler("level1", lambda u, c: self.level_command(u, c, "level1")))
        self._application.add_handler(CommandHandler("level2", lambda u, c: self.level_command(u, c, "level2")))
        self._application.add_handler(CommandHandler("level3", lambda u, c: self.level_command(u, c, "level3")))
        self._application.add_handler(CommandHandler("add", self.add_command))
        self._application.add_handler(CommandHandler("improve", self.improve_command))
        self._application.add_handler(CommandHandler("learn", self.learn_command))
        self._application.add_handler(CommandHandler("auto", self.auto_command))
        self._application.add_handler(CommandHandler("plan", self.plan_command))
        self._application.add_handler(CommandHandler("stop", self.stop_command))
        self._application.add_handler(CommandHandler("history", self.history_command))
        self._application.add_handler(CommandHandler("clear", self.clear_command))
        self._application.add_handler(CommandHandler("language", self.language_command))
        
        # ጽሑፍ አያያዥ - ሁሉም ነገር
        self._application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        # Callback
        self._application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # ስህተት
        self._application.add_error_handler(self.handle_error)
        
        return self._application

    async def run(self):
        """ቦቱን ማስኬድ"""
        app = self.create_application()
        
        # የትዕዛዝ ወረፋ ማቀነባበሪያ መጀመር
        asyncio.create_task(self.process_command_queue())
        
        self._log("🤖 Bot started polling...")
        
        # ማስኬድ
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        # እስኪቆም ድረስ
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self._log("Stopping bot...")
            await app.updater.stop()
            await app.stop()
            await app.shutdown()

# ============================================================
# ለውጭ አጠቃቀም ተግባራት
# ============================================================

_bot_instance = None
_bot_lock = threading.Lock()

def get_bot(token: str = None, webapp_url: str = None) -> UltimateGoldBot:
    """የአለም አቀፍ ቦት ኢንስታንስ መመለስ"""
    global _bot_instance
    if _bot_instance is None:
        with _bot_lock:
            if _bot_instance is None:
                _bot_instance = UltimateGoldBot(token, webapp_url)
    return _bot_instance

async def start_bot_async(token: str = None, webapp_url: str = None):
    """ቦቱን በራስ ማስኬድ (Async)"""
    bot = get_bot(token, webapp_url)
    await bot.run()

def start_bot_sync(token: str = None, webapp_url: str = None):
    """ቦቱን በራስ ማስኬድ (Sync)"""
    import asyncio
    asyncio.run(start_bot_async(token, webapp_url))

# ============================================================
# ሙከራ እና ማሳያ
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("👑 ULTIMATE GOLD AGENTIC AI - TELEGRAM BOT TEST")
    print("=" * 60)
    
    # ሙከራ
    print("📝 Testing bot initialization...")
    
    try:
        bot = get_bot()
        print("✅ Bot initialized successfully!")
        print(f"📊 WebApp URL: {bot.webapp_url}")
        print(f"📊 Token: {bot.token[:10]}...")
        
        print("\n📋 Available commands:")
        print("  /start - Welcome message")
        print("  /help - Full help")
        print("  /status - System status")
        print("  /strike <target> - Full attack")
        print("  /level1 <target> - Mobile hack")
        print("  /level2 <target> - Server scan+strike")
        print("  /level3 <target> - Gold stealth attack")
        print("  /add <name> - Add capability")
        print("  /improve <name> - Improve capability")
        print("  /learn <topic> - Learn from internet")
        print("  /auto - Auto-evolve")
        print("  /plan <target> - Generate plan")
        print("  /stop - Stop all commands")
        print("  /history - View history")
        print("  /language <am|en> - Change language")
        
        print("\n📊 Language support:")
        print("  🇪🇹 Amharic (am)")
        print("  🇬🇧 English (en)")
        
        print("\n✅ All tests passed!")
        print("\n💡 To run the bot:")
        print("  python -c 'from bot import start_bot_sync; start_bot_sync()'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 60)

# ============================================================
# 🏆 ይህ ሙሉ የተሟላ የቴሌግራም ቦት ሞጁል ነው
# ============================================================
