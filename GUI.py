import dearpygui.dearpygui as dpg
import find_by_genre as fbg
import all_field as search
import json


# Tạo context cho Dear PyGUI
dpg.create_context()

def genre_menu_callback(sender, app_data, user_data):
    genre = user_data
    movies = fbg.find_top_movies_by_genre(genre.lower())  # Gọi hàm lấy danh sách phim
    dpg.delete_item("results_list", children_only=True)  # Xóa kết quả cũ
    
    if movies:
        for movie in movies:
            dpg.add_text(f"{movie['title']}      {movie['vote_average']}", parent="results_list")  # Chỉ hiển thị tên phim
    else:
        dpg.add_text(f"Không tìm thấy phim nào trong thể loại '{genre}'", parent="results_list")

def search_movies(sender, app_data, user_data):
        # Lấy nội dung tìm kiếm từ ô input
    user_query = dpg.get_value("SearchInput")
    
    if not user_query.strip():
        print("Please enter a search query.")
        return

    # Gọi hàm search và nhận kết quả
    top_movies = search(user_query)

    # Hiển thị kết quả lên giao diện
    with dpg.window(label="Search Results", width=600, height=400, pos=(270, 350), tag="SearchResults"):
        if top_movies.empty:
            dpg.add_text("No results found.")
        else:
            for _, row in top_movies.iterrows():
                # Thêm thông tin phim vào giao diện
                dpg.add_text(f"Title: {row['title']}")
                dpg.add_text(f"Overview: {row['overview']}")
                dpg.add_text(f"Release Date: {row['release_date']}")

                try:
                    keywords_data = json.loads(row['keywords']) if row['keywords'] else []
                    keyword_names = [keyword['name'] for keyword in keywords_data]
                    dpg.add_text(f"Keywords: {', '.join(keyword_names) if keyword_names else 'None'}")
                except json.JSONDecodeError:
                    dpg.add_text("Keywords: Invalid format")
                
                try:
                    genres_data = json.loads(row['genres']) if row['genres'] else []
                    genre_names = [genre['name'] for genre in genres_data]
                    dpg.add_text(f"Genres: {', '.join(genre_names) if genre_names else 'None'}")
                except json.JSONDecodeError:
                    dpg.add_text("Genres: Invalid format")
                
                try:
                    cast_data = json.loads(row['cast']) if row['cast'] else []
                    cast_names = [cast['name'] for cast in cast_data[:5]]  # Top 5 diễn viên
                    dpg.add_text(f"Cast: {', '.join(cast_names) if cast_names else 'None'}")
                except json.JSONDecodeError:
                    dpg.add_text("Cast: Invalid format")

                dpg.add_separator()
    

with dpg.font_registry():
    # Tải font từ file
    header = dpg.add_font("font/LithosPro-Regular.otf",40)  
    buttonFont = dpg.add_font("font/LithosPro-Regular.otf",13) 
    title = dpg.add_font("font/MAIAN.TTF",20)

with dpg.theme() as input_theme:
    with dpg.theme_component(dpg.mvInputText):  # Áp dụng cho tất cả InputText
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (100,102,155,200))

with dpg.texture_registry():
    width, height, channels, data = dpg.load_image("asset/Homepage.png")
    texture_id = dpg.add_static_texture(width, height, data)

with dpg.theme() as transparent_button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)  # Nền bình thường (trong suốt)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255, 30), category=dpg.mvThemeCat_Core)  # Hover
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255, 50), category=dpg.mvThemeCat_Core)  # Khi nhấn

with dpg.window(label="Movie Retrieval Chatbot", tag="Primary Window"):
    dpg.add_image(texture_id)
    dpg.draw_text((400, 20), "NEMORY", color=(255, 255, 255, 255), size=40, tag="custom_text")
    dpg.bind_item_font("custom_text", header)

    dpg.draw_text((260, 220), "No matter what you remember about the movie, \nyou can use it to search.", color=(255, 255, 255, 255), size=20, tag="header1")
    dpg.bind_item_font("header1", title)
    
    with dpg.group(horizontal=True, horizontal_spacing=20, pos =(210, 80)):  # Dàn hàng ngang và cách 20 pixel
            for genre in ["Action", "Adventure", "Fantasy", "Science fiction", "Crime", "Drama", "Thriller"]:
                btn = dpg.add_button(label=genre, callback=genre_menu_callback, user_data=genre)
                dpg.bind_item_font(btn, buttonFont)
                dpg.bind_item_theme(btn, transparent_button_theme)  # Áp dụng theme

    with dpg.group(horizontal=True, horizontal_spacing=20, pos=(210, 80)):
        for genre in ["Action", "Adventure", "Fantasy", "Science fiction", "Crime", "Drama", "Thriller"]:
            btn = dpg.add_button(label=genre, callback=genre_menu_callback, user_data=genre)
            dpg.bind_item_font(btn, buttonFont)
            dpg.bind_item_theme(btn, transparent_button_theme)
    with dpg.group(horizontal=True, horizontal_spacing=20, pos =(220, 110)):  # Dàn hàng ngang và cách 20 pixel
        for genre in ["Animation", "Family", "Western", "Comedy", "Romance", "Horror", "Mystery"]:
            btn = dpg.add_button(label=genre, callback=genre_menu_callback, user_data=genre)
            dpg.bind_item_font(btn, buttonFont)
            dpg.bind_item_theme(btn, transparent_button_theme)  

    with dpg.group(horizontal=True, horizontal_spacing=20, pos =(260, 140)):  # Dàn hàng ngang và cách 20 pixel
        for genre in ["History", "War", "Music", "Documentary", "Foreign", "Tv movie"]:
            btn = dpg.add_button(label=genre, callback=genre_menu_callback, user_data=genre)
            dpg.bind_item_font(btn, buttonFont)
            dpg.bind_item_theme(btn, transparent_button_theme) 

    # # Khu vực hiển thị kết quả
    # dpg.add_text("Kết quả tìm kiếm:", pos=(150, 200))
    # with dpg.group(tag="results_list", pos=(150, 230)):
    #     pass  # Đây là nơi thêm kết quả

# Tạo viewport

    dpg.add_input_text(tag="SearchInput", hint="Input here...", pos=(270,290), width=480, height=40, multiline=True)
    dpg.bind_item_theme("SearchInput", input_theme)

    button_search = dpg.add_button(label="Search!", pos=(760, 300), callback=search_movies)
    dpg.bind_item_theme(button_search, transparent_button_theme)
    dpg.bind_item_font(button_search, title)

    
        #dpg.add_spacing(count=2)        
        #dpg.add_spacing(count=2)
        #dpg.add_button(label="Tìm kiếm")
        #dpg.add_spacing(count=2)
        #dpg.add_text("Kết quả tìm kiếm:")
        #dpg.add_input_text(tag="Kết quả tìm kiếm", multiline=True, readonly=True, width=600, height=300)

# Tạo viewport và hiển thị
dpg.create_viewport(title="Movie Retrieval Chatbot", width=1000, height=711)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()