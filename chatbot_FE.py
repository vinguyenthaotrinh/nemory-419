import dearpygui.dearpygui as dpg
import chatbot_BE  # Import file chatbot.py

dpg.create_context()

chat_history = []

def send_message():
    global chat_history
    query_data = dpg.get_item_user_data("input_text")
    clarification_mode = False
    original_query = ""

    if query_data is not None:
        original_query, clarification_mode = query_data

    query = dpg.get_value("input_text")
    if query.strip() == "":
        return

    if clarification_mode:
        dpg.add_text(f"You (Clarification): {query}", parent="chat_window", color=[255, 255, 255])
        response, elapsed_time = chatbot_BE.get_clarification_response(original_query, query, chat_history)
        dpg.set_item_user_data("input_text", None)
        dpg.configure_item("input_text", hint="Enter your message here...")
    else:
        dpg.add_text(f"You: {query}", parent="chat_window", color=[255, 255, 255])
        response, elapsed_time = chatbot_BE.get_chatbot_response(query, chat_history)

    dpg.set_value("input_text", "")
    dpg.add_text(f"Chatbot: {response}", parent="chat_window", color=[100, 150, 255])
    dpg.add_text(f"(Response generated in {elapsed_time:.2f} seconds)", parent="chat_window", color=[150, 150, 150])

    # Ask for feedback
    with dpg.group(horizontal=True, parent="chat_window"):
        dpg.add_text("Helpful?")
        dpg.add_button(label="Yes", user_data=(query if not clarification_mode else original_query, response, "yes"), callback=handle_feedback)
        dpg.add_button(label="No", user_data=(query if not clarification_mode else original_query, response, "no"), callback=handle_feedback)

def handle_feedback(sender, app_data, user_data):
    global chat_history
    query, response, feedback = user_data

    # Disable both Yes/No buttons and highlight the chosen one
    dpg.configure_item(sender, enabled=False)  # Disable the button that was clicked
    # Find the other button and disable it
    if feedback == "yes":
        dpg.configure_item(sender + 1, enabled=False) # Assuming 'No' button is the next item
        dpg.set_value(sender - 1, "Helpful? [Yes]") # Set text to indicate 'Yes' was chosen
    else:
        dpg.configure_item(sender - 1, enabled=False)  # Assuming 'Yes' button is the previous item
        dpg.set_value(sender - 2, "Helpful? [No]") # Set text to indicate 'No' was chosen

    if feedback == "yes":
        dpg.add_text("Chatbot: Glad to hear that!", parent="chat_window", color=[100, 150, 255])
        chat_history.append((query, response))
    else:
        dpg.add_text(
            "Chatbot: Could you please specify what information you're looking for?",
            parent="chat_window",
            color=[100, 150, 255],
        )
        # Update the send_message function to handle clarification
        dpg.set_item_user_data("input_text", (query, True))  # Mark that next input is a clarification
        dpg.configure_item("input_text", hint="Enter your clarification here...")

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
    dpg.create_viewport(title="Movie Chatbot", width=520, height=480)
    dpg.setup_dearpygui()
    dpg.bind_theme(input_theme)
    dpg.bind_theme(text_theme)
    dpg.show_viewport()
    dpg.set_primary_window("chatbot_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    run_gui()