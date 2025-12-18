import customtkinter as ctk

class zButton(ctk.CTkButton):
    def __init__(
            self,
            master,
            width = 140,
            height = 28,
            corner_radius = None,
            border_width = None,
            border_spacing = 2,
            bg_color = "transparent",
            fg_color = "#000000",
            hover_color = "#111111",
            border_color = None,
            text_color = None,
            text_color_disabled = None,
            background_corner_colors = None,
            round_width_to_even_numbers = True,
            round_height_to_even_numbers = True,
            text = "CTkButton",
            font = None,
            textvariable = None,
            image = None,
            state = "normal",
            hover = True,
            command = None,
            compound = "left",
            anchor = "center",
            **kwargs
        ):

        super().__init__(master, width, height, corner_radius, border_width, border_spacing, bg_color, fg_color, hover_color, border_color, text_color, text_color_disabled, background_corner_colors, round_width_to_even_numbers, round_height_to_even_numbers, text, font, textvariable, image, state, hover, command, compound, anchor, **kwargs)





def print_text():
    print("something happened")

if __name__ == "__main__":
    app = ctk.CTk()

    button = zButton(master = app, command = print_text)
    button.pack()
    
    app.mainloop()
