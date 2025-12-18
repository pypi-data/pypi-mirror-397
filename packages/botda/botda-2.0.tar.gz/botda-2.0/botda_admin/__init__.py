#!/usr/bin/env python3
"""
Сервер системы удаленного управления с GUI для создания файлов
Поддерживает создание файлов через блокнот-подобный интерфейс
"""

import json
import time
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import sys
import os
import select
from collections import deque
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import tempfile

# Кроссплатформенные импорты
try:
    # Для Linux/macOS
    import termios
    import tty
    HAS_TERMIOS = True
except ImportError:
    # Для Windows
    import msvcrt
    HAS_TERMIOS = False

class FileCreatorGUI:
    """GUI для создания файлов и папок"""
    
    def __init__(self):
        self.root = None
        self.text_widget = None
        self.current_content = ""
        self.filename = ""
        self.execute_after = False
        self.open_after = False
        self.result_event = threading.Event()
        self.result = None
    
    def create_file_dialog(self, default_name="", execute=False, open_after=False):
        """Открывает диалог создания файла"""
        self.filename = default_name
        self.execute_after = execute
        self.open_after = open_after
        self.result_event.clear()
        
        # Запускаем GUI в отдельном потоке
        gui_thread = threading.Thread(target=self._create_gui)
        gui_thread.daemon = True
        gui_thread.start()
        
        # Ждем завершения
        self.result_event.wait()
        return self.result
    
    def _create_gui(self):
        """Создает GUI окно"""
        self.root = tk.Tk()
        self.root.title(f"Создание файла: {self.filename}")
        self.root.geometry("800x600")
        
        # Настраиваем иконку если есть
        try:
            if sys.platform == "win32":
                self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # Фрейм для имени файла
        name_frame = tk.Frame(self.root)
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(name_frame, text="Имя файла:").pack(side=tk.LEFT)
        name_entry = tk.Entry(name_frame, width=50)
        name_entry.insert(0, self.filename)
        name_entry.pack(side=tk.LEFT, padx=5)
        
        # Фрейм с кнопками
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(button_frame, text="📁 Открыть в проводнике", 
                 command=self._open_in_explorer).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="▶ Запустить после создания", 
                 command=self._toggle_execute).pack(side=tk.LEFT, padx=2)
        
        # Текстовое поле
        text_frame = tk.Frame(self.root)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.text_widget = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, font=("Consolas", 10)
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Начальный текст
        initial_text = """# Введите содержимое файла
# Файл будет создан после закрытия этого окна
# Используйте Ctrl+S для сохранения, Ctrl+Q для выхода
"""
        self.text_widget.insert(1.0, initial_text)
        
        # Фрейм с кнопками сохранения
        save_frame = tk.Frame(self.root)
        save_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(save_frame, text="💾 Сохранить и закрыть", 
                 command=self._save_and_close, bg="green", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(save_frame, text="❌ Отмена", 
                 command=self._cancel).pack(side=tk.LEFT, padx=2)
        
        # Бинды клавиш
        self.root.bind('<Control-s>', lambda e: self._save_and_close())
        self.root.bind('<Control-q>', lambda e: self._cancel())
        self.root.bind('<Control-o>', lambda e: self._open_in_explorer())
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)
        
        # Обновляем имя файла при изменении
        def update_filename(*args):
            self.filename = name_entry.get()
            self.root.title(f"Создание файла: {self.filename}")
        
        name_entry.bind('<KeyRelease>', update_filename)
        
        self.root.mainloop()
    
    def _toggle_execute(self):
        """Переключает флаг выполнения"""
        self.execute_after = not self.execute_after
        print(f"Запуск после создания: {'ВКЛ' if self.execute_after else 'ВЫКЛ'}")
    
    def _open_in_explorer(self):
        """Открывает текущий путь в проводнике"""
        try:
            if sys.platform == "win32":
                os.startfile(os.path.dirname(os.path.abspath(self.filename)) or ".")
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "."])
            else:
                subprocess.Popen(["xdg-open", "."])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть проводник: {e}")
    
    def _save_and_close(self):
        """Сохраняет и закрывает окно"""
        self.current_content = self.text_widget.get(1.0, tk.END).rstrip('\n')
        self.result = {
            'filename': self.filename,
            'content': self.current_content,
            'execute': self.execute_after,
            'open_after': self.open_after,
            'success': True
        }
        self.root.destroy()
        self.result_event.set()
    
    def _cancel(self):
        """Отменяет создание"""
        self.result = {
            'success': False,
            'message': 'Отменено пользователем'
        }
        self.root.destroy()
        self.result_event.set()

