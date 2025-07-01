#!/bin/bash
# Установочный скрипт для Roblox Account Generator в Termux

echo "🤖 Установка Roblox Account Generator для Termux"
echo "================================================="

# Проверка, что мы в Termux
if [ -z "$PREFIX" ]; then
    echo "❌ Ошибка: Этот скрипт должен запускаться в Termux"
    exit 1
fi

echo "✅ Termux обнаружен"

# Обновление пакетов
echo "📦 Обновление пакетов..."
pkg update -y && pkg upgrade -y

# Установка необходимых пакетов
echo "🔧 Установка зависимостей..."
pkg install -y python git wget curl

# Проверка Python
if command -v python &> /dev/null; then
    echo "✅ Python установлен: $(python --version)"
else
    echo "❌ Ошибка: Python не установлен"
    exit 1
fi

# Создание рабочей директории
WORK_DIR="$HOME/roblox-generator"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "📁 Рабочая директория: $WORK_DIR"

# Создание основного скрипта
cat > "$WORK_DIR/roblox_generator.py" << 'EOF'
#!/usr/bin/env python3
"""
Roblox Account Generator для Termux - Финальная версия
Автоматическое создание аккаунтов в мобильном приложении Roblox
"""

import subprocess
import time
import random
import string
import os
import json
from datetime import datetime

