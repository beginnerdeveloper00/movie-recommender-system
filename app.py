import streamlit as st
import pickle
import requests

# -----------------------------
# load data
# -----------------------------
movies = pickle.load(open('movies.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

# -----------------------------
# session state
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "favorites" not in st.session_state:
    st.session_state.favorites = []

# -----------------------------
# CSS (Netflix style UI)
# -----------------------------
st.markdown("""
<style>
.movie-card {
    background-color: #111;
    padding: 10px;
    border-radius: 12px;
    text-align: center;
    transition: transform 0.3s;
}
.movie-card:hover {
    transform: scale(1.05);
}
.movie-title {
    font-size: 14px;
    font-weight: bold;
    color: white;
}
.movie-rating {
    color: gold;
}
.movie-overview {
    font-size: 12px;
    color: #ccc;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGIN
# -----------------------------
def login():
    st.markdown("<h2 style='text-align:center;'>🔐 Login</h2>", unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
        else:
            st.error("Invalid Credentials ❌")

# -----------------------------
# fetch movie details
# -----------------------------
def fetch_movie_details(movie_id):
    api_key = "87cfe779bd4d9bbdd4dd3250fade13cc"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    data = requests.get(url).json()

    poster = "https://image.tmdb.org/t/p/w500/" + data.get('poster_path') if data.get('poster_path') else ""
    rating = data.get('vote_average')
    overview = data.get('overview')

    return poster, rating, overview

# -----------------------------
# fetch trailer
# -----------------------------
def fetch_trailer(movie_id):
    api_key = "87cfe779bd4d9bbdd4dd3250fade13cc"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}"
    data = requests.get(url).json()

    for v in data.get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

# -----------------------------
# recommend function
# -----------------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]

    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    names, posters, ratings, overviews, trailers = [], [], [], [], []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id

        p, r, o = fetch_movie_details(movie_id)
        t = fetch_trailer(movie_id)

        names.append(movies.iloc[i[0]].title)
        posters.append(p)
        ratings.append(r)
        overviews.append(o)
        trailers.append(t)

    return names, posters, ratings, overviews, trailers

# -----------------------------
# MAIN FLOW
# -----------------------------
if not st.session_state.logged_in:
    login()
else:
    # 🔥 TITLE FIXED HERE
    st.markdown("<h1 style='text-align:center; color:red;'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)

    selected_movie = st.selectbox("🔍 Search Movie", sorted(movies['title'].values))

    if st.button("Recommend"):
        names, posters, ratings, overviews, trailers = recommend(selected_movie)

        cols = st.columns(5)

        for i in range(5):
            with cols[i]:
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{posters[i]}" width="100%" style="border-radius:10px;">
                    <p class="movie-title">{names[i]}</p>
                    <p class="movie-rating">⭐ {round(ratings[i],1) if ratings[i] else "N/A"}</p>
                    <p class="movie-overview">{(overviews[i][:80] + "...") if overviews[i] else "No description"}</p>
                </div>
                """, unsafe_allow_html=True)

                if trailers[i]:
                    st.markdown(f"[▶️ Trailer]({trailers[i]})")

                if st.button(f"❤️ Fav {i}"):
                    if names[i] not in st.session_state.favorites:
                        st.session_state.favorites.append(names[i])

    # Favorites section
    st.write("---")
    st.subheader("❤️ Favorites")

    for fav in st.session_state.favorites:
        st.write("👉", fav)