import os
import dearpygui.dearpygui as dpg
import find_by_genre as fbg
import all_field as search
import getposter as gp
import json

movies_data = fbg.load_json("dataset/movies.json")

dpg.create_context()

with dpg.value_registry():
    genre_selected = dpg.add_string_value(default_value="")
    
genres = [
    "Action", "Adventure", "Fantasy", "Science fiction", "Crime", "Drama", "Thriller",
    "Animation", "Family", "Western", "Comedy", "Romance", "Horror", "Mystery",
    "History", "War", "Music", "Documentary", "Foreign", "Tv movie"
]

with dpg.theme() as dropdown_theme:
    with dpg.theme_component(dpg.mvCombo):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))  
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (21, 76, 121, 50)) 
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (21, 76, 121, 200)) 
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (0, 0, 0, 100))   
        dpg.add_theme_color(dpg.mvStyleVar_WindowPadding, 5)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5) 
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 5)  
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 10) 


def switch_ui(hide_ui, show_ui):
    dpg.hide_item(hide_ui)  
    dpg.show_item(show_ui)  

def genre_menu_callback(sender, app_data, user_data):
    poster_paths = []
    genre = user_data
    movies = fbg.find_top_movies_by_genre(genre.lower())  # Lấy danh sách phim theo thể loại

    if not dpg.does_item_exist("Genresults_list"):
        print("Error: 'Genresults_list' does not exist!")
        return

    dpg.delete_item("Genresults_list", children_only=True)  # Xóa kết quả cũ

    if movies:
        with dpg.texture_registry(tag="GenreTextureRegistry") as reg_id:
            for movie in movies:
                poster_path = f"poster/{movie['id']}.jpg"
                try:
                    width, height, channels, data = dpg.load_image(poster_path)
                    texture_id = dpg.add_static_texture(width, height, data, parent=reg_id)
                    
                    with dpg.group(parent="Genresults_list", horizontal=False):
                        dpg.add_image(texture_id, width=100, height=150)  
                        with dpg.group(horizontal=True): 
                            dpg.add_text(f"{movie['title']} ({movie['vote_average']})")
                            dpg.add_text(f"ID: {movie['id']}")
                except Exception as e:
                    print(f"Could not load image {poster_path}: {e}")
    else:
        dpg.add_text(f"Không tìm thấy phim nào trong thể loại '{genre}'", parent="Genresults_list")

    switch_ui("Primary Window", "Genre UI")

def top_movie():
    
    movies = fbg.find_top_movies_by_genre('action')  # Lấy danh sách phim theo thể loại
    #ghép back top movie vào movies = top movie ()

    # Cập nhật danh sách phim hiển thị
    if not dpg.does_item_exist("TopMovie_list"):
        print("Error: 'TopMovie_list' does not exist!")
        return

    dpg.delete_item("TopMovie_list", children_only=True)  # Xóa kết quả cũ

    if dpg.does_item_exist("TopMovieTextureRegistry"):
        dpg.delete_item("TopMovieTextureRegistry")

    if movies:
        with dpg.texture_registry(tag="TopMovieTextureRegistry") as reg_id:
            row = None  # Dùng để tạo một hàng mới
            for idx, movie in enumerate(movies):
                if idx % 5 == 0:  # Mỗi hàng chứa tối đa 5 bộ phim
                    row = dpg.add_group(parent="TopMovie_list", horizontal=True, horizontal_spacing=60)

                poster_path = gp.get_poster_image(movie['id'])
                try:
                    width, height, channels, data = dpg.load_image(poster_path)
                    texture_id = dpg.add_static_texture(width, height, data, parent=reg_id)

                    with dpg.group(parent=row, horizontal=False):
                        dpg.add_image_button(texture_id, width=100, height=150, callback=show_movie_details, user_data=movie)
                        dpg.add_spacer(width=25)
                        titletext = dpg.add_text(f"{movie['title']} ({movie['vote_average']})", wrap=110)
                        dpg.add_spacer(width=25)
                        dpg.bind_item_font(titletext, titleMG)

                except Exception as e:
                    print(f"Could not load image {poster_path}: {e}")
    else:
        dpg.add_text(f"Không có top phim", parent="TopMovie_list")

