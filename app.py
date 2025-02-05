import streamlit as st
import pickle
import requests

st.set_page_config(
    page_title="Movie Recommender", 
    page_icon="🎬", 
    layout="wide"
)

def fetch_poster(movie_id):
     url = "https://api.themoviedb.org/3/movie/{}?api_key=da105461528af281bced1d01b8c5d154&language=en-US".format(movie_id)
     data=requests.get(url)
     data=data.json()
     poster_path = data['poster_path']
     full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
     return full_path


movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))
movies_list=movies['original_title'].values

st.header("Movie Recommender System")

import streamlit.components.v1 as components

imageCarouselComponent = components.declare_component("image-carousel-component", path="frontend/public")


imageUrls = [
    fetch_poster(19995),
    fetch_poster(299536),
    fetch_poster(559),
    fetch_poster(2830),
    fetch_poster(68721),
    fetch_poster(168259),
    fetch_poster(278927),
    fetch_poster(240),
    fetch_poster(155),
    fetch_poster(598),
    fetch_poster(914),
    fetch_poster(255709),
    fetch_poster(572154)
   
    ]


imageCarouselComponent(imageUrls=imageUrls, height=200)
selectvalue=st.selectbox("Select movie from dropdown", movies_list)

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=da105461528af281bced1d01b8c5d154&language=en-US"
    response = requests.get(url).json()
    
    poster_path = response.get('poster_path', '')
    poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else None
    
    title = response.get('original_title', 'Unknown')
    release_date = response.get('release_date', 'N/A')
    rating = response.get('vote_average', 'N/A')

    
    # Debug print statement to check the data
    print(f"Fetched movie details for ID {movie_id}: {title}, {release_date}, {rating}")
    
    return poster_url, title, release_date, rating


def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=da105461528af281bced1d01b8c5d154&language=en-US"
    data = requests.get(url).json()
    
    for video in data.get('results', []):
        if video['type'] == "Trailer":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None  # If no trailer is found



def recommend(movie):
    index=movies[movies['original_title']==movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector:vector[1])
    recommend_movie=[]
    recommend_poster=[]
    for i in distance[1:11]:
        movies_id=movies.iloc[i[0]].id
        recommend_movie.append(movies.iloc[i[0]].original_title)
        recommend_poster.append(fetch_poster(movies_id))
    return recommend_movie, recommend_poster


if st.button("Show Recommend"):
    movie_names, movie_posters = recommend(selectvalue)
    
    # Fetch details only for the recommended movies
    movie_details = [fetch_movie_details(movies[movies['original_title'] == name].iloc[0].id) for name in movie_names]

    # Ensure we have at least 10 recommendations (if available)
    extra_movies = recommend(movie_names[0])[0]  # Get additional 5 recommendations
    extra_details = [fetch_movie_details(movies[movies['original_title'] == name].iloc[0].id) for name in extra_movies]
    
    all_movies = movie_details + extra_details  # Combine both lists

    # Display first row (5 movies)
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]

    for i in range(5):  
        poster, title, release_date, rating = all_movies[i]
        with cols[i]:
            st.markdown(f"""
                <div style="text-align: center;">
                    <img src="{poster}" width="150" style="border-radius: 15px; margin-bottom: 10px;">
                    <div style="font-size: 12px;">
                        <strong>{title}</strong><br>
                        <em>Release Date: {release_date}</em><br>
                        <em>⭐ {rating}/10</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            trailer_url = fetch_trailer(movies[movies['original_title'] == title].iloc[0].id)
            if trailer_url:
                st.markdown(f'<a href="{trailer_url}" target="_blank"><button style="width: 100%; background-color: #ff6600; color: white; padding: 8px; border: none; border-radius: 5px; cursor: pointer;">🎬 Watch Trailer</button></a>', unsafe_allow_html=True)
            else:
                st.text("No Trailer Available")

    # Display second row (next 5 movies)
    col6, col7, col8, col9, col10 = st.columns(5)
    cols = [col6, col7, col8, col9, col10]

    for i in range(5, 10):  
        poster, title, release_date, rating = all_movies[i]
        with cols[i - 5]:
            st.markdown(f"""
                <div style="text-align: center;">
                    <img src="{poster}" width="150" style="border-radius: 15px; margin-bottom: 10px;">
                    <div style="font-size: 12px;">
                        <strong>{title}</strong><br>
                        <em>Release Date: {release_date}</em><br>
                        <em>⭐ {rating}/10</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            trailer_url = fetch_trailer(movies[movies['original_title'] == title].iloc[0].id)
            if trailer_url:
                st.markdown(f'<a href="{trailer_url}" target="_blank"><button style="width: 100%; background-color: #ff6600; color: white; padding: 8px; border: none; border-radius: 5px; cursor: pointer;">🎬 Watch Trailer</button></a>', unsafe_allow_html=True)
            else:
                st.text("No Trailer Available")

