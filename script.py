import os
import re
from urllib.parse import unquote, quote

def clean_and_rename():
    print("Универсальный конфигуратор vless-серверов (Полная очистка имен)")
    
    # Запрос путь к файлу
    input_path = input("Введите имя файла или полный путь к нему (например, D:\VPN Key\тест.txt): ").strip()
    input_path = input_path.strip("'\"") 
    
    if not os.path.exists(input_path):
        print(f"❌ Ошибка: Файл по пути '{input_path}' не найден!")
        return

    # Запрашиваем имя бренда
    brand_name = input("Введите название бренда (например, QuorVPN): ").strip()
    if not brand_name:
        brand_name = "VSP x QUOR"

    dir_name = os.path.dirname(input_path)
    file_name = os.path.basename(input_path)
    name_part, ext_part = os.path.splitext(file_name)
    output_path = os.path.join(dir_name, f"{name_part}_renamed{ext_part}")

    # Ключевые слова для определения LTE
    lte_keywords = ['обход', 'глушилки', 'lte', 'антиобход']

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(input_path, 'r', encoding='cp1251') as f:
            lines = f.readlines()

    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if 'vless://' in line and '#' in line:
            base_url, tag = line.split('#', 1)
            
            # Декадир тэгов
            tag = unquote(tag.replace('+', ' '))
            
            # Определить тип подписки
            tag_lower = tag.lower()
            if any(word in tag_lower for word in lte_keywords):
                connection_type = 'LTE'
            else:
                connection_type = 'WiFi'
                
            # Извлекаем флаг страны
            flag_match = re.search(r'([\U0001F1E6-\U0001F1FF]{2})', tag)
            flag = flag_match.group(1) if flag_match else ""
            
            # очистка имени
            # игнор тех слов
            words = re.findall(r'[А-Яа-яA-Za-z\-]+', tag)
            
            country_name = ""
            ignore_words = {'обход', 'глушилки', 'lte', 'антиобход', 'основной', 'сервер', 'server', 'vspboost', 'quorvpn', 'quor'}
            
            for word in words:
                if word.lower() not in ignore_words and len(word) > 2:
                    country_name = word
                    break
            
            # если пусто, пишем Server
            if not country_name:
                country_name = "Server"
            
            # Капс первой буквы страны
            country_name = country_name.capitalize()

            # Специальный фикс для Нидерландов/Белых списков (если определилось "Белые")
            if "Бел" in country_name and "🇳🇱" in flag:
                country_name = "Нидерланды"

            # собирается тег
            if flag:
                new_tag = f"{flag} {country_name} · {brand_name} · {connection_type}"
            else:
                new_tag = f"{country_name} · {brand_name} · {connection_type}"
                
            new_tag = re.sub(r'\s+', ' ', new_tag).strip()

            # кодировка обратно в VLESS
            encoded_tag = quote(new_tag)

            processed_lines.append(f"{base_url}#{encoded_tag}")
        else:
            processed_lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(processed_lines) + '\n')

    print("\n✅ Готово!")
    print(f"Обработано серверов: {len(processed_lines)}")
    print(f"Новый файл сохранен как: {output_path}\n")

if __name__ == "__main__":
    clean_and_rename()