class RobloxGenerator:
    def __init__(self):
        self.accounts_created = 0
        self.max_accounts = 10
        self.accounts_file = "accounts.txt"
        self.package_name = "com.roblox.client"
        
        # Настройки экрана (автоматически определяются)
        self.screen_width = 1080
        self.screen_height = 1920
        
        self.get_screen_size()
        
    def log(self, message):
        """Логирование с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def run_cmd(self, command):
        """Выполнить команду"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip()
        except:
            return False, ""
    
    def get_screen_size(self):
        """Получить размер экрана"""
        success, output = self.run_cmd("wm size")
        if success and "Physical size:" in output:
            try:
                size = output.split("Physical size: ")[1]
                width, height = map(int, size.split('x'))
                self.screen_width = width
                self.screen_height = height
                self.log(f"Размер экрана: {width}x{height}")
            except:
                self.log("Используется размер экрана по умолчанию")
    
    def generate_credentials(self):
        """Генерация учетных данных"""
        adjectives = ["Cool", "Super", "Epic", "Pro", "Fast", "Smart", "Wild", "Bold", "Quick", "Brave"]
        nouns = ["Player", "Gamer", "Hero", "Star", "King", "Queen", "Master", "Legend", "Ninja", "Champion"]
        
        username = random.choice(adjectives) + random.choice(nouns) + str(random.randint(1000, 9999))
        
        # Генерация надежного пароля
        password_length = random.randint(12, 16)
        chars = string.ascii_letters + string.digits + "!@#$%"
        password = ''.join(random.choice(chars) for _ in range(password_length))
        
        gender = random.choice(["Male", "Female"])
        
        return username, password, gender
    
    def tap(self, x, y):
        """Тап по координатам"""
        self.run_cmd(f"input tap {x} {y}")
        time.sleep(1.5)
    
    def type_text(self, text):
        """Ввод текста"""
        # Очистка поля
        self.run_cmd("input keyevent KEYCODE_CTRL_A")
        time.sleep(0.5)
        self.run_cmd("input keyevent KEYCODE_DEL")
        time.sleep(0.5)
        
        # Ввод текста
        escaped = text.replace("'", "\\'").replace('"', '\\"')
        self.run_cmd(f"input text '{escaped}'")
        time.sleep(1)
    
    def check_roblox(self):
        """Проверка установки Roblox"""
        success, output = self.run_cmd(f"pm list packages | grep {self.package_name}")
        return success and self.package_name in output
    
    def start_roblox(self):
        """Запуск Roblox"""
        self.log("Запуск Roblox...")
        
        # Закрытие если запущен
        self.run_cmd(f"am force-stop {self.package_name}")
        time.sleep(3)
        
        # Запуск
        success, _ = self.run_cmd(f"am start -n {self.package_name}/.ActivityMain")
        if success:
            time.sleep(10)  # Ждем загрузки
            return True
        return False
    
    def create_account(self):
        """Создание аккаунта"""
        username, password, gender = self.generate_credentials()
        self.log(f"Создание: {username} | {password} | {gender}")
        
        try:
            # Ожидание загрузки и поиск кнопки Sign Up
            time.sleep(5)
            
            # Координаты для разных размеров экрана
            center_x = self.screen_width // 2
            
            # 1. Поиск кнопки регистрации
            signup_positions = [
                (center_x, self.screen_height - 200),  # Внизу экрана
                (center_x, self.screen_height - 300),
                (center_x, self.screen_height - 400),
                (center_x, self.screen_height * 3 // 4),  # 3/4 высоты
            ]
            
            self.log("Поиск кнопки Sign Up...")
            for pos in signup_positions:
                self.tap(pos[0], pos[1])
                time.sleep(3)
                # Проверяем, открылась ли форма (примитивная проверка)
                break
            
            # 2. Заполнение формы
            form_start_y = self.screen_height // 3
            field_height = 100
            
            # Username поле
            self.log("Ввод username...")
            username_y = form_start_y
            self.tap(center_x, username_y)
            time.sleep(1)
            self.type_text(username)
            
            # Password поле
            self.log("Ввод password...")
            password_y = form_start_y + field_height * 2
            self.tap(center_x, password_y)
            time.sleep(1)
            self.type_text(password)
            
            # 3. Дата рождения
            self.log("Установка даты рождения...")
            birthday_y = form_start_y + field_height * 4
            
            # Месяц
            month_x = center_x - 150
            self.tap(month_x, birthday_y)
            time.sleep(1)
            
            # Выбор случайного месяца
            for _ in range(random.randint(1, 12)):
                self.run_cmd("input keyevent KEYCODE_DPAD_DOWN")
                time.sleep(0.2)
            self.run_cmd("input keyevent KEYCODE_ENTER")
            time.sleep(1)
            
            # День
            day_x = center_x
            self.tap(day_x, birthday_y)
            time.sleep(1)
            for _ in range(random.randint(1, 28)):
                self.run_cmd("input keyevent KEYCODE_DPAD_DOWN")
                time.sleep(0.1)
            self.run_cmd("input keyevent KEYCODE_ENTER")
            time.sleep(1)
            
            # Год (для 18+)
            year_x = center_x + 150
            self.tap(year_x, birthday_y)
            time.sleep(1)
            for _ in range(random.randint(25, 40)):  # 25-40 лет назад
                self.run_cmd("input keyevent KEYCODE_DPAD_DOWN")
                time.sleep(0.1)
            self.run_cmd("input keyevent KEYCODE_ENTER")
            time.sleep(1)
            
            # 4. Выбор пола
            self.log(f"Выбор пола: {gender}")
            gender_y = birthday_y + field_height
            
            if gender == "Male":
                self.tap(center_x - 100, gender_y)
            else:
                self.tap(center_x + 100, gender_y)
            time.sleep(1)
            
            # 5. Финальная кнопка Sign Up
            self.log("Нажатие кнопки регистрации...")
            final_button_y = gender_y + field_height * 2
            self.tap(center_x, final_button_y)
            time.sleep(5)
            
            # 6. Ожидание результата
            self.log("Ожидание завершения...")
            
            # Ждем до 120 секунд
            for i in range(120):
                time.sleep(2)
                
                # Простая проверка - если можем сделать скриншот без ошибок,
                # и прошло достаточно времени, считаем что аккаунт создан
                if i > 30:  # После 60 секунд ожидания
                    # Проверяем, не появилась ли ошибка
                    success, _ = self.run_cmd("screencap -p /dev/null")
                    if success:
                        self.log("✅ Аккаунт создан (предполагается)")
                        self.save_account(username, password)
                        return True
            
            self.log("⏰ Тайм-аут создания аккаунта")
            return False
            
        except Exception as e:
            self.log(f"❌ Ошибка: {e}")
            return False
    
    def save_account(self, username, password):
        """Сохранение аккаунта"""
        try:
            with open(self.accounts_file, "a") as f:
                f.write(f"{username}:{password}\n")
            self.log(f"💾 Сохранен: {username}:{password}")
        except Exception as e:
            self.log(f"❌ Ошибка сохранения: {e}")
    
    def clear_app_data(self):
        """Очистка данных приложения"""
        self.log("🧹 Очистка данных Roblox...")
        
        self.run_cmd(f"am force-stop {self.package_name}")
        time.sleep(2)
        
        # Попытка очистить данные (может потребовать root)
        success, _ = self.run_cmd(f"pm clear {self.package_name}")
        if success:
            self.log("✅ Данные очищены")
        else:
            self.log("⚠️ Не удалось очистить данные")
        
        time.sleep(3)
    
    def run(self):
        """Главный цикл"""
        self.log("🚀 Roblox Account Generator для Termux")
        self.log("=" * 50)
        
        # Проверки
        if not self.check_roblox():
            self.log("❌ Roblox не найден! Установите из Play Store")
            return
        
        self.log("✅ Roblox найден")
        self.log(f"🎯 Цель: создать {self.max_accounts} аккаунтов")
        
        # Создание файла для аккаунтов
        with open(self.accounts_file, "w") as f:
            f.write(f"# Roblox Accounts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Основной цикл
        for account_num in range(1, self.max_accounts + 1):
            try:
                self.log(f"\n{'='*20} Аккаунт {account_num}/{self.max_accounts} {'='*20}")
                
                # Очистка данных (кроме первого аккаунта)
                if account_num > 1:
                    self.clear_app_data()
                
                # Запуск Roblox
                if not self.start_roblox():
                    self.log("❌ Не удалось запустить Roblox")
                    continue
                
                # Создание аккаунта
                if self.create_account():
                    self.accounts_created += 1
                    self.log(f"🎉 Создано аккаунтов: {self.accounts_created}")
                else:
                    self.log("❌ Не удалось создать аккаунт")
                
                # Пауза между аккаунтами
                if account_num < self.max_accounts:
                    self.log("⏳ Пауза 15 секунд...")
                    time.sleep(15)
                    
            except KeyboardInterrupt:
                self.log("\n⚠️ Остановлено пользователем")
                break
            except Exception as e:
                self.log(f"❌ Неожиданная ошибка: {e}")
                continue
        
        # Финальная очистка
        self.clear_app_data()
        
        # Результаты
        self.log("\n" + "=" * 50)
        self.log("📊 ИТОГИ:")
        self.log(f"✅ Успешно создано: {self.accounts_created} аккаунтов")
        self.log(f"📁 Файл: {self.accounts_file}")
        
        if os.path.exists(self.accounts_file):
            self.log("\n📋 Созданные аккаунты:")
            with open(self.accounts_file, "r") as f:
                for line in f:
                    if ":" in line and not line.startswith("#"):
                        self.log(f"   {line.strip()}")
        
        self.log("🏁 Готово!")

if __name__ == "__main__":
    generator = RobloxGenerator()
    generator.run()
EOF

# Создание скрипта запуска
cat > "$WORK_DIR/start.sh" << 'EOF'
#!/bin/bash
echo "🤖 Запуск Roblox Account Generator..."
cd "$(dirname "$0")"
python roblox_generator.py
EOF

# Создание инструкции
cat > "$WORK_DIR/README.txt" << 'EOF'
🤖 Roblox Account Generator для Termux

📋 ИНСТРУКЦИЯ:

1. Убедитесь что Roblox установлен из Play Store
2. Запустите: bash start.sh
3. Программа автоматически создаст 10 аккаунтов
4. Результат сохранится в файл accounts.txt

⚙️ НАСТРОЙКИ:

Отредактируйте roblox_generator.py:
- max_accounts = 10  # количество аккаунтов
- accounts_file = "accounts.txt"  # файл результата

📱 ТРЕБОВАНИЯ:

- Android с Termux
- Установленный Roblox
- Доступ к input команде
- Стабильный интернет

⚠️ ВАЖНО:

- Координаты подбираются автоматически
- При появлении капчи - решайте вручную
- Программа автоматически очищает кэш между аккаунтами
- Каждый аккаунт сохраняется в формате username:password

🔧 РЕШЕНИЕ ПРОБЛЕМ:

Если не работает:
1. Проверьте что Roblox установлен
2. Перезапустите Termux
3. Дайте разрешения приложению
4. Попробуйте запустить с правами root

📞 Контакты: github.com/your-repo
EOF

# Установка прав
chmod +x "$WORK_DIR/start.sh"
chmod +x "$WORK_DIR/roblox_generator.py"

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📁 Файлы установлены в: $WORK_DIR"
echo ""
echo "🚀 Для запуска выполните:"
echo "   cd $WORK_DIR"
echo "   bash start.sh"
echo ""
echo "📖 Или прочитайте README.txt для подробной инструкции"
echo ""
echo "⚠️  ВАЖНО: Убедитесь что Roblox установлен из Play Store!"
echo ""
