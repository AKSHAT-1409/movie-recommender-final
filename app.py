import streamlit as st
import pickle
from altair.theme import names
import gzip
import time
import requests

# Load the movie data
movies = pickle.load(open('movies.pkl', 'rb'))

# Load the compressed similarity matrix
with gzip.open('similarity_compressed.pkl.gz', 'rb') as f:
    similarity_list = pickle.load(f)

# TMDB poster fetch function with retry logic
def fetch_poster(movie_id, retries=3, delay=1):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=aba58951484b1b4cfc582b0e4cf5bf58&language=en-US"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
            else:
                return "https://via.placeholder.com/500x750?text=No+Image"
        except Exception as e:
            print(f"Poster fetch error (attempt {attempt + 1}):", e)
            time.sleep(delay)
    return "https://via.placeholder.com/500x750?text=No+Image"

# Movie recommendation logic
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity_list[movie_index]
    movies_li = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_li:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# Streamlit UI
st.title("🎬 Movie Recommender System")

# ✅ Top 25 Movies of All Time (Static Section)
st.subheader("🍿 Top 25 Movies of All Time")

top_25_titles = [
    "Inception", "The Dark Knight", "Avatar", "The Avengers", "Deadpool",
    "Interstellar", "Django Unchained", "Guardians of the Galaxy", "The Hunger Games",
    "Mad Max: Fury Road", "Fight Club", "The Dark Knight Rises", "The Matrix",
    "Iron Man 3", "Iron Man", "The Lord of the Rings: The Fellowship of the Ring",
    "Jurassic World", "Pulp Fiction", "The Hobbit: An Unexpected Journey",
    "The Shawshank Redemption", "The Lord of the Rings: The Return of the King",
    "Forrest Gump", "Skyfall", "Titanic", "The Lord of the Rings: The Two Towers"
]

cols = st.columns(5)
for idx, title in enumerate(top_25_titles):
    try:
        movie_row = movies[movies['title'] == title].iloc[0]
        poster_url = fetch_poster(movie_row['id'])
        with cols[idx % 5]:
            st.image(poster_url, caption=title, use_column_width=True)
    except:
        with cols[idx % 5]:
            st.warning("Poster not found")

# 🎯 Movie Recommender Section
movie_list = movies['title'].values
option = st.selectbox("Search for a movie to get recommendations", movie_list)

if st.button('Recommend'):
    names, posters = recommend(option)
    st.subheader("Recommended Movies:")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])
