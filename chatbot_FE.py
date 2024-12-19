import dearpygui.dearpygui as dpg
import chatbot_BE  # Import file chatbot.py

dpg.create_context()

chat_history = []

def send_message():
    global chat_history
    query = dpg.get_value("input_text")
    if query.strip() == "":
        return

    dpg.add_text(f"You: {query}", parent="chat_window", color=[255, 255, 255])
    dpg.set_value("input_text", "")

    response, elapsed_time = chatbot_BE.get_chatbot_response(query, chat_history)
    dpg.add_text(f"Chatbot: {response}", parent="chat_window", color=[100, 150, 255])
    # dpg.add_text(f"(Response generated in {elapsed_time:.2f} seconds)", parent="chat_window", color=[150, 150, 150])

    # Ask for feedback
    with dpg.group(horizontal=True, parent="chat_window"):
        dpg.add_text("Helpful?")
        dpg.add_button(label="Yes", user_data=(query, response, "yes"), callback=handle_feedback)
        dpg.add_button(label="No", user_data=(query, response, "no"), callback=handle_feedback)

def handle_feedback(sender, app_data, user_data):
    global chat_history
    query, response, feedback = user_data
    
    if feedback == "yes":
        dpg.add_text("Chatbot: Glad to hear that!", parent="chat_window", color=[100, 150, 255])
        chat_history.append((query, response))
    else:
        dpg.add_text("Chatbot: Could you please specify what information you're looking for?", parent="chat_window", color=[100, 150, 255])
        # Add an input field for clarification
        with dpg.group(horizontal=True, parent="chat_window", tag="clarification_input_group"):
            dpg.add_input_text(hint="Enter clarification here", tag="clarification_input")
            dpg.add_button(label="Send", callback=send_clarification, user_data=(query))

def send_clarification(sender, app_data, user_data):
    global chat_history
    query = user_data[0]
    clarification = dpg.get_value("clarification_input")
    dpg.set_value("clarification_input", "")
    dpg.delete_item("clarification_input_group")
    
    dpg.add_text(f"You: {clarification}", parent="chat_window", color=[255, 255, 255])
    response, elapsed_time = chatbot_BE.get_clarification_response(query, clarification, chat_history) # Using the new function
    dpg.add_text(f"Chatbot: {response}", parent="chat_window", color=[100, 150, 255])
    dpg.add_text(f"(Response generated in {elapsed_time:.2f} seconds)", parent="chat_window", color=[150, 150, 150])

    # Ask for feedback again
    with dpg.group(horizontal=True, parent="chat_window"):
        dpg.add_text("Helpful? Y/N")
        dpg.add_button(label="Yes", user_data=(query, response, "yes"), callback=handle_feedback)
        dpg.add_button(label="No", user_data=(query, response, "no"), callback=handle_feedback)

with dpg.theme() as input_theme:
    with dpg.theme_component(dpg.mvInputText):  
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))  
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (150, 150, 150, 255)) 
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (100,102,155,200))

with dpg.theme() as text_theme:
    with dpg.theme_component(dpg.mvText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))
with dpg.theme() as chatbot_text_theme:
    with dpg.theme_component(dpg.mvText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (100, 150, 255, 255))  # Màu xanh cho chatbot

with dpg.font_registry():
    default_font = dpg.add_font("font/arial.ttf", 16)

with dpg.window(label="Chatbot", tag="chatbot_window", width=500, height=400):
    dpg.add_child_window(tag="chat_window", autosize_x=True, height=320)

    with dpg.group(horizontal=True):
        dpg.add_input_text(hint="Enter your message here...", tag="input_text", on_enter=True, callback=send_message, width= -70)
        dpg.bind_item_theme("input_text", input_theme)
        dpg.add_button(label="Send", callback=send_message, width = 70)

    dpg.bind_font(default_font)

def run_gui():
    dpg.create_viewport(title="Movie Chatbot", width=520, height=450)
    dpg.setup_dearpygui()
    dpg.bind_theme(input_theme)
    dpg.bind_theme(text_theme)
    dpg.show_viewport()
    dpg.set_primary_window("chatbot_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    run_gui()