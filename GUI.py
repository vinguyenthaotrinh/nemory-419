import os
import dearpygui.dearpygui as dpg
import find_by_genre as fbg
import getposter as gp
import all_field as search
import json
import category_search as cs

movies_file = "dataset/movies.json"
movies_data = fbg.load_json(movies_file)
current_ui = "Primary Window"
cs.load_data("dataset/genres_inverted.json", "dataset/movies.json", "dataset/production_countries_inverted.json", "dataset/release_year_inverted.json")

genres = [
    "Select Genre",
    "Action", "Adventure", "Fantasy", "Science fiction", "Crime", "Drama", "Thriller",
    "Animation", "Family", "Western", "Comedy", "Romance", "Horror", "Mystery",
    "History", "War", "Music", "Documentary", "Foreign", "Tv movie"
]

countries = [
    "Select Country",
    "United States of America", "United Kingdom", "Jamaica", "Bahamas", "Dominica", "Czech Republic", "Poland",
    "Slovenia", "New Zealand", "Germany", "Italy", "Malta", "Australia", "France",
    "Belgium"
]

year = [
    "Select Year",
    '1910s', '1920s', '1930s', '1940s', '1950s', '1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s'
]

current_state = {
    "keyword": "",
    "filters": {
        "genre": None,
        "country": None,
        "year": None
    }
}

dpg.create_context()

with dpg.value_registry():
    genre_selected = dpg.add_string_value(default_value="Select Genre")
    country_selected = dpg.add_string_value(default_value="Select Country")
    release_year_selected = dpg.add_string_value(default_value="Select Year")
    sort_selected = dpg.add_string_value(default_value="Sort by")

    

def switch_ui(hide_ui, show_ui):
    dpg.hide_item(hide_ui)  
    if show_ui == "Primary Window":
        reset_primary_window()
    else: reset_search_ui()

    dpg.show_item(show_ui)  

def top_movie():
    movies = cs.find_movie_ids_by_filters("", "", "")
    movies = cs.get_movies_information_from_ids(movies)
    movies = cs.sort_by_popularity(movies, 10)

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
        dpg.add_text(f"No top movies found", parent="TopMovie_list")

def center_text_in_window(window_width, text_tag, text, font_size):
    
    # Giả sử chiều cao font và chiều rộng mỗi ký tự tạm tính
    text_width = len(text) * (font_size * 2)  # Ước lượng chiều rộng ký tự
    print(text_width)
    text_height = font_size                     # Chiều cao của font
    
    # Tính toán vị trí chính giữa
    x_pos = (window_width - text_width) / 2
    y_pos = 110
    
    # Cập nhật vị trí cho text
    dpg.configure_item(text_tag, pos=(x_pos, y_pos))