class ClientManager:
    def __init__(self):
        self.clients = {}
        self.commands = {}
        self.client_commands = {}
        self.command_history = deque(maxlen=50)
        self.results = {}
        self.command_counter = 0
        self.active_filter = None
        self.selected_clients = set()
        self.live_output = {}
        self.result_listeners = []
        self.file_creator = FileCreatorGUI()
        
    def register_client(self, client_id, ip, os_info):
        now = datetime.now()
        
        if client_id not in self.clients:
            self.clients[client_id] = {
                'id': client_id, 'ip': ip, 'os': os_info,
                'first_seen': now, 'last_seen': now,
                'online': True, 'command_count': 0, 'last_command': None,
                'current_dir': '/'
            }
            print(f"\n[+] Новый клиент: {ip} ({os_info})")
            return True
        else:
            client = self.clients[client_id]
            client['last_seen'] = now
            client['online'] = True
            return False
    
    def process_special_command(self, command_text, client_info=None):
        """Обрабатывает специальные команды создания файлов/папок"""
        parts = command_text.strip().split()
        if not parts:
            return None
        
        cmd = parts[0].lower()
        
        if cmd in ['create', 'mkdir', 'touch', 'new']:
            # Определяем тип операции
            if len(parts) < 2:
                return "Ошибка: укажите имя файла/папки"
            
            name = parts[1]
            execute = len(parts) > 2 and parts[2].lower() in ['true', '1', 'yes', 'run']
            open_after = len(parts) > 2 and parts[2].lower() in ['open', 'explorer']
            
            if cmd == 'mkdir' or 'folder' in name.lower():
                # Создание папки
                return f"mkdir {name}"
            else:
                # Создание файла - открываем GUI
                print(f"\n[GUI] Открываю редактор для файла: {name}")
                print(f"[GUI] Запуск после: {execute}, Открыть после: {open_after}")
                
                # Запускаем GUI диалог
                result = self.file_creator.create_file_dialog(name, execute, open_after)
                
                if result and result['success']:
                    # Формируем команду для создания файла
                    filename = result['filename']
                    content = result['content']
                    
                    # Экранируем специальные символы
                    safe_content = content.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
                    
                    if sys.platform == "win32":
                        # Windows команда
                        cmd_line = f'echo.{safe_content} > "{filename}"'
                    else:
                        # Linux/Mac команда
                        cmd_line = f'cat > "{filename}" << \'EOF\'\n{safe_content}\nEOF'
                    
                    # Добавляем выполнение если нужно
                    if result.get('execute'):
                        if filename.endswith(('.py', '.pyw')):
                            cmd_line += f' && python "{filename}"'
                        elif filename.endswith(('.sh', '.bash')):
                            cmd_line += f' && bash "{filename}"'
                        elif filename.endswith('.ps1'):
                            cmd_line += f' && powershell -File "{filename}"'
                        else:
                            cmd_line += f' && "{filename}"'
                    
                    # Добавляем открытие в проводнике если нужно
                    if result.get('open_after'):
                        if sys.platform == "win32":
                            cmd_line += f' && explorer /select,"{os.path.abspath(filename)}"'
                        elif sys.platform == "darwin":
                            cmd_line += f' && open "{os.path.dirname(filename)}"'
                        else:
                            cmd_line += f' && xdg-open "{os.path.dirname(filename)}"'
                    
                    return cmd_line
                else:
                    return "Отменено пользователем"
        
        return None
    
    def set_command(self, command_text, target_filter=None):
        self.command_counter += 1
        cmd_id = f"CMD{self.command_counter:06d}"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        
        # Проверяем специальные команды
        special_cmd = self.process_special_command(command_text)
        if special_cmd:
            command_text = special_cmd
            print(f"[Спец. команда] Преобразовано в: {command_text[:100]}...")
        
        command_data = {
            'id': cmd_id, 'command': command_text, 'timestamp': timestamp,
            'target_filter': target_filter, 'created_at': datetime.now(),
            'status': 'pending', 'target_clients': []
        }
        
        target_clients = []
        if self.selected_clients:
            target_clients = list(self.selected_clients)
        elif target_filter:
            target_clients = self._get_clients_by_filter(target_filter)
        else:
            target_clients = [c['id'] for c in self.get_online_clients()]
        
        command_data['target_clients'] = target_clients
        
        sent_count = 0
        for client_id in target_clients:
            if client_id in self.clients:
                self.client_commands[client_id] = cmd_id
                self.clients[client_id]['command_count'] += 1
                self.clients[client_id]['last_command'] = datetime.now()
                sent_count += 1
        
        self.commands[cmd_id] = command_data
        self.command_history.append(command_data)
        self.live_output[cmd_id] = {}
        
        print(f"\n[→] Команда отправлена {sent_count} клиентам")
        print(f"    ID: {cmd_id}")
        print(f"    Текст: {command_text[:80]}{'...' if len(command_text) > 80 else ''}")
        
        return cmd_id, sent_count
    
    def _get_clients_by_filter(self, filter_dict):
        result = []
        for client_id, client in self.clients.items():
            if not client['online']:
                continue
            
            match = True
            if 'os' in filter_dict:
                if filter_dict['os'].lower() not in client['os'].lower():
                    match = False
            if 'os_prefix' in filter_dict:
                if not client['os'].lower().startswith(filter_dict['os_prefix'].lower()):
                    match = False
            if 'ip' in filter_dict:
                if client['ip'] != filter_dict['ip']:
                    match = False
            if 'ip_prefix' in filter_dict:
                if not client['ip'].startswith(filter_dict['ip_prefix']):
                    match = False
            
            if match:
                result.append(client_id)
        
        return result
    
    def get_online_clients(self, sort_by='ip'):
        online = [c for c in self.clients.values() if c['online']]
        
        if sort_by == 'ip':
            online.sort(key=lambda x: [
                int(part) if part.isdigit() else part 
                for part in x['ip'].split('.')
            ])
        elif sort_by == 'os':
            online.sort(key=lambda x: x['os'].lower())
        elif sort_by == 'last_seen':
            online.sort(key=lambda x: x['last_seen'], reverse=True)
        
        return online
    
    def get_command_for_client(self, client_id, ip, os_info):
        self.register_client(client_id, ip, os_info)
        
        if client_id in self.client_commands:
            cmd_id = self.client_commands[client_id]
            if cmd_id in self.commands:
                cmd = self.commands[cmd_id]
                return f"{cmd['timestamp']}|{cmd['command']}"
        
        return ""
    
    def save_result(self, client_id, command_str, exit_code, output):
        parts = command_str.split('|', 1)
        if len(parts) < 2:
            return False
        
        timestamp, cmd_text = parts
        
        cmd_id = None
        for cid, cmd in self.commands.items():
            if cmd['timestamp'] == timestamp:
                cmd_id = cid
                break
        
        if not cmd_id or client_id not in self.clients:
            return False
        
        if cmd_id not in self.results:
            self.results[cmd_id] = []
        
        result = {
            'client_id': client_id,
            'client_ip': self.clients[client_id]['ip'],
            'client_os': self.clients[client_id]['os'],
            'exit_code': exit_code,
            'output': output,
            'received_at': datetime.now()
        }
        
        self.results[cmd_id].append(result)
        
        if cmd_id not in self.live_output:
            self.live_output[cmd_id] = {}
        
        output_lines = output.strip().split('\n')
        if not output_lines or output_lines == ['']:
            output_lines = ["(нет вывода)"]
        
        self.live_output[cmd_id][client_id] = {
            'ip': self.clients[client_id]['ip'],
            'os': self.clients[client_id]['os'],
            'exit_code': exit_code,
            'lines': output_lines
        }
        
        if client_id in self.client_commands and self.client_commands[client_id] == cmd_id:
            del self.client_commands[client_id]
        
        for listener in self.result_listeners:
            listener(cmd_id, client_id, result)
        
        client_ip = self.clients[client_id]['ip']
        print(f"\n[←] Ответ от {client_ip}:")
        print(f"    Код: {exit_code}")
        if output and len(output.strip()) > 0:
            print(f"    Вывод: {output[:200]}{'...' if len(output) > 200 else ''}")
        
        return True
    
    def get_live_output(self, cmd_id):
        return self.live_output.get(cmd_id, {})

