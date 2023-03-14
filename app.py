import json
import re
import tkinter

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from keybert import KeyBERT
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import instagram_scrapper.main as scrapper
import threading
import customtkinter


class Settings(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)


class Main(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Text
        self.doc = ""
        self.n_top = 5
        self.n_post = 5

        # Model
        self.key_output = []
        self.kw_model = KeyBERT()

        # GUI
        self.title("Keybertaurus Rex")
        self.geometry("700x450")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        # create 2x2 grid system
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="Keybertaurus Rex",
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_large_image_label = customtkinter.CTkLabel(self.navigation_frame, text="Input Instagram Username")
        self.home_frame_large_image_label.grid(row=1, column=0, padx=20, pady=10)

        self.text_input = customtkinter.CTkTextbox(self.navigation_frame, height=20)
        self.text_input.grid(row=2, column=0, sticky="nsew")

        self.n_top_label = customtkinter.CTkLabel(self.navigation_frame, text=f'N-Top : {self.n_top}')
        self.n_top_label.grid(row=3, column=0, padx=20, pady=10)

        self.slider = customtkinter.CTkSlider(self.navigation_frame, from_=0, to=10, command=self.n_top_event)
        self.slider.place(relx=0.5, rely=0.45, anchor=tkinter.CENTER)

        self.n_post_label = customtkinter.CTkLabel(self.navigation_frame, text=f'N-Post : {self.n_post}')
        self.n_post_label.grid(row=4, column=0, padx=20, pady=10)

        self.slider = customtkinter.CTkSlider(self.navigation_frame, from_=0, to=10, command=self.n_post_event)
        self.slider.place(relx=0.5, rely=0.75, anchor=tkinter.CENTER)

        self.home_frame_button_1 = customtkinter.CTkButton(self.navigation_frame, text="Generate Keywords",
                                                           command=self.button_callback)
        self.home_frame_button_1.grid(row=5, column=0, padx=20, pady=10)

        self.home_label = customtkinter.CTkLabel(self.home_frame, text="Generated Keywords")
        self.home_label.grid(row=0, column=0, padx=20, pady=10)

        self.home_frame.grid(row=0, column=1, sticky="nsew")

    def n_top_event(self, value):
        self.n_top = int(value)
        self.n_top_label = customtkinter.CTkLabel(self.navigation_frame, text=f'N-Top : {self.n_top}')
        self.n_top_label.grid(row=3, column=0, padx=20, pady=10)

    def n_post_event(self, value):
        self.n_post = int(value)
        self.n_post_label = customtkinter.CTkLabel(self.navigation_frame, text=f'N-Post : {self.n_post}')
        self.n_post_label.grid(row=3, column=0, padx=20, pady=10)

    # add methods to app
    def button_callback(self):

        # Thread
        account_name = self.text_input.get("1.0", "end-1c")
        scrapperThread = threading.Thread(target=scrapper.Scrapper(account_name, self.n_post))
        scrapperThread.start()

        # Input

        # self.doc = self.join_comments(account_name)
        self.doc = "Sudah nyobain yang rasa story berry romancheese 2 enakkk bangettt + topping cincau sea salt cream, Enak banget barusan gw coba rasanya melting banget, Roman cheese enak bangettt kayk rasa cheese cake, Min Terlalu Enak Min Jadi Ketagihan,"

        # Pre-Processing
        self.doc = self.doc.lower()
        self.doc = self.doc.replace(",", ".")

        regex_pattern = r'\B(#|@)\w+|[^\w\s,.]'
        self.doc = re.sub(regex_pattern, '', self.doc)
        self.remove_duplicates()

        factory = StopWordRemoverFactory()
        stop_word_remover = factory.create_stop_word_remover()
        stop_word_remover.remove(self.doc)

        factory = StemmerFactory()
        stemming = factory.create_stemmer()
        self.doc = stemming.stem(self.doc)

        # Model Extraction
        keywords = self.kw_model.extract_keywords(docs=self.doc, keyphrase_ngram_range=(2, 2),
                                                  stop_words=['yang', 'yg'], top_n=self.n_top)

        # GUI
        self.delete_output()
        for item, value in sorted(keywords, key=lambda x: x[1], reverse=True):
            self.key_output.append(customtkinter.CTkButton(self.home_frame, text=f'{item}',
                                                           font=customtkinter.CTkFont(family="Century Gothic", size=12,
                                                                                      weight="bold")))
        self.draw_output()

    def remove_duplicates(self):
        result = ''
        prev_char = ''

        for char in self.doc:
            if char != prev_char:
                result += char
            prev_char = char

        self.doc = result

    def draw_output(self):
        i = 1
        for key in self.key_output:
            key.configure(state="disabled", fg_color="#DDF7E3", text_color="#DF2E38")
            key.grid(row=i, column=0, padx=20, pady=(20, 0))
            i += 1

    def delete_output(self):
        for key in self.key_output:
            key.destroy()

        self.key_output = []

    def join_comments(self, username):
        import time
        time.sleep(2)
        # Open the JSON file
        with open("data/" + username + ".json", 'r') as f:
            # Decode the JSON data
            data = json.load(f)

        strs = []
        for posts in data["posts"]:
            for comments in posts["comments"]:
                strs.append(comments["text"])
                # for replies in comments["replies"]:
                #     strs.append(replies["text"])

        return ', '.join(strs)


if __name__ == '__main__':
    main = Main()
    main.mainloop()