def filter_movies():
    genre = dpg.get_value(genre_selected)
    country = dpg.get_value(country_selected)
    year = dpg.get_value(release_year_selected)
    sort_by = dpg.get_value(sort_selected)

    current_state["filters"]["genre"] = genre if genre != "Select Genre" else None
    current_state["filters"]["country"] = country if country != "Select Country" else None
    current_state["filters"]["year"] = year if year != "Select Year" else None

    keyword = current_state["keyword"]

    # Tạo chuỗi điều kiện hiển thị
    conditions = []
    if genre != "Select Genre":
        conditions.append(f"{genre.lower()}")
    if country != "Select Country":
        conditions.append(f"country {country}")
    if year != "Select Year":
        conditions.append(f"year {year}")
    print(conditions)

    # Ghép các điều kiện thành chuỗi
    condition_text = ", ".join(conditions)
    display_text = f"These are {condition_text} movies" if conditions else "There are no movies that match your request."
    
    # Cập nhật dòng text trên UI
    if dpg.does_item_exist("filter_text"):
        dpg.set_value("filter_text", display_text)
    else:
        dpg.add_text(display_text, tag="filter_text", parent="Search UI", color=(255, 255, 255))

    #ghép back filter vào movies = filter (genre, country, year)
    # filtered_movies = [movie for movie in movies if
    #                    (genre == "" or movie["genre"] == genre) and
    #                    (country == "" or movie["country"] == country) and
    #                    (year == "" or str(movie["year"]) == year)]

    #Ghép back sort by Popularity, Rating, Latest Movie
    movie_ids = cs.find_movie_ids_by_filters(genre, year, country)
    if (keyword != ""):
        movies = search.search(keyword)
        movie_ids = (
            [str(movie['id']) for movie in movies] if isinstance(movies, list) 
            else list(map(str, movies['id'].tolist()))
        )
    
    filtered_ids = cs.find_movie_ids_by_filters(genre, year, country)
    final_movie_ids = set(filtered_ids).intersection(movie_ids)

    
    movies = cs.get_movies_information_from_ids(final_movie_ids)
    movies = cs.sort_by_popularity(movies, 10)

    if sort_by == "Popularity":
        movies = cs.sort_by_popularity(movies, 10)
    elif sort_by == "Rating":
        movies = cs.sort_movies_by_score(movies, 10)
    elif sort_by == "Latest Movie":
        movies = cs.sort_by_release_date(movies, 10)
    

    # Cập nhật danh sách phim hiển thị
    if not dpg.does_item_exist("Movie_list"):
        print("Error: 'Movie_list' does not exist!")
        return

    dpg.delete_item("Movie_list", children_only=True)  # Xóa kết quả cũ

    if dpg.does_item_exist("MovieTextureRegistry"):
        dpg.delete_item("MovieTextureRegistry")

    if movies:
        with dpg.texture_registry(tag="MovieTextureRegistry") as reg_id:
            row = None  # Dùng để tạo một hàng mới
            for idx, movie in enumerate(movies):
                if idx % 5 == 0:  # Mỗi hàng chứa tối đa 5 bộ phim
                    row = dpg.add_group(parent="Movie_list", horizontal=True, horizontal_spacing=60)

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
        dpg.add_text(f"No matching movies found", parent="Movie_list")



def on_select(sender, app_data):
    if app_data.startswith("Select"):
        selected_value = None
    else:
        selected_value = app_data
    dpg.set_value(sender, app_data)

# Hàm hiển thị giao diện chi tiết phim
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
            print("hacHACB")
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

def reset_primary_window():
    # Reset các dropdown về giá trị mặc định
    dpg.set_value(dropdown_genre, "Select Genre")
    dpg.set_value(dropdown_country, "Select Country")
    dpg.set_value(dropdown_year, "Select Year")
    
    # Reset giá trị của search input
    dpg.set_value("SearchInput", "")

def reset_search_ui():
    # Reset các dropdown về giá trị mặc định
    dpg.set_value(dropdown_genre2, "Select Genre")
    dpg.set_value(dropdown_country2, "Select Country")
    dpg.set_value(dropdown_year2, "Select Year")
    
    # Reset giá trị của search input
    dpg.set_value("SearchInput1", "")

