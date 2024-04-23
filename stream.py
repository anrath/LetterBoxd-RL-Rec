import streamlit as st
import pandas as pd
import numpy as np
import json
import torch
import transformers

@st.cache_data
def load_data(filepath):
    data = pd.read_csv(filepath)
    data.dropna(subset=['year_released'], inplace=True)
    drop_cols = ['image_url', 'imdb_id', 'imdb_link', 'tmdb_id', 'tmdb_link']
    data.drop(drop_cols, axis=1, inplace=True)
    data['year_released'] = data['year_released'].astype('Int16')
    data['runtime'] = data['runtime'].astype('Int16', errors='ignore')
    data.set_index('movie_id', inplace=True)
    return data

@st.cache_resource()
def load_model(model_path, tokenizer_name="openai-community/gpt2"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = torch.load(model_path, map_location=device)
    tokenizer = transformers.GPT2Tokenizer.from_pretrained(tokenizer_name)
    if device.type == "cuda":
        model = model.to("cuda")
    return model, tokenizer

movie_data = load_data('data/movie_data.csv')
gpt2, gpt2_tokenizer = load_model("training/gpt-2-letterboxd-tune-000.pt")
nan2list = lambda x: x if type(x) is str else '[]'

def format_movie_data_v2(movie_data): # , user_rating, user_review):
    release_yr = movie_data.get("year_released", None)
    title_fmt = movie_data.get("movie_title", "N/A") + (f" ({release_yr})" if release_yr else "")
    genre_fmt = ' and '.join([x.lower() for x in json.loads(nan2list(movie_data.get('genres', "[]")))])
    runtime = movie_data.get('runtime', None)
    if runtime is not None and not np.isnan(runtime):
        hours = int(runtime // 60)
        minutes = int(runtime % 60)
        runtime_fmt = f"{hours}h {minutes}m"
    else:
        runtime_fmt = "N/A"
    
    avg_rating = movie_data.get('vote_average')
    votes = movie_data.get('vote_count')
    if votes is not None and not np.isnan(votes) and votes > 0:
        votes = int(votes)
        avg_rating_fmt = f"{avg_rating:.2f} ({votes} vote(s))"
    else:
        avg_rating_fmt = "N/A"
    
    production_countries_fmt = ' and '.join(json.loads(nan2list(movie_data.get('production_countries', "[]")))) or 'N/A'
    languages_fmt = ' and '.join(json.loads(nan2list(movie_data.get('spoken_languages', "[]")))) or 'N/A'
    overview = movie_data.get("overview", "N/A")
    
    return f"""
Title: {title_fmt}
Genres: {genre_fmt}
Runtime: {runtime_fmt}
Average rating: {avg_rating_fmt}
Production countries: {production_countries_fmt}
Languages: {languages_fmt}
Overview: {overview}
""".strip()

def process_selected_movies(selected_movie_ids, movie_ratings):
    string = ""
    for movie, rating in zip(selected_movie_ids, movie_ratings):
        mv = movie_data.loc[movie]
        formatted = format_movie_data_v2(mv)
        string += f"---\n{formatted}\n---\nRating: {rating} / 10\n"
        
    tokenization = gpt2_tokenizer(string, return_tensors='pt', truncation=True).to('cuda')
    with torch.no_grad():
        out = gpt2.generate(**tokenization, max_new_tokens=1, do_sample=False, pad_token_id=gpt2_tokenizer.eos_token_id)
    out = gpt2_tokenizer.decode(out[0])
    try:
        pred_rating = int(out.split()[-1])
        st.write(pred_rating)
        return pred_rating
    except:
        print("parse error")
        st.write(out)
        return out
        
def main():
    st.title("Movie Recommendation System")
    st.session_state.movie_ratings = {}
    
    # Sidebar for movie selection
    with st.sidebar:
        st.header("Select Movies")
        # Text input for searching movies
        search_query = st.text_input("Search movies:", "")
        
        # Filtering movies based on search query
        if search_query:
            filtered_movies = movie_data[movie_data['movie_title'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_movies = movie_data.head(0)
        
        # Display filtered movies in a selectbox, using movie_id as a reference
        selected_movie_id_list = st.multiselect("Choose a movie:", filtered_movies['movie_title']  + " - " + filtered_movies.index.map(str))
        
        # Button to add movie to the selection list
        if st.button("Add Movie"):
            if selected_movie_id_list:
                movie_id_list = [idVal.split(' - ')[-1] for idVal in selected_movie_id_list]
                add_movie_to_selection(movie_id_list)

    # Main area for displaying selected movies and collecting ratings
    st.header("Your Selected Movies")
    display_selected_movies()

def add_movie_to_selection(movie_id_list):
    for movie_id in movie_id_list:
        if 'selected_movies' not in st.session_state:
            st.session_state.selected_movies = set()
        st.session_state.selected_movies.add(movie_id)
    st.rerun()

def display_selected_movies():
    # Display the list of selected movies and allow rating
    if 'selected_movies' in st.session_state and st.session_state.selected_movies:
        selected_movie_ids = list(st.session_state.selected_movies)
        selected_movies = movie_data.loc[selected_movie_ids]
        
        for movie_id, movie in selected_movies.iterrows():
            rating = st.number_input(f'Rate "{movie["movie_title"]}":', min_value=1, max_value=10, value=5, key=movie_id)
            st.session_state.movie_ratings[movie_id] = rating
        
        if st.button("Submit Ratings"):
            process_selected_movies(selected_movie_ids, st.session_state.movie_ratings)
            st.success("Movies and ratings submitted successfully!")
    else:
        st.write("No movies selected yet. Please select movies from the sidebar.")

if __name__ == "__main__":
    main()
