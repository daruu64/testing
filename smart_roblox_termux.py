#!/usr/bin/env python3
"""
Улучшенная версия Roblox Account Generator для Termux
С автоматическим поиском элементов через UI Automator
"""

import subprocess
import time
import random
import string
import os
import re
from datetime import datetime

class SmartRobloxGenerator:
    def __init__(self):
        self.accounts_created = 0
        self.max_accounts = 10
        self.accounts_file = "roblox_accounts.txt"
        self.package_name = "com.roblox.client"
        self.ui_dump_path = "/data/local/tmp/ui_dump.xml"
        
    def log(self, message):
        """Логирование с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def run_command(self, command):
        """Выполнить команду в терминале"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            self.log(f"Ошибка выполнения команды: {e}")
            return False, "", str(e)
    
    def generate_username(self):
        """Генерация случайного имени пользователя"""
        prefixes = ["Cool", "Super", "Epic", "Pro", "Best", "Top", "Fast", "Smart", "Wild", "Bold"]
        suffixes = ["Player", "Gamer", "Hero", "Star", "Master", "King", "Queen", "Legend", "Champ", "Ninja"]
        
        username = random.choice(prefixes) + random.choice(suffixes) + str(random.randint(100, 9999))
        return username
    
    def generate_password(self):
        """Генерация случайного пароля"""
        length = random.randint(10, 15)
        chars = string.ascii_letters + string.digits + "!@#$%"
        password = ''.join(random.choice(chars) for _ in range(length))
        # Убеждаемся что есть цифры и буквы
        if not any(c.isdigit() for c in password):
            password = password[:-1] + str(random.randint(0, 9))
        if not any(c.isalpha() for c in password):
            password = password[:-1] + random.choice(string.ascii_letters)
        return password
    
    def get_ui_dump(self):
        """Получить дамп UI"""
        success, _, _ = self.run_command(f"uiautomator dump {self.ui_dump_path}")
        if not success:
            return None
        
        success, content, _ = self.run_command(f"cat {self.ui_dump_path}")
        return content if success else None
    
    def find_element_bounds(self, content, text_patterns, class_patterns=None):
        """Найти границы элемента по тексту или классу"""
        patterns = []
        
        # Добавляем паттерны для поиска по тексту
        for pattern in text_patterns:
            patterns.extend([
                rf'text="{pattern}"[^>]*bounds="([^"]+)"',
                rf'content-desc="{pattern}"[^>]*bounds="([^"]+)"',
                rf'hint="{pattern}"[^>]*bounds="([^"]+)"'
            ])
        
        # Добавляем паттерны для поиска по классу
        if class_patterns:
            for pattern in class_patterns:
                patterns.append(rf'class="{pattern}"[^>]*bounds="([^"]+)"')
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                bounds = matches[0]
                # Парсим координаты [x1,y1][x2,y2]
                coords = re.findall(r'\[(\d+),(\d+)\]', bounds)
                if len(coords) == 2:
                    x1, y1 = map(int, coords[0])
                    x2, y2 = map(int, coords[1])
                    # Возвращаем центр элемента
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    self.log(f"Найден элемент '{pattern}' в позиции ({center_x}, {center_y})")
                    return center_x, center_y
        
        return None
    
    def tap_coordinate(self, x, y):
        """Тап по координатам"""
        success, _, _ = self.run_command(f"input tap {x} {y}")
        time.sleep(1.5)
        return success
    
    def input_text(self, text):
        """Ввод текста"""
        # Очищаем поле перед вводом
        self.run_command("input keyevent KEYCODE_CTRL_A")
        time.sleep(0.5)
        self.run_command("input keyevent KEYCODE_DEL")
        time.sleep(0.5)
        
        # Вводим текст
        escaped_text = text.replace(" ", "%s").replace("&", "\\&").replace("'", "\\'")
        success, _, _ = self.run_command(f"input text '{escaped_text}'")
        time.sleep(1)
        return success
    
    def swipe_screen(self, start_x, start_y, end_x, end_y, duration=500):
        """Свайп по экрану"""
        success, _, _ = self.run_command(f"input swipe {start_x} {start_y} {end_x} {end_y} {duration}")
        time.sleep(1)
        return success
    
    def wait_for_element(self, text_patterns, timeout=30, class_patterns=None):
        """Ждать появления элемента"""
        self.log(f"Ожидание элемента: {text_patterns}")
        
        for i in range(timeout):
            content = self.get_ui_dump()
            if content:
                coords = self.find_element_bounds(content, text_patterns, class_patterns)
                if coords:
                    return coords
            time.sleep(1)
        
        self.log(f"Тайм-аут ожидания элемента: {text_patterns}")
        return None
    
    def start_roblox(self):
        """Запуск приложения Roblox"""
        self.log("Запуск Roblox...")
        
        # Останавливаем приложение если оно запущено
        self.run_command(f"am force-stop {self.package_name}")
        time.sleep(2)
        
        # Запускаем приложение
        success, _, _ = self.run_command(f"am start -n {self.package_name}/.ActivityMain")
        
        if success:
            self.log("✓ Roblox запущен")
            time.sleep(8)  # Ждем полной загрузки
            return True
        else:
            self.log("✗ Не удалось запустить Roblox")
            return False
    
    def create_account(self):
        """Создание одного аккаунта"""
        self.log(f"Создание аккаунта #{self.accounts_created + 1}")
        
        username = self.generate_username()
        password = self.generate_password()
        gender = random.choice(["Male", "Female"])
        
        self.log(f"Данные: {username} | {password} | {gender}")
        
        try:
            # 1. Ищем кнопку регистрации
            self.log("Поиск кнопки регистрации...")
            signup_patterns = ["Sign Up", "SIGN UP", "Create Account", "Register"]
            
            coords = self.wait_for_element(signup_patterns, timeout=20)
            if coords:
                self.tap_coordinate(coords[0], coords[1])
                time.sleep(3)
            else:
                self.log("Кнопка регистрации не найдена, пробуем альтернативный метод...")
                # Пробуем тапнуть в нижней части экрана где обычно кнопка
                self.tap_coordinate(540, 1600)
                time.sleep(3)
            
            # 2. Ввод имени пользователя
            self.log("Поиск поля Username...")
            username_patterns = ["Username", "USER NAME", "Enter username"]
            username_classes = ["android.widget.EditText"]
            
            coords = self.wait_for_element(username_patterns, timeout=15, class_patterns=username_classes)
            if coords:
                self.tap_coordinate(coords[0], coords[1])
                time.sleep(1)
                self.input_text(username)
                self.log(f"✓ Введен username: {username}")
            else:
                self.log("✗ Поле Username не найдено")
                return False
            
            # 3. Ввод пароля
            self.log("Поиск поля Password...")
            password_patterns = ["Password", "PASSWORD", "Enter password"]
            
            coords = self.wait_for_element(password_patterns, timeout=10, class_patterns=username_classes)
            if coords:
                self.tap_coordinate(coords[0], coords[1])
                time.sleep(1)
                self.input_text(password)
                self.log(f"✓ Введен password")
            else:
                self.log("✗ Поле Password не найдено")
                return False
            
            # 4. Установка даты рождения
            self.log("Настройка даты рождения...")
            
            # Месяц
            month_patterns = ["Month", "MONTH"]
            coords = self.wait_for_element(month_patterns, timeout=10)
            if coords:
                self.tap_coordinate(coords[0], coords[1])
                time.sleep(1)
                # Выбираем случайный месяц (тапаем вниз на случайное количество)
                for _ in range(random.randint(1, 12)):
                    self.run_command("input keyevent KEYCODE_DPAD_DOWN")
                    time.sleep(0.2)
                self.run_command("input keyevent KEYCODE_ENTER")
                time.sleep(1)
            
            # День
            day_patterns = ["Day", "DAY"]
            coords = self.wait_for_element(day_patterns, timeout=10)
            if coords:
                self.tap_coordinate(coords[0], coords[1])
                time.sleep(1)
                for _ in range(random.randint(1, 28)):
                    self.run_command("input keyevent KEYCODE_DPAD_DOWN")
                    time.sleep(0.1)
                self.run_command("input keyevent KEYCODE_ENTER")
                time.sleep(1)
            
            # Год
            year_patterns = ["Year", "YEAR"]
            coords = self.wait_for_element(year_patterns, timeout=10)
            if coords:
                self.tap_coordinate(coords[0], coords[1])
                time.sleep(1)
                # Выбираем год для возраста 18+ (примерно 20-30 лет назад)
                for _ in range(random.randint(20, 35)):
                    self.run_command("input keyevent KEYCODE_DPAD_DOWN")
                    time.sleep(0.1)
                self.run_command("input keyevent KEYCODE_ENTER")
                time.sleep(1)
            
            # 5. Выбор пола
            self.log(f"Выбор пола: {gender}")
            if gender == "Male":
                coords = self.wait_for_element(["Male", "MALE"], timeout=10)
            else:
                coords = self.wait_for_element(["Female", "FEMALE"], timeout=10)
            
            if coords:
                self.tap_coordinate(coords[0], coords[1])
                time.sleep(1)
            
            # 6. Финальная регистрация
            self.log("Поиск финальной кнопки регистрации...")
            final_signup_patterns = ["Sign Up", "SIGN UP", "Create Account", "CREATE ACCOUNT", "Continue"]
            
            coords = self.wait_for_element(final_signup_patterns, timeout=10)
            if coords:
                self.tap_coordinate(coords[0], coords[1])
                self.log("✓ Кнопка регистрации нажата")
            else:
                # Пробуем нажать в нижней части экрана
                self.tap_coordinate(540, 1800)
            
            time.sleep(5)
            
            # 7. Проверка на капчу и ожидание завершения
            self.log("Ожидание завершения регистрации...")
            
            for i in range(90):  # Ждем до 90 секунд
                content = self.get_ui_dump()
                if content:
                    if any(word in content.lower() for word in ["captcha", "verify", "robot", "human"]):
                        if i == 0:  # Показываем сообщение только один раз
                            self.log("⚠️  Обнаружена капча - решите её вручную в приложении")
                        time.sleep(2)
                        continue
                    
                    # Проверяем успешное создание аккаунта
                    if any(word in content.lower() for word in ["home", "avatar", "customize", "robux", "profile"]):
                        self.log("✓ Аккаунт успешно создан!")
                        self.save_account(username, password)
                        return True
                    
                    # Проверяем на ошибки
                    if any(word in content.lower() for word in ["error", "already taken", "invalid", "failed"]):
                        self.log("✗ Ошибка при создании аккаунта")
                        return False
                
                time.sleep(2)
            
            self.log("✗ Тайм-аут создания аккаунта")
            return False
            
        except Exception as e:
            self.log(f"Ошибка создания аккаунта: {e}")
            return False
    
    def save_account(self, username, password):
        """Сохранение данных аккаунта"""
        try:
            with open(self.accounts_file, "a", encoding="utf-8") as f:
                f.write(f"{username}:{password}\n")
            self.log(f"✓ Аккаунт сохранен: {username}:{password}")
        except Exception as e:
            self.log(f"Ошибка сохранения аккаунта: {e}")
    
    def clear_app_cache(self):
        """Очистка кеша и данных приложения"""
        self.log("Очистка данных Roblox...")
        
        # Останавливаем приложение
        self.run_command(f"am force-stop {self.package_name}")
        time.sleep(3)
        
        # Очищаем данные приложения (требует root)
        success, _, _ = self.run_command(f"pm clear {self.package_name}")
        
        if success:
            self.log("✓ Данные приложения очищены")
        else:
            self.log("✗ Не удалось очистить данные (требуются root права)")
        
        time.sleep(3)
    
    def run(self):
        """Основной цикл программы"""
        self.log("=" * 60)
        self.log("🤖 Smart Roblox Account Generator для Termux")
        self.log("=" * 60)
        
        # Проверки
        self.log("Выполнение предварительных проверок...")
        
        # Проверка UI Automator
        success, _, _ = self.run_command("uiautomator dump --help")
        if not success:
            self.log("✗ UI Automator недоступен")
            return
        else:
            self.log("✓ UI Automator доступен")
        
        # Проверка Roblox
        success, output, _ = self.run_command(f"pm list packages | grep {self.package_name}")
        if not success or self.package_name not in output:
            self.log("✗ Roblox не установлен")
            return
        else:
            self.log("✓ Roblox найден")
        
        self.log(f"Цель: создать {self.max_accounts} аккаунтов")
        self.log(f"Файл: {self.accounts_file}")
        
        # Создание файла для аккаунтов
        if not os.path.exists(self.accounts_file):
            with open(self.accounts_file, "w", encoding="utf-8") as f:
                f.write("# Roblox Accounts (username:password)\n")
                f.write("# Generated by Smart Roblox Generator\n")
                f.write("# " + "=" * 40 + "\n")
        
        # Основной цикл
        while self.accounts_created < self.max_accounts:
            try:
                self.log(f"\n{'='*20} Аккаунт {self.accounts_created + 1}/{self.max_accounts} {'='*20}")
                
                # Очистка перед новым аккаунтом (кроме первого)
                if self.accounts_created > 0:
                    self.clear_app_cache()
                
                # Запуск Roblox
                if not self.start_roblox():
                    self.log("Пропускаем итерацию из-за ошибки запуска")
                    continue
                
                # Создание аккаунта
                if self.create_account():
                    self.accounts_created += 1
                    self.log(f"🎉 Успешно создано: {self.accounts_created}/{self.max_accounts}")
                    
                    if self.accounts_created >= self.max_accounts:
                        break
                else:
                    self.log("❌ Не удалось создать аккаунт")
                
                # Пауза между аккаунтами
                if self.accounts_created < self.max_accounts:
                    self.log("⏳ Пауза перед следующим аккаунтом...")
                    time.sleep(10)
                    
            except KeyboardInterrupt:
                self.log("\n⚠️  Программа остановлена пользователем")
                break
            except Exception as e:
                self.log(f"❌ Неожиданная ошибка: {e}")
                time.sleep(5)
                continue
        
        # Финальная очистка
        self.clear_app_cache()
        
        # Итоговая статистика
        self.log("\n" + "=" * 60)
        self.log("📊 РЕЗУЛЬТАТЫ:")
        self.log(f"✅ Создано аккаунтов: {self.accounts_created}")
        self.log(f"📁 Файл с аккаунтами: {self.accounts_file}")
        
        if self.accounts_created > 0:
            self.log("\n📋 Последние созданные аккаунты:")
            try:
                with open(self.accounts_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines[-self.accounts_created:]:
                        if ":" in line and not line.startswith("#"):
                            self.log(f"   {line.strip()}")
            except:
                pass
        
        self.log("=" * 60)
        self.log("🏁 Программа завершена!")

def main():
    """Точка входа"""
    generator = SmartRobloxGenerator()
    generator.run()

if __name__ == "__main__":
    main()
