import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import re
import matplotlib.pyplot as plt


# Функція для завантаження тексту з URL
def fetch_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching the text from {url}: {e}")
        return None


# Mapper: розбиває текст на слова
def map_words(text_chunk):
    words = re.findall(r'\b\w+\b', text_chunk.lower())  # Розбиваємо на слова, ігноруючи регістр
    return Counter(words)


# Reducer: об'єднує частоти слів
def reduce_counters(counter1, counter2):
    counter1.update(counter2)
    return counter1


# Візуалізація топ-слів
def visualize_top_words(word_counts, top_n=10):
    top_words = word_counts.most_common(top_n)
    words, counts = zip(*top_words)
    
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.title(f'Топ {top_n} слів за частотою використання')
    plt.xlabel('Слова')
    plt.ylabel('Частота')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def analyze_words(url, num_threads=4, top_n=10):
    text = fetch_text(url)
    if not text:
        print("Помилка: Не вдалося отримати вхідний текст.")
        return
    
    # Розділяємо текст на частини для багатопотокової обробки
    chunk_size = max(len(text) // num_threads, 1)  # Перевірка на мінімальний розмір частини
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    # Використання багатопотоковості
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        counters = list(executor.map(map_words, chunks))
    
    # Застосовуємо Reducer
    total_word_count = Counter()
    for counter in counters:
        total_word_count = reduce_counters(total_word_count, counter)
    
    # Візуалізуємо топ-слова
    visualize_top_words(total_word_count, top_n)


if __name__ == "__main__":
    url = "https://www.gutenberg.org/files/1342/1342-0.txt"  
    analyze_words(url, num_threads=4, top_n=10)
