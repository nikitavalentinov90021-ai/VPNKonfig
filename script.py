import os
import re
from urllib.parse import unquote, quote
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Настройки темы оформления
ctk.set_appearance_mode("System")  # Авто-выбор (светлая/темная в зависимости от Windows)
ctk.set_default_color_theme("blue") # Синяя цветовая схема

class VlessConfiguratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка главного окна
        self.title("QuorVPN · Конфигуратор VLESS")
        self.geometry("600x500")
        self.resizable(False, False)

        # Переменная для хранения пути к файлу
        self.file_path = ""

        #  Заголовок 
        self.title_label = ctk.CTkLabel(self, text="Универсальный конфигуратор VLESS", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=20)

        #  Блок выбора файла 
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, padx=20, fill="x")

        self.file_entry = ctk.CTkEntry(self.file_frame, placeholder_text="Выберите файл с серверами...", width=380)
        self.file_entry.pack(side="left", padx=(10, 5), pady=10)

        self.file_btn = ctk.CTkButton(self.file_frame, text="Обзор", width=100, command=self.browse_file)
        self.file_btn.pack(side="right", padx=(5, 10), pady=10)

        # --- Блок ввода бренда ---
        self.brand_frame = ctk.CTkFrame(self)
        self.brand_frame.pack(pady=10, padx=20, fill="x")

        self.brand_label = ctk.CTkLabel(self.brand_frame, text="Название для серверов:", font=ctk.CTkFont(size=14))
        self.brand_label.pack(side="left", padx=10, pady=10)

        self.brand_entry = ctk.CTkEntry(self.brand_frame, placeholder_text="Например: QuorVPN", width=250)
        self.brand_entry.insert(0, "QuorVPN") # Дефолтное значение
        self.brand_entry.pack(side="right", padx=10, pady=10)

        # --- Консоль / Вывод логов ---
        self.log_textbox = ctk.CTkTextbox(self, width=560, height=180, font=ctk.CTkFont(family="Courier", size=12))
        self.log_textbox.pack(pady=15, padx=20)
        self.log_textbox.insert("0.0", "Система готова к работе.\nВыберите файл и нажмите 'Запустить очистку'...")
        self.log_textbox.configure(state="disabled") # Запрещаем редактирование пользователем

        # --- Кнопка Сторта ---
        self.start_btn = ctk.CTkButton(self, text="Запустить очистку", font=ctk.CTkFont(size=16, weight="bold"), height=40, command=self.process_config)
        self.start_btn.pack(pady=10)

    def log(self, text):
        """Вспомогательная функция для вывода логов в текстовое поле"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"\n{text}")
        self.log_textbox.see("end") # Скролл вниз
        self.log_textbox.configure(state="disabled")

    def clear_log(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    def browse_file(self):
        """Открытие диалогового окна для выбора файла"""
        file_selected = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_selected:
            self.file_path = file_selected
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, file_selected)

    def process_config(self):
        """Основная логика твоего скрипта, адаптированная под GUI"""
        input_path = self.file_entry.get().strip().strip("'\"")
        brand_name = self.brand_entry.get().strip()
        
        if not brand_name:
            brand_name = "VSP x QUOR"

        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Ошибка", f"Файл по пути '{input_path}' не найден!")
            return

        self.clear_log()
        self.log("=== Начало обработки ===")

        dir_name = os.path.dirname(input_path)
        file_name = os.path.basename(input_path)
        name_part, ext_part = os.path.splitext(file_name)
        output_path = os.path.join(dir_name, f"{name_part}_renamed{ext_part}")

        lte_keywords = ['обход', 'глушилки', 'lte', 'антиобход', 'БС', 'Белые', 'Списки']

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(input_path, 'r', encoding='cp1251') as f:
                    lines = f.readlines()
            except Exception as e:
                self.log(f"❌ Ошибка кодировки: {str(e)}")
                return

        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'vless://' in line and '#' in line:
                base_url, tag = line.split('#', 1)
                tag = unquote(tag.replace('+', ' '))
                
                tag_lower = tag.lower()
                if any(word in tag_lower for word in lte_keywords):
                    connection_type = 'LTE'
                else:
                    connection_type = 'WiFi'
                    
                flag_match = re.search(r'([\U0001F1E6-\U0001F1FF]{2})', tag)
                flag = flag_match.group(1) if flag_match else ""
                
                words = re.findall(r'[А-Яа-яA-Za-z\-]+', tag)
                country_name = ""
                ignore_words = {'обход', 'глушилки', 'lte', 'антиобход', 'основной', 'сервер', 'server', 'обходняк', 'глушат'}
                
                for word in words:
                    if word.lower() not in ignore_words and len(word) > 2:
                        country_name = word
                        break
                
                if not country_name:
                    country_name = "Server"
                
                country_name = country_name.capitalize()

                if "Бел" in country_name and "🇳🇱" in flag:
                    country_name = "Нидерланды"

                if flag:
                    new_tag = f"{flag} {country_name} · {brand_name} · {connection_type}"
                else:
                    new_tag = f"{country_name} · {brand_name} · {connection_type}"
                    
                new_tag = re.sub(r'\s+', ' ', new_tag).strip()
                encoded_tag = quote(new_tag)
                processed_lines.append(f"{base_url}#{encoded_tag}")
            else:
                processed_lines.append(line)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(processed_lines) + '\n')
            
            self.log("✅ Успешно завершено!")
            self.log(f"Обработано серверов: {len(processed_lines)}")
            self.log(f"Файл сохранен: {output_path}")
            
            messagebox.showinfo("Успех", f"Файл успешно сохранен!\nОбработано серверов: {len(processed_lines)}")
        except Exception as e:
            self.log(f"❌ Ошибка записи файла: {str(e)}")

if __name__ == "__main__":
    app = VlessConfiguratorApp()
    app.mainloop()
