import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.clock import Clock
from plyer import camera

IMAGE_MAPPING = [
    {"fim": "s.jpg", "text": "Good Morning Saab"},       
    {"fim": "k.jpg", "text": "Good Morning Kishore Bro"}, 
    {"fim": "p.jpg", "text": "Good Morning Prasad Bro"},     
    {"fim": "l.jpg", "text": "Good Morning Lincoln Bro"},
    {"fim": "h.jpg", "text": "Good Morning Hari Bro"},   
    {"fim": "v.jpg", "text": "Good Morning Venu Bro"}    
]

COLOR_PALETTE = {
    "Dark Blue": (0, 0, 0.54, 1),
    "Dark Red": (0.54, 0, 0, 1),
    "White": (1, 1, 1, 1),
    "Dark Yellow": (0.6, 0.5, 0, 1),
    "Dark Orange": (0.8, 0.3, 0, 1),
    "Dark Pink": (0.6, 0, 0.4, 1),
    "Dark Green": (0, 0.39, 0, 1),
    "Dark Gold": (0.72, 0.53, 0.04, 1)
}

class MobileGreetingApp(FloatLayout):
    def __init__(self, **kwargs):
        super(MobileGreetingApp, self).__init__(**kwargs)
        
        self.bg_path = "default_bg.jpg" # Fallback base background template
        
        # 1. Background Visual Shell
        self.background = Image(source=self.bg_path, size_hint=(None, None), size=(400, 400), pos_hint={'center_x': 0.5, 'center_y': 0.6})
        self.add_widget(self.background)
        
        # 2. Camera Trigger Button
        self.cam_btn = Button(text="Capture BG from Camera", size_hint=(0.6, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.22})
        self.cam_btn.bind(on_release=self.capture_background)
        self.add_widget(self.cam_btn)
        
        # 3. Text Color Selection Spinner (Dropdown Menu)
        self.color_spinner = Spinner(
            text='Select Text Color',
            values=list(COLOR_PALETTE.keys()),
            size_hint=(0.6, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.12}
        )
        self.color_spinner.bind(text=self.on_color_change)
        self.add_widget(self.color_spinner)
        
        # Core configuration handles
        self.current_color = (1, 1, 1, 1)
        self.dim_source = 'r.jpg'
        
        self.cards = []
        self.setup_sliding_elements()
        
        self.current_index = 0
        self.cards[0]["status"] = "active"
        self.scroll_speed = 0.375 
        
        Clock.schedule_interval(self.animate_scroll, 1/60.0)

    def capture_background(self, instance):
        """Leverages plyer API wrapper layer to call native hardware camera."""
        self.bg_path = os.path.join(App.get_running_app().user_data_dir, "captured_bg.jpg")
        try:
            camera.take_picture(filename=self.bg_path, on_complete=self.on_camera_complete)
        except NotImplementedError:
            print("Camera feature only functions natively inside compiled APK installations.")

    def on_camera_complete(self, filename):
        if os.path.exists(filename):
            self.background.source = filename
            self.background.reload()

    def on_color_change(self, spinner, text):
        self.current_color = COLOR_PALETTE.get(text, (1, 1, 1, 1))
        for card in self.cards:
            card["label"].color = self.current_color

    def setup_sliding_elements(self):
        for item in IMAGE_MAPPING:
            dim_img = Image(source=self.dim_source, size_hint=(None, None), size=(85, 85))
            fim_img = Image(source=item["fim"], size_hint=(None, None), size=(85, 85))
            
            lbl = Label(
                text=item["text"], 
                font_size=32, # 160% Scale configuration sizing
                color=self.current_color,
                size_hint=(None, None),
                size=(350, 50),
                halign="center"
            )
            
            # Start offscreen left boundaries
            dim_img.x = -400
            fim_img.x = -400
            lbl.x = -400
            
            # Absolute Y alignments inside relative parent bounds
            dim_img.y = self.background.y + 280
            lbl.y = self.background.y + 185
            fim_img.y = self.background.y + 40
            
            self.add_widget(dim_img)
            self.add_widget(lbl)
            self.add_widget(fim_img)
            
            self.cards.append({"dim": dim_img, "fim": fim_img, "label": lbl, "status": "waiting"})

    def animate_scroll(self, dt):
        if self.current_index >= len(self.cards):
            self.current_index = 0
            for card in self.cards: card["status"] = "waiting"
            self.cards[0]["status"] = "active"
            return

        card = self.cards[self.current_index]
        target_img_x = self.background.x + (400 - 85) / 2
        target_lbl_x = self.background.x + (400 - 350) / 2

        if card["status"] == "active":
            if card["dim"].x < target_img_x:
                card["dim"].x += self.scroll_speed
                card["label"].x += self.scroll_speed
                card["fim"].x += self.scroll_speed
            else:
                card["status"] = "exiting"
        elif card["status"] == "exiting":
            if card["dim"].x < self.background.x + 420:
                card["dim"].x += self.scroll_speed
                card["label"].x += self.scroll_speed
                card["fim"].x += self.scroll_speed
            else:
                card["dim"].x, card["label"].x, card["fim"].x = -400, -400, -400
                card["status"] = "done"
                self.current_index += 1
                if self.current_index < len(self.cards):
                    self.cards[self.current_index]["status"] = "active"

class MainApp(App):
    def build(self):
        return MobileGreetingApp()

if __name__ == '__main__':
    MainApp().run()
