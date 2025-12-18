import tkinter as tk
from PIL import Image, ImageTk

class Game:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.width = 800
        self.height = 600
        self.title_text = "Red Panda Game"

        self.player = self.Player()
        self.text_elements = []

        self.keys_pressed = set()

    def init(self):
        self.root = tk.Tk()
        self.root.title(self.title_text)
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

        # Keyboard bindings
        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)

        print("Game initialized")

    def title(self, text):
        self.title_text = text
        if self.root:
            self.root.title(text)
        print(f"Game title: {text}")

    def size(self, size_str):
        parts = size_str.replace(" ", "").split(',')
        self.width = int(parts[0].split('=')[1])
        self.height = int(parts[1].split('=')[1])
        if self.canvas:
            self.canvas.config(width=self.width, height=self.height)
        print(f"Game size: {self.width}x{self.height}")

    class Player:
        def __init__(self):
            self.sprite_path = None
            self.image = None
            self.pos = [400, 300]
            self.speed = 10  # movement speed

        def sprite(self, path):
            self.sprite_path = path
            try:
                img = Image.open(path)
                self.image = ImageTk.PhotoImage(img)
            except Exception as e:
                print("Error loading sprite:", e)
                self.image = None
            print(f"Player sprite: {path}")

        def move(self, direction, key=None):
            # Programmatic moves (like in .rpc)
            if direction == "up":
                self.pos[1] -= self.speed
            elif direction == "down":
                self.pos[1] += self.speed
            elif direction == "left":
                self.pos[0] -= self.speed
            elif direction == "right":
                self.pos[0] += self.speed

    def window_text(self, pos, text):
        self.text_elements.append((pos, str(text)))

    # Keyboard event handlers
    def _on_key_press(self, event):
        self.keys_pressed.add(event.keysym.lower())

    def _on_key_release(self, event):
        self.keys_pressed.discard(event.keysym.lower())

    def render(self):
        if not self.canvas:
            raise RuntimeError("Game not initialized!")

        # Main update loop
        def update():
            # Move player based on keys pressed
            if 'w' in self.keys_pressed:
                self.player.pos[1] -= self.player.speed
            if 's' in self.keys_pressed:
                self.player.pos[1] += self.player.speed
            if 'a' in self.keys_pressed:
                self.player.pos[0] -= self.player.speed
            if 'd' in self.keys_pressed:
                self.player.pos[0] += self.player.speed

            self.canvas.delete("all")  # clear canvas

            # Draw player
            if self.player.image:
                x, y = self.player.pos
                self.canvas.create_image(x, y, image=self.player.image, anchor="center")

            # Draw texts
            for t in self.text_elements:
                x, y = 10, 10  # only support "left, top"
                self.canvas.create_text(x, y, anchor="nw", text=t[1], fill="white", font=("Arial", 16))

            self.root.after(50, update)  # repeat ~20 FPS

        update()
        self.root.mainloop()
