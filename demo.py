import dearpygui.dearpygui as dpg

# Tạo context cho Dear PyGUI
dpg.create_context()

with dpg.font_registry():
    # Tải font từ file
    header = dpg.add_font("font/LithosPro-Regular.otf",40)  
    buttonFont = dpg.add_font("font/LithosPro-Regular.otf",13) 
    title = dpg.add_font("font/MAIAN.TTF",20)

with dpg.theme() as input_theme:
    with dpg.theme_component(dpg.mvInputText):  # Áp dụng cho tất cả InputText
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (100,102,155,200))

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

    button_search = dpg.add_button(label="Search!", pos=(760, 300), callback=lambda: print("Button clicked!"))
    dpg.bind_item_theme(button_search, transparent_button_theme)
    dpg.bind_item_font(button_search, title)

    dpg.add_input_text(tag="SearchInput", hint="Input here...", pos=(270,290), width=480, height=40, multiline=True)
    dpg.bind_item_theme("SearchInput", input_theme)


    
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

# Đặt cửa sổ chính
dpg.set_primary_window("Primary Window", True)

# Bắt đầu vòng lặp GUI
dpg.start_dearpygui()

# Dọn dẹp tài nguyên
dpg.destroy_context()
