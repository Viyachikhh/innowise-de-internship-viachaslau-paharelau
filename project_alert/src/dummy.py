import os

def dummy_creds_example():
    url = os.getenv('TARGET_URL', 'default_url')
    api_key = os.getenv('API_KEY')
    
    if not api_key:
        print("Ошибка: API_KEY не найден!")
    else:
        print(f"Подключаюсь к {url} используя ключ {api_key[:3]}***")

