import streamlit as st

# Dummy method which would use our recommendation system
def process_selected_movies(selected_movies):
    print("Selected Movies in Order:")
    for movie in selected_movies:
        print(movie)

def main():
    st.title("Movie Recommendation System")

    movies = [
        "The Shawshank Redemption", "The Godfather", "The Dark Knight",
        "Schindler's List", "Pulp Fiction", "The Lord of the Rings: The Return of the King",
        "The Good, the Bad and the Ugly", "Fight Club", "Forrest Gump",
        "Inception", "Star Wars: Episode V - The Empire Strikes Back"
    ]
    
    # Sidebar for movie selection
    with st.sidebar:
        st.header("Select Movies")
        # Multiselect widget to select movies from the given array
        selected_movies = st.multiselect("Choose your movies:", movies)

    # Main area for displaying selected movies
    st.header("Selected Movies")
    if selected_movies:
        ordered_movies = st.multiselect("Reorder your selected movies (optional):",
                                        selected_movies, default=selected_movies)
        
        if st.button("Submit"):
            process_selected_movies(ordered_movies)
            st.success("Movies submitted successfully!")
    else:
        st.write("No movies selected yet. Please select movies from the sidebar.")

if __name__ == "__main__":
    main()
