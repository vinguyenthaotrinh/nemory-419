from gpt4all import GPT4All

MODEL_DOWNLOAD = "orca-mini-3b-gguf2-q4_0.gguf"
MODEL_PATH_CACHE = "model_gpt"

print("Starting model...")
# --- Khởi tạo model GPT4All ---
model = GPT4All(model_name=MODEL_DOWNLOAD, model_path=MODEL_PATH_CACHE, verbose=True, device='cpu')
print("Done init model. ")

system_template = 'A chat between a curious user and an artificial intelligence assistant.\n'
# many models use triple hash '###' for keywords, Vicunas are simpler:
prompt_template = 'USER: {0}\nASSISTANT: '
with model.chat_session(system_template, prompt_template):
    response1 = model.generate('why is the grass green?')
    print(response1)
    print()
    response2 = model.generate('tell me about Avatar movie')
    print(response2)