def show_movie_details(sender, app_data, user_data):
    global current_ui

    if not dpg.does_item_exist("DetailUI"):
        print("Error: Parent container 'DetailUI' does not exist.")
        return
    dpg.delete_item("DetailContent", children_only=True)  # Clear everything under DetailUI
    movie = user_data  # Thông tin phim được truyền qua user_data
    print (movie)
    if dpg.does_item_exist("DetailTextureRegistry"):
        dpg.delete_item("DetailTextureRegistry")

    try:    
        with dpg.texture_registry(tag="DetailTextureRegistry") as reg_id:
            gp.get_poster_image(movie['id'])
            poster_path = f"poster/{movie['id']}.jpg"
            movie_details = movies_data.get(str(movie['id']))
            try:
                width, height, channels, data = dpg.load_image(poster_path)
                texture_id = dpg.add_static_texture(width, height, data)
                with dpg.group(parent="DetailContent", horizontal=True):
                    dpg.add_image(texture_id, width=200, height=300, pos= (20,20))
                    with dpg.group(horizontal=False):
                        dpg.add_spacer(width=30)
                        titleM = dpg.add_text(f"{movie['title']}", color=(255, 255, 255), indent=30, wrap = 500)
                        dpg.bind_item_font(titleM, titlemovieText)
                        dpg.add_spacer(width=10)

                        release = dpg.add_text(f"Release Date: {movie_details.get('release_date', 'Unknown')}", color=(255, 255, 255), indent=30)
                        print (movie_details.get('release_date', 'Unknown'))
                        dpg.bind_item_font(release, detailText)
                        dpg.add_spacer(width=10)

                        overView = dpg.add_text(f"Overview: {movie_details.get('overview', 'No description available.')}", wrap=500, color=(255, 255, 255), indent=30)
                        dpg.bind_item_font(overView, detailText)
                        dpg.add_spacer(width=10)

                        rating = dpg.add_text(f"Rating: {movie_details.get('vote_average', 'N/A')}", color=(255, 255, 255), indent=30)
                        dpg.bind_item_font(rating, detailText)

            except Exception as e:
                dpg.add_text(f"Poster not available: {e}")
        
        # Switch UI after successfully updating details
    except Exception as e:
        print(f"Error creating movie details group: {e}")
    switch_ui(current_ui, "DetailUI")

def search_movies(sender, app_data, user_data):
    # Lấy nội dung tìm kiếm từ ô input
    user_query = dpg.get_value("SearchInput")
    print(user_query)
    if not user_query.strip():
        print("Please enter a search query.")
        return

    # Gọi hàm search và nhận kết quả
    top_movies = search.search(user_query)

    dpg.delete_item("results_list", children_only=True)  # Xóa kết quả cũ

    # Create a container for search results
    with dpg.group(tag="SearchResults", parent="results_list"):
        if top_movies is None:
            dpg.add_text("No results found.")
        else:
            for _, row in top_movies.iterrows():
                titletext = dpg.add_text(f"Title: {row['title']}")
                dpg.bind_item_font(titletext, movieText)
                try:
                    genres_data = json.loads(row['genres']) if row['genres'] else []
                    genre_names = [genre['name'] for genre in genres_data]
                    gennrestext = dpg.add_text(f"Genres: {', '.join(genre_names) if genre_names else 'None'}")
                    dpg.bind_item_font(gennrestext, movieText)
                except json.JSONDecodeError:
                    dpg.add_text("Genres: Invalid format")
                dpg.add_separator()  

with dpg.theme() as child_window_theme:
    with dpg.theme_component(dpg.mvChildWindow):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (100,102,155,200))  
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (100, 100, 150, 255))  
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (150, 150, 200, 255))  

with dpg.font_registry():
    header = dpg.add_font("font/LithosPro-Regular.otf",40)  
    buttonFont = dpg.add_font("font/LithosPro-Regular.otf",13) 
    title = dpg.add_font("font/MAIAN.TTF",20)
    titleMG = dpg.add_font("font/arialbd.ttf",13)
    movieText = dpg.add_font("font/MAIAN.TTF",15)
    detailText = dpg.add_font("font/arial.ttf",16)
    titlemovieText = dpg.add_font("font/LithosPro-Black.otf",35)

with dpg.theme() as input_theme:
    with dpg.theme_component(dpg.mvInputText):  
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))  
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (150, 150, 150, 255)) 
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (100,102,155,200))

with dpg.texture_registry():
    width, height, channels, data = dpg.load_image("asset/Homepage.png")
    texture_id = dpg.add_static_texture(width, height, data)
    width1, height1, channels1, data1 = dpg.load_image("asset/bgExtra.png")
    bgExtra = dpg.add_static_texture(width1, height1, data1)
