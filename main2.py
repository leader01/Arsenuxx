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
    dpg.set_value("txt2", "Bot said: " + text_to_speech)
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
            dpg.set_value("stat", "Bot status: Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your mic is on?")
            dpg.set_value("stat", "Bot status: Didn't hear anything")
            dpg.set_value("txt2", "Bot said: Can you check if your mic is on?")
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
        play_voice_assistant_speech("Это переводится как " + result.text)
        print(result.text)

    except:
        # in case if internet is unavailable. Using .txt file with words to translate
        file = open('wordbase.txt', encoding="utf8")
        f = file.read()
        result = ast.literal_eval(f)
        for i in result:
            if i[0] == arg:
                play_voice_assistant_speech("Это переводится как " + i[1])
            elif i[1] == arg:
                play_voice_assistant_speech("Это переводится как " + i[0])


def play_greetings(*args):
    play_voice_assistant_speech("Приветствую")


def play_farewell_and_quit(*args):
    play_voice_assistant_speech("Пока")

def search_for_definition_on_wikipedia(arg: str):
    try:
        result = wikipedia.summary(arg, sentences=2)
        play_voice_assistant_speech(result)
    except:
        dpg.set_value("stat", "Bot status: Error")



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
        dpg.set_value("stat", "Bot status: ...")

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
        dpg.set_value("txt0", "Result: " + result.text)

    def main_loop():
        dpg.set_item_label("btn1", "Listening...")
        # Start of voice recording with output
        voice_input = record_and_recognize_audio()

        if os.path.exists("microphone-results.wav"):
            os.remove("microphone-results.wav")


        print(voice_input)
        try:
            dpg.set_value("txt1", "You said: " + voice_input)
        except:
            pass

        # separating commands from additional information (arguments)
        if voice_input:
            voice_input = voice_input.split(" ")
            command = voice_input[0]
            command_options = [str(input_part) for input_part in voice_input[1:len(voice_input)]]
            execute_command_with_name(command, command_options)
        dpg.set_item_label("btn1", "Press to speak")


    # // Basic user interface //
    dpg.create_context()

    dpg.create_viewport(title='Arsenux', width=600, height=200)

    with dpg.font_registry():
            with dpg.font(r"fonts\timesetx-rus.ttf", 13, default_font=True, id="Default font"):
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    dpg.bind_font("Default font")

    with dpg.window(tag="Primary Window"):
        dpg.add_text("Speaking recognition by Arsen")
        dpg.add_separator()
        dpg.add_button(label="Press to speak", callback=callback, tag="btn1")
        dpg.add_input_text(label="Enter word for translation", tag="input_text", callback=callback2, on_enter=True)
        dpg.add_text(tag="txt0")
        dpg.add_separator()
        dpg.add_text("/// Execution info ")
        dpg.add_text("Bot status:", tag="stat")
        dpg.add_text("You said:", tag="txt1")
        dpg.add_text("Bot said:", tag="txt2")
        dpg.add_separator()

    dpg.show_metrics()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()