def search_movies(sender, app_data, user_data):
    # Lấy nội dung tìm kiếm từ ô input
    user_query = dpg.get_value("SearchInput")
    current_state["keyword"] = user_query
    current_state["filters"] = {"genre": None, "country": None, "year": None}

    if not user_query.strip():
        print("Please enter a search query.")
        return

    # Gọi hàm search và nhận kết quả
    top_movies = search.search(user_query)

    if not dpg.does_item_exist("Movie_list"):
        print("Error: 'Movie_list' does not exist!")
        return

    dpg.delete_item("Movie_list", children_only=True)  # Xóa kết quả cũ

    if dpg.does_item_exist("MovieTextureRegistry"):
        dpg.delete_item("MovieTextureRegistry")

    # Check if top_movies is valid
    if top_movies is None or top_movies.empty:
        dpg.add_text("No matching movies found", parent="Movie_list")
        return

    # Display movies with posters and details
    with dpg.texture_registry(tag="MovieTextureRegistry") as reg_id:
        row = None  # Container for a row of movies
        for idx, (_, row_data) in enumerate(top_movies.iterrows()):  # Iterate over DataFrame rows
            movie = {
                "title": row_data["title"],
                "id": row_data["id"],
                "vote_average": row_data["vote_average"],
                "release_date": row_data["release_date"],
                "overview": row_data["overview"],
            }

            if idx % 5 == 0:  # Mỗi hàng chứa tối đa 5 bộ phim
                row = dpg.add_group(parent="Movie_list", horizontal=True, horizontal_spacing=60)

            poster_path = gp.get_poster_image(movie["id"])
            if poster_path:
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
                print(f"No poster path found for movie ID {movie['id']}.")

    display_text = f"Keyword: {user_query}"

    if dpg.does_item_exist("filter_text"):
        dpg.set_value("filter_text", display_text)
    else:
        dpg.add_text(display_text, tag="filter_text", parent="Search UI", color=(255, 255, 255))

    switch_ui("Primary Window", "Search UI")

def search_movies1(sender, app_data, user_data):
    # Lấy nội dung tìm kiếm từ ô input
    user_query = dpg.get_value("SearchInput1")
    current_state["keyword"] = user_query

    print(user_query)
    if not user_query.strip():
        print("Please enter a search query.")
        return
    
    display_text = f"Keyword: {user_query}"

    if dpg.does_item_exist("filter_text"):
        dpg.set_value("filter_text", display_text)
    else:
        dpg.add_text(display_text, tag="filter_text", parent="Search UI", color=(255, 255, 255))

    # Gọi hàm search và nhận kết quả
    top_movies = search.search(user_query)

    if not dpg.does_item_exist("Movie_list"):
        print("Error: 'Movie_list' does not exist!")
        return

    dpg.delete_item("Movie_list", children_only=True)  # Xóa kết quả cũ

    if dpg.does_item_exist("MovieTextureRegistry"):
        dpg.delete_item("MovieTextureRegistry")

    # Check if top_movies is valid
    if top_movies is None or top_movies.empty:
        dpg.add_text("No matching movies found", parent="Movie_list")
        return

    # Display movies with posters and details
    with dpg.texture_registry(tag="MovieTextureRegistry") as reg_id:
        row = None  # Container for a row of movies
        for idx, (_, row_data) in enumerate(top_movies.iterrows()):  # Iterate over DataFrame rows
            movie = {
                "title": row_data["title"],
                "id": row_data["id"],
                "vote_average": row_data["vote_average"],
                "release_date": row_data["release_date"],
                "overview": row_data["overview"],
            }

            if idx % 5 == 0:  # Mỗi hàng chứa tối đa 5 bộ phim
                row = dpg.add_group(parent="Movie_list", horizontal=True, horizontal_spacing=60)

            poster_path = gp.get_poster_image(movie["id"])
            if poster_path:
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
                print(f"No poster path found for movie ID {movie['id']}.")

