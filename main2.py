import speech_recognition
import wave
import json
import os
import pyttsx3
from googletrans import Translator
import wikipedia
import ast
import dearpygui.dearpygui as dpg

class VoiceAssistant:
    """
    Parameters of assistant, including name, gender, language
    """
    name = ""
    gender = ""
    speech_language = ""
    recognition_language = ""


def setup_assistant_voice():
    """
    Default voice
    """
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            ttsEngine.setProperty("voice", voices[1].id)
        else:
            ttsEngine.setProperty("voice", voices[2].id)
    else:
        assistant.recognition_language = "ru-RU"
        ttsEngine.setProperty("voice", voices[0].id)


def play_voice_assistant_speech(text_to_speech):
    """
    Playing voice of assistant answers (without saving audio)
    :param text_to_speech: text, which we need convert to voice
    by Arsen
    """
    dpg.set_value("txt2", "Мой ответ: " + text_to_speech)
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()


def record_and_recognize_audio(*args: tuple):
    """
        Voice record and recognition
    """
    with microphone:
        recognized_data = ""

        # noise level regulation
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            dpg.set_value("stat", "Статус: Слушаю...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your mic is on?")
            dpg.set_value("stat", "Статус: Ошибка, звук не распознан")
            dpg.set_value("txt2", "Мой ответ: Можете ли вы проверить включен ли ваш микрофон?")
            return

        # using online recognition by Google
        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language=assistant.speech_language).lower()

        except speech_recognition.UnknownValueError:
            pass

        # In case if Internet access is not available
        # use offline recognition by Vosk
        except speech_recognition.RequestError:
            print("Trying to use offline recognition...")

        return recognized_data

def execute_command_with_name(command_name: str, *args: list):
    """
    User commands execution with additional arguments
    :param command_name: command name
    :param args: arguments, which will be transferred to function
    """
    for key in commands.keys():
        if command_name in key:
            commands[key](*args)
        else:
            pass  # print("Command not found")


def get_translation(arg: str):
    destination = None
    t_lang = ""
    if assistant.speech_language == "ru":
        t_lang = "Это переводится как "
    elif assistant.speech_language == "en":
        t_lang = "It's translates like "
    try:
        if type(arg) != str:
            arg = ''.join(arg)
        lang = translator.detect(arg)
        if "lang=ru" in lang:
            destination = "en"
        elif "lang=en" in lang:
            destination = "ru"
        # online translation by Google
        result = translator.translate(arg, dest=assistant.speech_language)
        play_voice_assistant_speech(t_lang + result.text)
        print(result.text)

    except:
        # in case if internet is unavailable. Using .txt file with words to translate
        file = open('wordbase.txt', encoding="utf8")
        f = file.read()
        result = ast.literal_eval(f)
        for i in result:
            if i[0] == arg:
                play_voice_assistant_speech(t_lang + i[1])
            elif i[1] == arg:
                play_voice_assistant_speech(t_lang + i[0])


def play_greetings(*args):
    if assistant.speech_language == "ru":
        play_voice_assistant_speech("Приветствую")
    else:
        play_voice_assistant_speech("Greetings master")


def play_farewell_and_quit(*args):
    if assistant.sex == "ru":
        play_voice_assistant_speech("Пока")
    else:
        play_voice_assistant_speech("Bye bye")

def search_for_definition_on_wikipedia(arg: str):
    try:
        result = wikipedia.summary(arg, sentences=2)
        play_voice_assistant_speech(result)
    except:
        dpg.set_value("stat", "Статус: Ошибка[x1wiki]")



def change_language(arg: str):
    if arg == ["русский"] or arg == ["russian"]:
        assistant.speech_language = "ru"
        setup_assistant_voice()
        play_voice_assistant_speech("Язык успешно изменён")
    elif arg == ["английский"] or arg == ["english"]:
        assistant.speech_language = "en"
        setup_assistant_voice()
        play_voice_assistant_speech("Language was successfully changed ")


commands = {
    ("hello", "hi", "morning", "привет"): play_greetings,
    ("bye", "goodbye", "quit", "exit", "stop", "пока"): play_farewell_and_quit,
    ("wikipedia", "definition", "about", "определение", "википедия"): search_for_definition_on_wikipedia,
    ("translate", "interpretation", "translation", "перевод", "перевести", "переведи"): get_translation,
    ("language", "язык"): change_language
}

