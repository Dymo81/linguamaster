import io
import streamlit as st
from openai import OpenAI
from dotenv import dotenv_values
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue, PayloadSchemaType
import uuid
import datetime

env = dotenv_values(".env")
# client = OpenAI(api_key=env["OPENAI_API_KEY"])

# Połączenie z Qdrant
qdrant = QdrantClient(
    url=env["QDRANT_URL"],
    api_key=env["QDRANT_API_KEY"]
)

COLLECTION_NAME = env["QDRANT_COLLECTION"]

def get_openai_client():
    return OpenAI(api_key=st.session_state["openai_api_key"])

# Funkcja tłumacząca tekst
def translate_text(text, target_language):
    prompt = f"Tłumacz poniższy tekst z języka polskiego na {target_language}:\n\n{text}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Jesteś nauczycielem języków obcych z 10 letnim doświadczeniem. Tłumacz jasno i naturalnie."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

# Funkcja sprawdzająca w jakim języku jest napisany tekst
def is_polish(text: str) -> bool:
    prompt = f"Na podstawie poniższego tekstu powiedz tylko 'tak' jeśli jest po polsku, a 'nie' jeśli jest w innym języku. Tekst: {text}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Jesteś nauczycielem języków obcych. Odpowiadaj tylko: 'tak' lub 'nie'."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3,  # wystarczy
        temperature=0
    )

    answer = response.choices[0].message.content.strip().lower()
    return answer == "tak"

# Funkcja poprawiająca tekst pod względem gramatycznym
def correct_foreign_text(text: str) -> str:
    prompt = f"Na podstawie podanego tekstu, wciel się w rolę eksperta językowego i popraw ten tekst zgodnie z zasadami gramatycznymi obowiązującymi w tym języku. Tekst: {text}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Jesteś ekspertem językowym. Zwracaj tylko poprawioną wersję zdania."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=60,
        temperature=0
    )

    return response.choices[0].message.content.strip()

# Funkcja poprawiająca tekst stylistycznie 
def beautify_text(text: str) -> str:
    prompt = f"Na podstawie podanego tekstu w języku obcym wciel się w native speakera z 15-letnim doświadczeniem i cenionego na rynku. Sprawdź, czy podany tekst jest poprawny gramatycznie, rozbuduj zdanie tak, aby brzmiało ono naturalnie jak w codziennym życiu. Tekst: {text}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Jesteś native speakerem języka obcego z doświadczeniem w nauczaniu i edycji językowej. Zwróć tylko poprawioną i naturalnie brzmiącą wersję tekstu."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=80,
        temperature=0.7  # pozwólmy na trochę więcej swobody stylu
    )

    return response.choices[0].message.content.strip()

