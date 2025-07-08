import streamlit as st
import pickle
import requests
import gzip
import time

# Load movie data
movies = pickle.load(open('movies.pkl', 'rb'))

# Load similarity matrix
with gzip.open('similarity_compressed.pkl.gz', 'rb') as f:
    similarity_list = pickle.load(f)

# OMDB API key
OMDB_API_KEY = "f7472f22"

# TMDB poster fetch
def fetch_poster(movie_id, retries=3, delay=1):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=aba58951484b1b4cfc582b0e4cf5bf58&language=en-US"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
        except:
            time.sleep(delay)
    return "https://via.placeholder.com/500x750?text=No+Image"

# OMDB description and ratings
def fetch_movie_info(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        return {
            "plot": data.get("Plot", "No description available."),
            "imdb": data.get("imdbRating", "N/A"),
            "rt": next((r['Value'] for r in data.get("Ratings", []) if r["Source"] == "Rotten Tomatoes"), "N/A")
        }
    except:
        return {"plot": "Error fetching info.", "imdb": "N/A", "rt": "N/A"}

# Recommendation logic
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity_list[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    rec_names = []
    rec_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].id
        rec_names.append(movies.iloc[i[0]].title)
        rec_posters.append(fetch_poster(movie_id))
    return rec_names, rec_posters

# --- Streamlit App ---
st.set_page_config(layout="wide")
st.title("🎬 Movie Recommender System")

# Section: Search and Recommend
movie_list = movies['title'].values
selected_movie = st.selectbox("🔍 Search and get recommendations", movie_list)

if st.button('Recommend'):
    names, posters = recommend(selected_movie)
    st.subheader("📽️ Recommended Movies:")
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.caption(names[i])

# --- Static Top 25 Section ---
st.markdown("---")
st.subheader("🏆 Top 25 Movies of All Time")

top_25_titles = [
    "Inception", "The Dark Knight", "Avatar", "The Avengers", "Deadpool",
    "Interstellar", "Django Unchained", "Guardians of the Galaxy", "The Hunger Games",
    "Mad Max: Fury Road", "Fight Club", "The Dark Knight Rises", "The Matrix",
    "Iron Man 3", "Iron Man", "The Lord of the Rings: The Fellowship of the Ring",
    "Jurassic World", "Pulp Fiction", "The Hobbit: An Unexpected Journey",
    "The Shawshank Redemption", "The Lord of the Rings: The Return of the King",
    "Forrest Gump", "Skyfall", "Titanic", "The Lord of the Rings: The Two Towers"
]

cols_top = st.columns(5)
for idx, title in enumerate(top_25_titles):
    try:
        movie_row = movies[movies['title'] == title].iloc[0]
        poster_url = fetch_poster(movie_row['id'])
        with cols_top[idx % 5]:
            st.image(poster_url, caption=title, use_container_width=True)
    except:
        with cols_top[idx % 5]:
            st.warning("Poster not found")

# --- Explore All Movies ---
st.markdown("---")
st.subheader("🎞️ Explore All Movies")

search_query = st.text_input("🔎 Type to search movies below").lower()

filtered_movies = movies[movies['title'].str.lower().str.contains(search_query)]
cols_all = st.columns(5)
selected_movie_for_info = None

for idx, row in filtered_movies.iterrows():
    col = cols_all[idx % 5]
    with col:
        if st.button(row['title']):
            selected_movie_for_info = row
        st.image(fetch_poster(row['id']), use_container_width=True)

# --- Movie Detail View ---
if selected_movie_for_info is not None:
    movie_title = selected_movie_for_info['title']
    movie_id = selected_movie_for_info['id']
    movie_info = fetch_movie_info(movie_title)
    poster_url = fetch_poster(movie_id)

    st.markdown("---")
    st.subheader(f"🎬 {movie_title}")
    left, right = st.columns([1, 2])
    with left:
        st.image(poster_url, width=300)
    with right:
        st.markdown(f"**📝 Description:** {movie_info['plot']}")
        st.markdown(f"**⭐ IMDb Rating:** {movie_info['imdb']}")
        st.markdown(f"**🍅 Rotten Tomatoes:** {movie_info['rt']}")