if __name__ == "__main__":
    # initializing instruments of recognition and record
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    # initializing instrument of voice synthesis
    ttsEngine = pyttsx3.init()

    # tune assistant datas
    assistant = VoiceAssistant()
    assistant.name = "Alice"
    assistant.sex = "female"
    assistant.speech_language = "ru"
    wikipedia.set_lang("ru")

    # voice installations by default
    setup_assistant_voice()

    # google translator initialization
    translator = Translator()

    def callback():
        main_loop()
        dpg.set_value("stat", "Статус: ...")

    def callback2():
        value = dpg.get_value("input_text")
        value = value.encode("windows-1252")
        value = value.decode("cp1251")

        destination = None
        lang = str(translator.detect(value))
        if "lang=ru" in lang:
            destination = "en"
        elif "lang=en" in lang:
            destination = "ru"
        result = translator.translate(value, dest=destination)
        dpg.set_value("txt0", "Результат: " + result.text)

    def main_loop():
        dpg.set_item_label("btn1", "Обработка...")
        # Start of voice recording with output
        voice_input = record_and_recognize_audio()

        if os.path.exists("microphone-results.wav"):
            os.remove("microphone-results.wav")


        print(voice_input)
        try:
            dpg.set_value("txt1", "Вы сказали:" + voice_input)
        except:
            pass

        # separating commands from additional information (arguments)
        if voice_input:
            voice_input = voice_input.split(" ")
            command = voice_input[0]
            command_options = [str(input_part) for input_part in voice_input[1:len(voice_input)]]
            execute_command_with_name(command, command_options)
        dpg.set_item_label("btn1", "Нажмите чтоб говорить")

    def reset():
        assistant.name = "Alice"
        assistant.sex = "female"
        assistant.speech_language = "ru"
        wikipedia.set_lang("ru")
        setup_assistant_voice()
        if assistant.speech_language == "ru":
            play_voice_assistant_speech("Настройки ассистента были успешно сброшены")
        elif assistant.speech_language == "en":
            play_voice_assistant_speech("Settings of assistant was successfully reset")

    def change_language_call():
        if assistant.speech_language == "ru":
            assistant.speech_language = "en"
            wikipedia.set_lang("en")
            setup_assistant_voice()
            play_voice_assistant_speech("Language was successfully changed")
        elif assistant.speech_language == "en":
            assistant.speech_language = "ru"
            wikipedia.set_lang("ru")
            setup_assistant_voice()
            play_voice_assistant_speech("Язык был успешно изменён")

    # // Basic user interface //
    dpg.create_context()

    dpg.create_viewport(title='Arsenux', width=600, height=200)

    with dpg.font_registry():
            with dpg.font(r"fonts/cyrillic.ttf", 20, default_font=True, id="Default font"):
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    dpg.bind_font("Default font")

    with dpg.window(label="Settings", modal=True, show=False, id="settings_id", no_title_bar=True):
        dpg.add_separator()
        with dpg.group():
            dpg.add_button(label="Сбросить настройки ассистента", callback=reset)
            dpg.add_button(label="Изменить язык ассистента", callback=change_language_call)
            dpg.add_button(label="Закрыть окно", callback=lambda: dpg.configure_item("settings_id", show=False))

    with dpg.window(label="Help", modal=True, show=False, id="modal_id", no_title_bar=True):
        dpg.add_text("Арсен Даудов.\n+7 705 584 2794")
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("modal_id", show=False))

    with dpg.window(tag="Primary Window"):
        with dpg.group(horizontal=True):
            dpg.add_button(label="Настройки", callback=lambda: dpg.configure_item("settings_id", show=True))
            dpg.add_button(label="Помощь", callback=lambda: dpg.configure_item("modal_id", show=True))

        dpg.add_separator()
        dpg.add_text("Голосовое распознование")
        dpg.add_separator()
        dpg.add_button(label="Нажмите чтоб говорить", callback=callback, tag="btn1")
        dpg.add_input_text(label="Введите слово или предложение для перевода", tag="input_text", callback=callback2, on_enter=True)
        dpg.add_text(tag="txt0")
        dpg.add_separator()
        dpg.add_text("/// Информация отладки ")
        dpg.add_text("Статус:", tag="stat")
        dpg.add_text("Вы сказали:", tag="txt1")
        dpg.add_text("Мой ответ:", tag="txt2")
        dpg.add_separator()

    dpg.show_metrics()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()