# Funkcja wyjaśniająca trudne słowa i konstrukcje gramatyczne 
def explain_text(text: str) -> str:
    prompt = f"""
    Na podstawie poniższego tekstu wypisz trudne słowa oraz konstrukcje gramatyczne, które występują w tekście.
    Podziel słowa ze względu na stopień trudności języka, np: A1, A2, B1 itd.
    Pokaż znaczenie tych słów w kontekście ich codziennego użytkowania.
    Jeżeli chodzi o gramatykę - wytłumacz ją w jak najprostszy sposób, nie komplikuj sprawy.
    Użyj prostego języka, tak jakbyś tłumaczył 12-latkowi. Dodaj podobne przykłady.

    Tekst: {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Jesteś świetnym nauczycielem języków, który tłumaczy wszystko prosto i skutecznie. Twoim uczniem jest 12-latek."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.4
    )

    return response.choices[0].message.content.strip()

def listening_text(text: str) -> io.BytesIO:
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )

    audio_bytes = io.BytesIO(response.content)
    return audio_bytes

# Funkcja do zapisu punktu do Qdrant
def save_history_to_qdrant(original_text, processed_text, language, mode):
    # Tworzenie embeddingu z OpenAI
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=processed_text
    ).data[0].embedding

    # Dane do zapisania
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "original_text": original_text,
            "processed_text": processed_text,
            "language": language,
            "mode": mode,
            "timestamp": str(datetime.datetime.now())
        }
    )

    qdrant.upsert(collection_name=COLLECTION_NAME, points=[point])


#
# MAIN
#
st.title('Lingua Master')

# OpenAI API key protection
if not st.session_state.get("openai_api_key"):
    if "OPENAI_API_KEY" in env:
        st.session_state["openai_api_key"] = env["OPENAI_API_KEY"]

    else:
        st.info("Dodaj swój klucz API OpenAI aby móc korzystać z tej aplikacji")
        st.session_state["openai_api_key"] = st.text_input("Klucz API", type="password")
        if st.session_state["openai_api_key"]:
            st.rerun()

if not st.session_state.get("openai_api_key"):
    st.stop()

# Usuwanie kolekcji - testowanie nowych rozwiazań
# if st.sidebar.button("🗑️ Usuń kolekcję i utwórz od nowa"):
#     qdrant.delete_collection(collection_name=COLLECTION_NAME)
#     st.sidebar.success("Kolekcja została usunięta. Uruchom ponownie aplikację.")

# Inicjalizacja kolekcji (jeśli nie istnieje)
if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
    # Tworzymy nową kolekcję z embeddingiem (1536 dla text-embedding-3-small)
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        on_disk_payload=True
    )

    # Dodajemy indeks dla pola 'mode' (filtr po trybie: Tłumaczenie / Korekta / Stylizacja)
    qdrant.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="mode",
        field_schema=PayloadSchemaType.KEYWORD
    )
git
st.header("📘 Tłumaczenie z języka polskiego")
text_polish = st.text_area("Wpisz tekst po polsku", key="text_polish")

st.header("🌍 Korekta lub stylizacja tekstu w języku obcym")
text_foreign = st.text_area("Wpisz tekst w języku obcym", key="text_foreign")

mode = st.radio(
    "Jak chcesz przetworzyć tekst w języku obcym?",
    ["Popraw tylko błędy", "Popraw i wygładź styl"]
)

LANGUAGE_MAP = {
    "angielski": "English",
    "hiszpański": "Spanish",
    "francuski": "French",
    "niemiecki": "German",
    "włoski": "Italian"
}

language_pl = st.selectbox(
    "Wybierz język docelowy",
    list(LANGUAGE_MAP.keys())
)

language_en = LANGUAGE_MAP[language_pl]

if st.button("Tłumacz"):
    if text_polish:
        translated_text = translate_text(text_polish, language_en)
        st.success("✅ Tłumaczenie:")
        st.markdown(translated_text)

        # AUDIO
        audio_file = listening_text(translated_text)
        st.audio(audio_file, format="audio/mp3")

        # WYJAŚNIENIE (w ekspanderze)
        with st.expander("🔍 Wyjaśnienie słówek i gramatyki", expanded=False):
            explanation = explain_text(translated_text)
            st.markdown(explanation)

        # HISTORIA
        save_history_to_qdrant(
            original_text=text_polish,
            processed_text=translated_text,
            language=language_en,
            mode="Tłumaczenie"
        )
    else:
        st.warning("Wpisz tekst do przetłumaczenia.")

# Przyciski obok siebie? Można rozważyć w przyszłości.

if st.button("Popraw / Stylizuj"):
    if text_foreign:
        if mode == "Popraw tylko błędy":
            corrected_text = correct_foreign_text(text_foreign)
            process_mode = "Korekta"
        else:
            corrected_text = beautify_text(text_foreign)
            process_mode = "Stylizacja"

        st.success("✅ Wynik:")
        st.markdown(corrected_text)

        # AUDIO
        audio_file = listening_text(corrected_text)
        st.audio(audio_file, format="audio/mp3")

        # WYJAŚNIENIE (w ekspanderze)
        with st.expander("🔍 Wyjaśnienie słówek i gramatyki", expanded=False):
            explanation = explain_text(corrected_text)
            st.markdown(explanation)

        # HISTORIA
        save_history_to_qdrant(
            original_text=text_foreign,
            processed_text=corrected_text,
            language="Detected",  # opcjonalnie można wykrywać język
            mode=process_mode
        )
    else:
        st.warning("Wpisz tekst do poprawy lub stylizacji.")

# Wyszukiwanie i filtrowanie
with st.expander("📜 Historia Twoich tłumaczeń i poprawek", expanded=False):
    filter_mode = st.selectbox(
        "Filtruj historię według trybu:",
        ["Wszystko", "Tłumaczenie", "Korekta", "Stylizacja"]
    )

    # Budowanie filtra
    must_conditions = []
    if filter_mode != "Wszystko":
        must_conditions.append(
            FieldCondition(
                key="mode",
                match=MatchValue(value=filter_mode)
            )
        )

    query_filter = Filter(must=must_conditions) if must_conditions else None

    # Pobranie historii
    points, _ = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        limit=50,
        with_payload=True,
        scroll_filter=query_filter
    )

    if points:
        for point in reversed(list(points)):
            p = point.payload
            st.markdown(f"""
**🕒 {p['timestamp']}**  
- **Tryb**: `{p['mode']}`  
- **Język**: `{p['language']}`  
- **Oryginał**: {p['original_text']}  
- **Rezultat**: {p['processed_text']}  
---""")
    else:
        st.info("Brak zapisanej historii.")