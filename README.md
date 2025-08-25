# Lingua Master - Aplikacja do nauki języków

Aplikacja Streamlit do tłumaczenia, korekty i stylizacji tekstów w różnych językach z wykorzystaniem AI.

## 🚀 Uruchomienie lokalne

### 1. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 2. Konfiguracja zmiennych środowiskowych

Utwórz plik `.env` w głównym katalogu projektu:

```env
# Konfiguracja Qdrant
QDRANT_URL=https://your-qdrant-instance.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION=lingua_master_history

# OpenAI API Key (opcjonalne - można też wprowadzić w aplikacji)
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Uruchomienie aplikacji

```bash
streamlit run app.py
```

## ☁️ Uruchomienie na Streamlit Cloud

### 1. Wypchnij kod do repozytorium GitHub

### 2. Skonfiguruj sekrety w Streamlit Cloud:

Przejdź do ustawień aplikacji w Streamlit Cloud i dodaj następujące sekrety:

- `QDRANT_URL` - URL do Twojej instancji Qdrant
- `QDRANT_API_KEY` - Klucz API do Qdrant
- `QDRANT_COLLECTION` - Nazwa kolekcji (opcjonalne, domyślnie: `lingua_master_history`)
- `OPENAI_API_KEY` - Klucz API OpenAI (opcjonalne)

### 3. Aplikacja automatycznie się wdroży

## 🔧 Wymagania

- Python 3.8+
- Konto Qdrant Cloud lub lokalna instancja Qdrant
- Klucz API OpenAI

## 📋 Funkcje

- **Tłumaczenie** - tłumaczenie tekstów z polskiego na inne języki
- **Korekta** - poprawianie błędów gramatycznych w tekstach obcojęzycznych
- **Stylizacja** - poprawianie i ulepszanie stylu tekstów
- **Audio** - odtwarzanie tekstów w formie audio
- **Wyjaśnienia** - szczegółowe wyjaśnienia słówek i gramatyki
- **Historia** - zapisywanie i wyszukiwanie w historii tłumaczeń

## 🛠️ Rozwiązywanie problemów

### Błąd "No secrets found"

Aplikacja automatycznie wykrywa środowisko uruchomienia i używa odpowiednich źródeł konfiguracji:

- **Lokalnie**: sprawdza plik `.env` i zmienne środowiskowe systemu
- **Streamlit Cloud**: używa sekretów z ustawień aplikacji

### Błąd połączenia z Qdrant

Sprawdź czy:

- URL Qdrant jest poprawny
- Klucz API jest prawidłowy
- Instancja Qdrant jest dostępna