def dropdown_callback(sender, app_data, user_data):
    # Cập nhật giá trị dropdown đã chọn
    if user_data == "genre":
        dpg.set_value(genre_selected, app_data)

        display_text = f"These are {app_data} movies"

        if dpg.does_item_exist("filter_text"):
            dpg.set_value("filter_text", display_text)
        else:
            dpg.add_text(display_text, tag="filter_text", parent="Search UI", color=(255, 255, 255))
            
    elif user_data == "country":
        dpg.set_value(country_selected, app_data)

        display_text = f"These are {app_data} movies"
        
        if dpg.does_item_exist("filter_text"):
            dpg.set_value("filter_text", display_text)
        else:
            dpg.add_text(display_text, tag="filter_text", parent="Search UI", color=(255, 255, 255))
            

    elif user_data == "country":
        dpg.set_value(release_year_selected, app_data)

        display_text = f"These are {app_data} movies"
        
        if dpg.does_item_exist("filter_text"):
            dpg.set_value("filter_text", display_text)
        else:
            dpg.add_text(display_text, tag="filter_text", parent="Search UI", color=(255, 255, 255))
            
    else: 
        display_text = "There are no movies that match your request."
        if dpg.does_item_exist("filter_text"):
            dpg.set_value("filter_text", display_text)
        else:
            dpg.add_text(display_text, tag="filter_text", parent="Search UI", color=(255, 255, 255))
            
    filter_movies()
    switch_ui("Primary Window", "Search UI")

with dpg.theme() as result_background_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (50, 50, 50, 255))  # Màu xám

with dpg.theme() as child_window_theme:
    with dpg.theme_component(dpg.mvChildWindow):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (100,102,155,200))  
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (100, 100, 150, 255))  
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (150, 150, 200, 255))  

with dpg.theme() as child_window_searchbar_theme:
    with dpg.theme_component(dpg.mvChildWindow):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (100,102,155,0))  
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (100, 100, 150, 0))  
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (150, 150, 200, 0))  

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


with dpg.font_registry():
    # Tải font từ file
    header = dpg.add_font("font/LithosPro-Regular.otf",40)  
    buttonFont = dpg.add_font("font/LithosPro-Regular.otf",13) 
    title = dpg.add_font("font/MAIAN.TTF",20)
    keyword = dpg.add_font("font/MAIAN.TTF",30)

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
    
    dpg.draw_text((220, 25), "NEMORY", color=(255, 255, 255, 255), size=40, tag="custom_text")
    dpg.bind_item_font("custom_text", header)

    dpg.draw_text((380, 140), "THE BEST MOVIES OF ALL TIME", color=(255, 255, 255, 255), size=20, tag="top_text")
    dpg.bind_item_font("top_text", title)

    with dpg.group(pos=(300, 90), width = 150, height = 100):
        dropdown_genre = dpg.add_combo(
            items=genres, 
            callback=dropdown_callback,
            user_data= "genre", 
            default_value="Select Genre",

        )
    dpg.bind_item_font(dropdown_genre, buttonFont)
    dpg.bind_item_theme(dropdown_genre, dropdown_theme)  

    with dpg.group(pos=(500, 90), width = 150, height = 100):
        dropdown_country = dpg.add_combo(
            items=countries, 
            callback=dropdown_callback,
            user_data= "country", 
            default_value="Select Country"
        )
    dpg.bind_item_font(dropdown_country, buttonFont)
    dpg.bind_item_theme(dropdown_country, dropdown_theme) 

    with dpg.group(pos=(700, 90), width = 150, height = 100):
        dropdown_year = dpg.add_combo(
            items=year, 
            callback=dropdown_callback,
            user_data= "year", 
            default_value="Select Year"
        )
    dpg.bind_item_font(dropdown_year, buttonFont)
    dpg.bind_item_theme(dropdown_year, dropdown_theme)  

    dpg.add_input_text(tag="SearchInput", hint="Input here...", pos=(450,30), width=420, height=40, multiline=True)
    dpg.bind_item_theme("SearchInput", input_theme)
    dpg.bind_item_font("SearchInput", title)

    button_search = dpg.add_button(label="Search!", pos=(890, 35), callback=search_movies)
    dpg.bind_item_theme(button_search, transparent_button_theme)
    dpg.bind_item_font(button_search, title)


    with dpg.child_window(tag="TopMovie_list", width=800, height=480, pos=(100, 180)):
        dpg.add_text("Results will appear here.") 
        top_movie()

    dpg.bind_item_theme("TopMovie_list", child_window_theme)

