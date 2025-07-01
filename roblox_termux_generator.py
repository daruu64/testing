#!/usr/bin/env python3
"""
Roblox Account Generator for Termux
Автоматически создает аккаунты в мобильном приложении Roblox
Требует установленный Roblox и настроенный UI Automator
"""

import subprocess
import time
import random
import string
import os
from datetime import datetime

class RobloxTermuxGenerator:
    def __init__(self):
        self.accounts_created = 0
        self.max_accounts = 10
        self.accounts_file = "roblox_accounts.txt"
        self.package_name = "com.roblox.client"
        
    def log(self, message):
        """Логирование с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def run_command(self, command):
        """Выполнить команду в терминале"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            self.log(f"Ошибка выполнения команды: {e}")
            return False, "", str(e)
    
    def generate_username(self):
        """Генерация случайного имени пользователя"""
        adjectives = ["Cool", "Super", "Epic", "Awesome", "Amazing", "Fantastic", "Great", "Best", "Top", "Pro"]
        nouns = ["Player", "Gamer", "User", "Hero", "Star", "King", "Queen", "Master", "Legend", "Champion"]
        
        username = random.choice(adjectives) + random.choice(nouns) + str(random.randint(10, 999))
        return username
    
    def generate_password(self):
        """Генерация случайного пароля"""
        length = random.randint(8, 12)
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
    
    def check_app_installed(self):
        """Проверить, установлено ли приложение Roblox"""
        self.log("Проверка установки Roblox...")
        success, output, error = self.run_command(f"pm list packages | grep {self.package_name}")
        
        if success and self.package_name in output:
            self.log("✓ Roblox найден")
            return True
        else:
            self.log("✗ Roblox не найден. Установите приложение из Play Store")
            return False
    
    def start_roblox(self):
        """Запуск приложения Roblox"""
        self.log("Запуск Roblox...")
        success, _, _ = self.run_command(f"am start -n {self.package_name}/.ActivityMain")
        
        if success:
            self.log("✓ Roblox запущен")
            time.sleep(5)  # Ждем загрузки
            return True
        else:
            self.log("✗ Не удалось запустить Roblox")
            return False
    
    def tap_coordinate(self, x, y):
        """Тап по координатам"""
        success, _, _ = self.run_command(f"input tap {x} {y}")
        time.sleep(1)
        return success
    
    def input_text(self, text):
        """Ввод текста"""
        # Экранируем специальные символы
        escaped_text = text.replace(" ", "%s").replace("&", "\\&")
        success, _, _ = self.run_command(f"input text '{escaped_text}'")
        time.sleep(1)
        return success
    
    def find_and_tap_text(self, text):
        """Найти текст на экране и тапнуть по нему"""
        self.log(f"Поиск текста: {text}")
        
        # Получаем дамп UI
        success, output, _ = self.run_command("uiautomator dump /data/local/tmp/ui_dump.xml")
        if not success:
            return False
        
        # Читаем дамп
        success, dump_content, _ = self.run_command("cat /data/local/tmp/ui_dump.xml")
        if not success:
            return False
        
        if text.lower() in dump_content.lower():
            self.log(f"✓ Найден текст: {text}")
            return True
        else:
            self.log(f"✗ Не найден текст: {text}")
            return False
    
    def wait_for_element(self, text, timeout=30):
        """Ждать появления элемента с текстом"""
        self.log(f"Ожидание элемента: {text}")
        
        for i in range(timeout):
            if self.find_and_tap_text(text):
                return True
            time.sleep(1)
        
        self.log(f"Тайм-аут ожидания элемента: {text}")
        return False
    
    def create_account(self):
        """Создание одного аккаунта"""
        self.log(f"Создание аккаунта #{self.accounts_created + 1}")
        
        username = self.generate_username()
        password = self.generate_password()
        gender = random.choice(["Male", "Female"])
        
        self.log(f"Генерация данных: {username} | {password} | {gender}")
        
        try:
            # Координаты для различных элементов (могут потребовать настройки)
            # Эти координаты нужно настроить под ваш экран
            
            # 1. Тап по кнопке "Sign Up" (примерные координаты)
            self.log("Поиск кнопки регистрации...")
            time.sleep(3)
            
            # Попробуем найти кнопку регистрации
            signup_coords = [(540, 1400), (540, 1500), (540, 1600)]  # Различные позиции
            
            for coord in signup_coords:
                self.tap_coordinate(coord[0], coord[1])
                time.sleep(2)
                
                # Проверяем, открылась ли форма регистрации
                success, output, _ = self.run_command("uiautomator dump /data/local/tmp/ui_dump.xml")
                if success:
                    success, dump_content, _ = self.run_command("cat /data/local/tmp/ui_dump.xml")
                    if "username" in dump_content.lower() or "password" in dump_content.lower():
                        self.log("✓ Форма регистрации открыта")
                        break
            
            time.sleep(2)
            
            # 2. Ввод имени пользователя
            self.log("Ввод имени пользователя...")
            # Координаты поля username (нужно настроить)
            username_coords = [(540, 800), (540, 900), (540, 1000)]
            
            for coord in username_coords:
                self.tap_coordinate(coord[0], coord[1])
                time.sleep(1)
                self.input_text(username)
                time.sleep(1)
                break
            
            # 3. Ввод пароля
            self.log("Ввод пароля...")
            # Координаты поля password
            password_coords = [(540, 1000), (540, 1100), (540, 1200)]
            
            for coord in password_coords:
                self.tap_coordinate(coord[0], coord[1])
                time.sleep(1)
                self.input_text(password)
                time.sleep(1)
                break
            
            # 4. Установка даты рождения
            self.log("Установка даты рождения...")
            # Месяц
            self.tap_coordinate(200, 1300)  # Dropdown месяца
            time.sleep(1)
            self.tap_coordinate(200, 1400)  # Выбор месяца
            time.sleep(1)
            
            # День
            self.tap_coordinate(400, 1300)  # Dropdown дня
            time.sleep(1)
            self.tap_coordinate(400, 1400)  # Выбор дня
            time.sleep(1)
            
            # Год
            self.tap_coordinate(600, 1300)  # Dropdown года
            time.sleep(1)
            self.tap_coordinate(600, 1400)  # Выбор года
            time.sleep(1)
            
            # 5. Выбор пола
            self.log(f"Выбор пола: {gender}")
            if gender == "Male":
                self.tap_coordinate(400, 1500)  # Кнопка Male
            else:
                self.tap_coordinate(680, 1500)  # Кнопка Female
            time.sleep(1)
            
            # 6. Нажатие кнопки "Sign Up"
            self.log("Нажатие кнопки регистрации...")
            self.tap_coordinate(540, 1700)  # Кнопка Sign Up
            time.sleep(5)
            
            # 7. Ожидание завершения регистрации или обработка капчи
            self.log("Ожидание завершения регистрации...")
            
            # Проверяем на капчу
            for i in range(60):  # Ждем до 60 секунд
                success, output, _ = self.run_command("uiautomator dump /data/local/tmp/ui_dump.xml")
                if success:
                    success, dump_content, _ = self.run_command("cat /data/local/tmp/ui_dump.xml")
                    if success:
                        if "captcha" in dump_content.lower() or "verify" in dump_content.lower():
                            self.log("⚠️  Обнаружена капча - требуется ручное решение")
                            self.log("Решите капчу в приложении, программа подождет...")
                            time.sleep(30)  # Ждем решения капчи
                            continue
                        elif "home" in dump_content.lower() or "avatar" in dump_content.lower():
                            self.log("✓ Аккаунт успешно создан!")
                            self.save_account(username, password)
                            return True
                
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
        """Очистка кеша приложения Roblox"""
        self.log("Очистка кеша Roblox...")
        
        # Останавливаем приложение
        self.run_command(f"am force-stop {self.package_name}")
        time.sleep(2)
        
        # Очищаем кеш
        success, _, _ = self.run_command(f"pm clear {self.package_name}")
        
        if success:
            self.log("✓ Кеш очищен")
        else:
            self.log("✗ Не удалось очистить кеш")
        
        time.sleep(3)
    
    def run(self):
        """Основной цикл программы"""
        self.log("=" * 50)
        self.log("Roblox Account Generator для Termux")
        self.log("=" * 50)
        
        # Проверка установки Roblox
        if not self.check_app_installed():
            return
        
        # Проверка root-доступа
        success, _, _ = self.run_command("id")
        if success:
            self.log("✓ Доступ к командам получен")
        else:
            self.log("✗ Нет доступа к командам")
            return
        
        self.log(f"Цель: создать {self.max_accounts} аккаунтов")
        self.log(f"Файл сохранения: {self.accounts_file}")
        
        # Создание файла аккаунтов
        if not os.path.exists(self.accounts_file):
            with open(self.accounts_file, "w", encoding="utf-8") as f:
                f.write("# Roblox Accounts (username:password)\n")
        
        # Основной цикл создания аккаунтов
        while self.accounts_created < self.max_accounts:
            try:
                self.log(f"\n--- Аккаунт {self.accounts_created + 1}/{self.max_accounts} ---")
                
                # Очистка кеша перед созданием нового аккаунта
                if self.accounts_created > 0:
                    self.clear_app_cache()
                
                # Запуск Roblox
                if not self.start_roblox():
                    self.log("Не удалось запустить Roblox, пропускаем...")
                    continue
                
                # Создание аккаунта
                if self.create_account():
                    self.accounts_created += 1
                    self.log(f"✓ Успешно создано аккаунтов: {self.accounts_created}")
                else:
                    self.log("✗ Не удалось создать аккаунт")
                
                # Пауза между созданием аккаунтов
                if self.accounts_created < self.max_accounts:
                    self.log("Пауза перед следующим аккаунтом...")
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                self.log("\n⚠️  Программа остановлена пользователем")
                break
            except Exception as e:
                self.log(f"Неожиданная ошибка: {e}")
                continue
        
        # Финальная очистка
        self.clear_app_cache()
        
        self.log("\n" + "=" * 50)
        self.log(f"Программа завершена!")
        self.log(f"Создано аккаунтов: {self.accounts_created}")
        self.log(f"Аккаунты сохранены в: {self.accounts_file}")
        self.log("=" * 50)

def main():
    """Точка входа"""
    generator = RobloxTermuxGenerator()
    generator.run()

if __name__ == "__main__":
    main()
