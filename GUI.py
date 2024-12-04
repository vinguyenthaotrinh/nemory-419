import dearpygui.dearpygui as dpg
import find_by_genre as fbg

# Tạo context cho Dear PyGUI
dpg.create_context()

with dpg.font_registry():
    header = dpg.add_font("font/LithosPro-Regular.otf", 40)  
    buttonFont = dpg.add_font("font/LithosPro-Regular.otf", 13)

def genre_menu_callback(sender, app_data, user_data):
    genre = user_data
    movies = fbg.find_top_movies_by_genre(genre.lower())  # Gọi hàm lấy danh sách phim
    dpg.delete_item("results_list", children_only=True)  # Xóa kết quả cũ
    
    if movies:
        for movie in movies:
            dpg.add_text(f"{movie['title']}", parent="results_list")  # Chỉ hiển thị tên phim
    else:
        dpg.add_text(f"Không tìm thấy phim nào trong thể loại '{genre}'", parent="results_list")

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

    # Khu vực hiển thị kết quả
    dpg.add_text("Kết quả tìm kiếm:", pos=(150, 200))
    with dpg.group(tag="results_list", pos=(150, 230)):
        pass  # Đây là nơi thêm kết quả

# Tạo viewport
dpg.create_viewport(title="Movie Retrieval Chatbot", width=1000, height=711)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()