with dpg.window(label="Search", tag="Search UI", show=False):
    dpg.add_image(texture_id)
    dpg.add_text("Keyword", tag="filter_text", color=(255, 255, 255), pos=(370,110))
    dpg.bind_item_font("filter_text", keyword)

    headerGen = dpg.add_button(label="NEMORY", callback=lambda: switch_ui("Search UI", "Primary Window"), pos=(220, 45))
    dpg.bind_item_font(headerGen, header)
    dpg.bind_item_theme(headerGen, transparent_button_theme)

    with dpg.group(pos=(100, 170), width = 150, height = 100):
        dropdown_genre2 = dpg.add_combo(
            items=genres, 
            source=genre_selected,
            callback=on_select,
            user_data= "genre",
            default_value="Select Genre" 
        )
    dpg.bind_item_font(dropdown_genre2, buttonFont)
    dpg.bind_item_theme(dropdown_genre2, dropdown_theme)   

    with dpg.group(pos=(300, 170), width = 150, height = 100):
        dropdown_country2 = dpg.add_combo(
            items=countries, 
            source=country_selected,
            callback=on_select,
            user_data= "country",
            default_value="Select Country" 
        )
    dpg.bind_item_font(dropdown_country2, buttonFont)
    dpg.bind_item_theme(dropdown_country2, dropdown_theme) 

    with dpg.group(pos=(500, 170), width = 150, height = 100):
        dropdown_year2 = dpg.add_combo(
            items=year, 
            source=release_year_selected,
            callback=on_select,
            user_data= "year",
            default_value="Select Year" 
        )
    dpg.bind_item_font(dropdown_year2, buttonFont)
    dpg.bind_item_theme(dropdown_year2, dropdown_theme)  

    with dpg.group(pos=(700, 170), width = 150, height = 100):
        dropdown_sortby = dpg.add_combo(
            items= ["Popularity", "Rating", "Latest Movie"], 
            default_value="Sort by",
            source=sort_selected,
            callback=on_select,
            user_data= "other"
        )
    dpg.bind_item_font(dropdown_sortby, buttonFont)
    dpg.bind_item_theme(dropdown_sortby, dropdown_theme)  

    dpg.add_button(label="Find", tag = "btn_Find", callback=filter_movies, pos=(900,170))
    #center_text_in_window(1000, "filter_text", "Keyword", font_size=20)
    dpg.bind_item_theme("btn_Find", transparent_button_theme)
    dpg.bind_item_font("btn_Find", title)


    with dpg.child_window(tag="Movie_list", width=800, height=480, pos=(100, 230)):
        dpg.add_text("Results will appear here.") 
        # filter_movies()

    dpg.bind_item_theme("Movie_list", child_window_theme)

    dpg.add_input_text(tag="SearchInput1", hint="Input here...", pos=(450,40), width=420, height=40, multiline=True)
    dpg.bind_item_theme("SearchInput1", input_theme)
    dpg.bind_item_font("SearchInput1", title)

    button_search1 = dpg.add_button(label="Search!", pos=(890, 45), callback=search_movies1)
    dpg.bind_item_theme(button_search1, transparent_button_theme)
    dpg.bind_item_font(button_search1, title)

with dpg.window(label="Movie Details", tag="DetailUI", show=False):
    dpg.add_image(bgExtra)
    headerDetail = dpg.add_button(label="NEMORY", callback=lambda: switch_ui("DetailUI", "Primary Window"), pos=(50, 60))        
    dpg.bind_item_font(headerDetail, header)
    dpg.bind_item_theme(headerDetail, transparent_button_theme)

    with dpg.child_window(tag="DetailContent", width=800, height=480, pos=(100, 150)):
        dpg.add_text("Results will appear here.") 
    dpg.bind_item_theme("DetailContent", child_window_theme)
        
# Tạo viewport và hiển thị
dpg.create_viewport(title="Movie Retrieval Chatbot", width=1000, height=711)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()