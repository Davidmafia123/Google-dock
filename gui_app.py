import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GDA - Google Dorking Automation")
        self.geometry("900x700")

        # Set grid layout 1x1
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create tab view
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_view.add("Run")
        self.tab_view.add("Setup")

        # ============ Run Tab ============
        self.run_tab = self.tab_view.tab("Run")
        self.run_tab.grid_columnconfigure(0, weight=1)

        run_label = ctk.CTkLabel(
            self.run_tab,
            text="Run Tab\n\n(Content for Single/Batch Search will go here)",
            font=ctk.CTkFont(size=16)
        )
        run_label.grid(row=0, column=0, padx=20, pady=20)

        # ============ Setup Tab ============
        self.setup_tab = self.tab_view.tab("Setup")
        self.setup_tab.grid_columnconfigure(0, weight=1)

        setup_label = ctk.CTkLabel(
            self.setup_tab,
            text="Setup Tab\n\n(Content for Locations, Queries, Schedule, Export will go here)",
            font=ctk.CTkFont(size=16)
        )
        setup_label.grid(row=0, column=0, padx=20, pady=20)


if __name__ == "__main__":
    # Set appearance mode
    ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

    app = App()
    app.mainloop()