with dpg.theme() as transparent_button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)  # Nền bình thường (trong suốt)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255, 30), category=dpg.mvThemeCat_Core)  # Hover
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255, 50), category=dpg.mvThemeCat_Core)  # Khi nhấn

with dpg.window(label="Movie Retrieval Chatbot", tag="Primary Window"):
    current_ui = "Primary Window"
    dpg.add_image(texture_id)
    
    dpg.draw_text((230, 25), "NEMORY", color=(255, 255, 255, 255), size=40, tag="custom_text")
    dpg.bind_item_font("custom_text", header)

    dpg.draw_text((260, 220), "No matter what you remember about the movie, \nyou can use it to search.", color=(255, 255, 255, 255), size=20, tag="header1")
    dpg.bind_item_font("header1", title)

    with dpg.group(pos=(410, 90), width = 150, height = 100):
        dropdown_genre = dpg.add_combo(
            items=genres, 
            callback=lambda s, a: [dpg.set_value(genre_selected, a),switch_ui("Primary Window", "Genre UI")],
            user_data= genres, 
            default_value="Genre"
        )
    dpg.bind_item_font(dropdown_genre, buttonFont)
    dpg.bind_item_theme(dropdown_genre, dropdown_theme)  

    # with dpg.group(pos=(410, 90), width = 150, height = 100):
    #     dropdown_country = dpg.add_combo(
    #         items=countries, 
    #         callback=lambda s, a: [dpg.set_value(country_selected, a),switch_ui("Primary Window", "Search UI")],
    #         user_data= countries, 
    #         default_value="Country"
    #     )
    # dpg.bind_item_font(dropdown_country, buttonFont)
    # dpg.bind_item_theme(dropdown_country, dropdown_theme)  

    dpg.add_input_text(tag="SearchInput", hint="Input here...", pos=(460,30), width=420, height=40, multiline=True)
    dpg.bind_item_theme("SearchInput", input_theme)
    dpg.bind_item_font("SearchInput", title)

    button_search = dpg.add_button(label="Search!", pos=(920, 35), callback=search_movies)
    dpg.bind_item_theme(button_search, transparent_button_theme)
    dpg.bind_item_font(button_search, title)

    with dpg.child_window(tag="results_list", width=480, height=220, pos=(270, 360)):
        dpg.add_text("Results will appear here.") 
    dpg.bind_item_theme("results_list", child_window_theme)

    with dpg.child_window(tag="TopMovie_list", width=800, height=480, pos=(100, 150)):
        dpg.add_text("Results will appear here.") 
        top_movie()

    dpg.bind_item_theme("TopMovie_list", child_window_theme)


with dpg.window(label="Genre", tag="Genre UI", show=False):
    dpg.add_image(bgExtra)
    headerGen = dpg.add_button(label="NEMORY", callback=lambda: switch_ui("Genre UI", "Primary Window"), pos=(50, 60))
    dpg.bind_item_font(headerGen, header)
    dpg.bind_item_theme(headerGen, transparent_button_theme)

    with dpg.group(horizontal=True, horizontal_spacing=20, pos=(310, 45)):
        for genre in ["Action", "Adventure", "Fantasy", "Science fiction", "Crime", "Drama", "Thriller"]:
            btn = dpg.add_button(label=genre, callback=genre_menu_callback, user_data=genre)
            dpg.bind_item_font(btn, buttonFont)
            dpg.bind_item_theme(btn, transparent_button_theme)
    with dpg.group(horizontal=True, horizontal_spacing=20, pos =(310, 70)):  
        for genre in ["Animation", "Family", "Western", "Comedy", "Romance", "Horror", "Mystery"]:
            btn = dpg.add_button(label=genre, callback=genre_menu_callback, user_data=genre)
            dpg.bind_item_font(btn, buttonFont)
            dpg.bind_item_theme(btn, transparent_button_theme)  

    with dpg.group(horizontal=True, horizontal_spacing=20, pos =(310, 95)):  
        for genre in ["History", "War", "Music", "Documentary", "Foreign", "Tv movie"]:
            btn = dpg.add_button(label=genre, callback=genre_menu_callback, user_data=genre)
            dpg.bind_item_font(btn, buttonFont)
            dpg.bind_item_theme(btn, transparent_button_theme) 

    with dpg.child_window(tag="Genresults_list", width=800, height=600, pos=(100, 150)):
        dpg.add_text("Results will appear here.") 
    dpg.bind_item_theme("Genresults_list", child_window_theme)

# Tạo viewport và hiển thị
dpg.create_viewport(title="Movie Retrieval Chatbot", width=1000, height=711)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()