class ServerAPI(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            manager = self.server.client_manager
            
            if self.path == '/check':
                client_id = data.get('client_id')
                ip = data.get('ip')
                os_info = data.get('os')
                
                command = manager.get_command_for_client(client_id, ip, os_info)
                
                self._send_json({'command': command})
                
            elif self.path == '/result':
                client_id = data.get('client_id')
                command_str = data.get('command')
                exit_code = data.get('exit_code')
                output = data.get('output')
                
                success = manager.save_result(client_id, command_str, exit_code, output)
                
                self._send_json({'success': success})
                
        except Exception as e:
            print(f"[API ERROR] {e}")
            self.send_error(500)
    
    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

class ConsoleUI:
    def __init__(self, manager, host, port):
        self.manager = manager
        self.host = host
        self.port = port
        self.running = True
        self.mode = 'main'
        self.sort_by = 'ip'
        self.input_buffer = ""
        self.current_cmd_id = None
        self.refresh_rate = 2
        self.last_refresh = 0
        
        manager.result_listeners.append(self.on_new_result)
    
    def on_new_result(self, cmd_id, client_id, result):
        if self.mode == 'live' and cmd_id == self.current_cmd_id:
            self.display_live_output()
    
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        ip = self.get_local_ip()
        online = len(self.manager.get_online_clients())
        pending = len(self.manager.client_commands)
        
        print("╔══════════════════════════════════════════════════════════════╗")
        title = "СЕРВЕР УПРАВЛЕНИЯ КЛИЕНТАМИ v2.0"
        address = f"{ip}:{self.port}"
        spaces = 58 - len(title) - len(address)
        print(f"║ {title}{' ' * spaces}{address} ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║ Онлайн: {online:<3} │ Ожидание: {pending:<3} │ Сортировка: {self.sort_by:<8} ║")
        
        if self.manager.selected_clients:
            selected_count = len(self.manager.selected_clients)
            selected_ips = [self.manager.clients[cid]['ip'] for cid in list(self.manager.selected_clients)[:3]]
            selected_text = f"Выбрано: {selected_count} ({', '.join(selected_ips)}"
            if selected_count > 3:
                selected_text += f" +{selected_count-3})"
            else:
                selected_text += ")"
            print(f"║ {selected_text:<56} ║")
        
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║ Специальные команды:                                        ║")
        print("║   create <name> [run/open] - создать файл с редактором      ║")
        print("║   mkdir <name>            - создать папку                  ║")
        print("║   touch <name>            - создать пустой файл            ║")
        print("╠══════════════════════════════════════════════════════════════╣")
    
    def display_clients(self):
        clients = self.manager.get_online_clients(self.sort_by)
        
        if clients:
            print("║ №  Статус IP              ОС                      Время   ║")
            print("╠══════════════════════════════════════════════════════════════╣")
            
            for i, client in enumerate(clients[:15]):
                sec_ago = (datetime.now() - client['last_seen']).seconds
                
                if sec_ago < 10:
                    status = "🟢"
                elif sec_ago < 30:
                    status = "🟡"
                else:
                    status = "⚪"
                
                ip = client['ip'][:15].ljust(15)
                os_short = client['os'][:20]
                if len(client['os']) > 20:
                    os_short = os_short[:17] + "..."
                
                prefix = "✓" if client['id'] in self.manager.selected_clients else " "
                
                print(f"║ {prefix}{i+1:2d} {status} {ip} {os_short:20} {sec_ago:4d}с ║")
            
            if len(clients) > 15:
                print(f"║ ... и ещё {len(clients) - 15} устройств                        ║")
        else:
            print("║              Нет подключенных устройств                 ║")
        
        print("╠══════════════════════════════════════════════════════════════╣")
    
    def display_footer(self):
        if self.mode == 'main':
            print("║ 1-15:Выбор  S:Сорт  F:Фильтр  C:Команда  L:Live  R:Рез  X:Выход ║")
        elif self.mode == 'command':
            if self.input_buffer:
                print(f"║ Команда: {self.input_buffer:<48} ║")
            else:
                print("║ Введите команду (Enter-отправить, Esc-отмена):           ║")
                print("║ Примеры: create script.py run  mkdir folder  touch file.txt ║")
        elif self.mode == 'filter':
            print("║ 1:Все 2:Windows 3:Linux 4:Ubuntu 5:По IP C:Очистить B:Назад  ║")
        elif self.mode == 'sort':
            print("║ 1:По IP 2:По ОС 3:По активности B:Назад                     ║")
        
        print("╚══════════════════════════════════════════════════════════════╝")
    
    def display_main(self):
        self.clear_screen()
        self.display_header()
        self.display_clients()
        self.display_footer()
    
    def get_key(self):
        try:
            if HAS_TERMIOS:
                import sys
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        ch = sys.stdin.read(1)
                        
                        if ch == '\x1b':
                            next_ch = sys.stdin.read(1) if select.select([sys.stdin], [], [], 0.01)[0] else ''
                            if next_ch == '':
                                return 'ESC'
                        elif ch == '\r' or ch == '\n':
                            return 'ENTER'
                        elif ch == '\x7f' or ch == '\x08':
                            return 'BACKSPACE'
                        elif ch.isprintable():
                            return ch.lower()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            else:
                import time
                start_time = time.time()
                while (time.time() - start_time) < 0.1:
                    if msvcrt.kbhit():
                        try:
                            ch = msvcrt.getch().decode('utf-8', errors='ignore')
                        except:
                            ch = msvcrt.getch().decode('cp866', errors='ignore')
                        
                        if ch == '\r' or ch == '\n':
                            return 'ENTER'
                        elif ch == '\x1b':
                            return 'ESC'
                        elif ch == '\x08' or ch == '\x7f':
                            return 'BACKSPACE'
                        elif ch.isprintable():
                            return ch.lower()
                    
                    time.sleep(0.01)
                
        except Exception as e:
            pass
        
        return None
    
    def handle_main_mode(self):
        key = self.get_key()
        
        if key:
            if key.isdigit() and '1' <= key <= '9':
                idx = int(key)
                clients = self.manager.get_online_clients(self.sort_by)
                if 0 < idx <= len(clients):
                    client = clients[idx-1]
                    if client['id'] in self.manager.selected_clients:
                        self.manager.selected_clients.remove(client['id'])
                        print(f"\n[-] Убрано: {client['ip']}")
                    else:
                        self.manager.selected_clients.add(client['id'])
                        print(f"\n[+] Выбрано: {client['ip']}")
                    time.sleep(0.5)
            
            elif key == 's':
                self.mode = 'sort'
                self.input_buffer = ""
            
            elif key == 'f':
                self.mode = 'filter'
                self.input_buffer = ""
            
            elif key == 'c':
                if (self.manager.selected_clients or 
                    self.manager.get_online_clients()):
                    self.mode = 'command'
                    self.input_buffer = ""
                else:
                    print("\n[!] Нет клиентов для отправки команды")
                    time.sleep(1)
            
            elif key == 'l':
                if self.manager.command_history:
                    self.current_cmd_id = self.manager.command_history[-1]['id']
                    self.mode = 'live'
                else:
                    print("\n[!] Нет выполненных команд")
                    time.sleep(1)
            
            elif key == 'r':
                if self.manager.command_history:
                    self.show_results()
                else:
                    print("\n[!] Нет результатов")
                    time.sleep(1)
            
            elif key == 'x':
                self.running = False
    
    def handle_command_mode(self):
        key = self.get_key()
        
        if key == 'ESC':
            self.mode = 'main'
            self.input_buffer = ""
        
        elif key == 'ENTER' and self.input_buffer.strip():
            cmd_text = self.input_buffer.strip()
            
            target_filter = None
            if self.manager.selected_clients:
                pass
            elif self.manager.active_filter:
                target_filter = self.manager.active_filter
            
            cmd_id, sent = self.manager.set_command(cmd_text, target_filter)
            
            print(f"\n[!] Команда отправлена")
            print(f"    Нажмите 'L' для отслеживания выполнения")
            
            self.input_buffer = ""
            self.mode = 'main'
            time.sleep(2)
        
        elif key == 'BACKSPACE':
            self.input_buffer = self.input_buffer[:-1]
        
        elif key and key.isprintable():
            self.input_buffer += key
    
    def run(self):
        print(f"[!] Сервер запущен: {self.get_local_ip()}:{self.port}")
        print("[!] Ожидание подключений...")
        print("[!] Для создания файлов используйте команды:")
        print("    create <filename> [run/open] - создать файл с редактором")
        print("    mkdir <foldername>          - создать папку")
        print("    touch <filename>            - создать пустой файл")
        time.sleep(2)
        
        while self.running:
            if self.mode == 'main':
                self.display_main()
                self.handle_main_mode()
            
            time.sleep(0.05)

def run_server():
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    
    manager = ClientManager()
    
    class ThreadedHTTPServer(HTTPServer):
        client_manager = manager
    
    server = ThreadedHTTPServer(('0.0.0.0', port), ServerAPI)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    console = ConsoleUI(manager, '0.0.0.0', port)
    console.run()
    
    print("\n[!] Остановка сервера...")
    server.shutdown()

if __name__ == "__main__":
    run_server()