import dearpygui.dearpygui as dpg

# Tạo context cho Dear PyGUI
dpg.create_context()

with dpg.font_registry():
    # Tải font từ file
    header = dpg.add_font("font/LithosPro-Regular.otf",30)  # Thay đổi đường dẫn và kích thước font


def genre_menu_callback(sender, app_data, user_data):
    print(f"Selected Genre: {user_data}")  # `user_data` chứa tên thể loại

with dpg.texture_registry():
    width, height, channels, data = dpg.load_image("asset/Homepage.png")
    texture_id = dpg.add_static_texture(width, height, data)

with dpg.theme() as transparent_button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)  # Nền bình thường (trong suốt)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255, 30), category=dpg.mvThemeCat_Core)  # Hover (mờ nhẹ)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255, 50), category=dpg.mvThemeCat_Core)  # Khi nhấn (mờ hơn)


# Tạo cửa sổ giao diện chính
with dpg.window(label="Movie Retrieval Chatbot", tag="Primary Window"):
            
    dpg.draw_image(texture_id, (0, 0), (720, 512))
    
    dpg.draw_text((280, 20), "NEMORY", color=(255, 255, 255, 255), size=30, tag="custom_text")

    dpg.bind_item_font("custom_text", header)

    button_search = dpg.add_button(label="Search!", pos=(150, 120), callback=lambda: print("Button clicked!"))
    dpg.bind_item_theme(button_search, transparent_button_theme)

    with dpg.group(horizontal=True, horizontal_spacing=20, pos =(80, 60)):  # Dàn hàng ngang và cách 20 pixel
            for genre in ["Action", "Adventure", "Fantasy", "Science fiction", "Crime", "Drama", "Thriller"]:
                btn = dpg.add_button(label=genre, callback=genre_menu_callback, user_data=genre)
                dpg.bind_item_theme(btn, transparent_button_theme)  # Áp dụng theme

    with dpg.group(horizontal=True, horizontal_spacing=20, pos =(110, 80)):  # Dàn hàng ngang và cách 20 pixel
            for genre in ["Animation", "Family", "Western", "Comedy", "Romance", "Horror", "Mystery"]:
                btn = dpg.add_button(label=genre, callback=genre_menu_callback, user_data=genre)
                dpg.bind_item_theme(btn, transparent_button_theme)  # Áp dụng theme

    with dpg.group(horizontal=True, horizontal_spacing=20, pos =(160, 100)):  # Dàn hàng ngang và cách 20 pixel
            for genre in ["History", "War", "Music", "Documentary", "Foreign", "Tv movie"]:
                btn = dpg.add_button(label=genre, callback=genre_menu_callback, user_data=genre)
                dpg.bind_item_theme(btn, transparent_button_theme)  # Áp dụng theme


        #dpg.add_text("Tìm kiếm thông tin phim", color=[255, 255, 0])
        #dpg.add_spacing(count=2)

        #dpg.add_input_text(label="Tên phim", tag="Tên phim", hint="Nhập tên phim...")
        
        #dpg.add_spacing(count=2)
        #dpg.add_button(label="Tìm kiếm")
        #dpg.add_spacing(count=2)
        #dpg.add_text("Kết quả tìm kiếm:")
        #dpg.add_input_text(tag="Kết quả tìm kiếm", multiline=True, readonly=True, width=600, height=300)

# Tạo viewport và hiển thị
dpg.create_viewport(title="Movie Retrieval Chatbot", width=720, height=512)
dpg.setup_dearpygui()
dpg.show_viewport()

# Đặt cửa sổ chính
dpg.set_primary_window("Primary Window", True)

# Bắt đầu vòng lặp GUI
dpg.start_dearpygui()

# Dọn dẹp tài nguyên
dpg.destroy_context()
