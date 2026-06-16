import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Color, Ellipse, StencilPush, StencilUse, StencilUnUse, StencilPop

# Request permissions on Android runtime dynamically
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

IMAGE_MAPPING = [
    {"fim": "s.jpg", "text": "Good Morning Saab", "filename": "greeting_saab.gif"},       
    {"fim": "k.jpg", "text": "Good Morning Kishore Bro", "filename": "greeting_kishore.gif"}, 
    {"fim": "p.jpg", "text": "Good Morning Prasad Bro", "filename": "greeting_prasad.gif"},     
    {"fim": "l.jpg", "text": "Good Morning Lincoln Bro", "filename": "greeting_lincoln.gif"},
    {"fim": "h.jpg", "text": "Good Morning Hari Bro", "filename": "greeting_hari.gif"},   
    {"fim": "v.jpg", "text": "Good Morning Venu Bro", "filename": "greeting_venu.gif"}    
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

class RoundImage(Image):
    """Custom Kivy Widget that dynamically clips any image into a transparent circle."""
    def __init__(self, **kwargs):
        super(RoundImage, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Mask everything outside the circle radius out using stencil buffers
            StencilPush()
            Color(1, 1, 1, 1)
            Ellipse(pos=self.pos, size=self.size)
            StencilUse()
            
            # Draw the original source image inside the transparent circle shield boundary
            Image(source=self.source, pos=self.pos, size=self.size).canvas.draw()
            
            StencilUnUse()
            Ellipse(pos=self.pos, size=self.size)
            StencilPop()


class MobileGreetingApp(FloatLayout):
    def __init__(self, **kwargs):
        super(MobileGreetingApp, self).__init__(**kwargs)
        
        # Determine the safe storage path for saving the GIFs on Android
        if platform == 'android':
            # Saves directly to your phone's main storage "Download" folder
            self.export_path = "/sdcard/Download/Greeting_GIFs/"
            self.bg_path = "default_bg.jpg"
        else:
            self.export_path = "./Greeting_GIFs/"
            self.bg_path = "default_bg.jpg"

        if not os.path.exists(self.export_path):
            os.makedirs(self.export_path)

        # 1. Background Shell (Now a round clip)
        self.background = RoundImage(source=self.bg_path, size_hint=(None, None), size=(400, 400), pos_hint={'center_x': 0.5, 'center_y': 0.6})
        self.add_widget(self.background)
        
        # 2. Camera Trigger Button
        self.cam_btn = Button(text="Capture BG from Camera", size_hint=(0.7, 0.07), pos_hint={'center_x': 0.5, 'center_y': 0.24})
        self.cam_btn.bind(on_release=self.capture_background)
        self.add_widget(self.cam_btn)
        
        # 3. Spinner Dropdown Menu for text color
        self.color_spinner = Spinner(
            text='Select Text Color',
            values=list(COLOR_PALETTE.keys()),
            size_hint=(0.7, 0.07),
            pos_hint={'center_x': 0.5, 'center_y': 0.16}
        )
        self.color_spinner.bind(text=self.on_color_change)
        self.add_widget(self.color_spinner)

        # 4. Save GIFs Button
        self.gif_btn = Button(text="Save 6 GIFs to Downloads", size_hint=(0.7, 0.07), pos_hint={'center_x': 0.5, 'center_y': 0.08}, background_color=(0, 0.6, 0, 1))
        self.gif_btn.bind(on_release=self.generate_and_save_gifs)
        self.add_widget(self.gif_btn)
        
        self.current_color = (1, 1, 1, 1)
        self.cards = []
        self.setup_sliding_elements()
        
        self.current_index = 0
        self.cards[0]["status"] = "active"
        self.scroll_speed = 0.375 
        
        Clock.schedule_interval(self.animate_scroll, 1/60.0)

    def capture_background(self, instance):
        from plyer import camera
        # Cache image inside the app sandbox folder safely to avoid system lockouts
        target_file = os.path.join(App.get_running_app().user_data_dir, "captured_bg.jpg")
        try:
            camera.take_picture(filename=target_file, on_complete=self.on_camera_complete)
        except Exception as e:
            print(f"Camera Error: {e}")

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
            # FIX: Use our new RoundImage widget layout to strip out background rectangles dynamically
            dim_img = RoundImage(source='r.jpg', size_hint=(None, None), size=(85, 85))
            fim_img = RoundImage(source=item["fim"], size_hint=(None, None), size=(85, 85))
            
            lbl = Label(
                text=item["text"], 
                font_size=32, 
                color=self.current_color,
                size_hint=(None, None),
                size=(350, 50),
                halign="center"
            )
            
            dim_img.x = -400
            fim_img.x = -400
            lbl.x = -400
            
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

    def generate_and_save_gifs(self, instance):
        """Uses local Pillow package to render the frames and export the files to storage."""
        from PIL import Image as PILImage, ImageDraw, ImageFont
        
        # Load active backgrounds
        bg_src = self.background.source if os.path.exists(self.background.source) else "default_bg.jpg"
        
        def process_circle(img_path, size=(85, 85)):
            if not os.path.exists(img_path):
                im = PILImage.new("RGBA", size, (100, 100, 100, 255))
            else:
                im = PILImage.open(img_path).convert("RGBA")
            # Clear out white pixels
            datas = im.getdata()
            newData = []
            for pixel in datas:
                if pixel[0] >= 240 and pixel[1] >= 240 and pixel[2] >= 240:
                    newData.append((0, 0, 0, 0))
                else:
                    newData.append(pixel)
            im.putdata(newData)
            im = im.resize(size, PILImage.Resampling.LANCZOS)
            mask = PILImage.new("L", size, 0)
            ImageDraw.Draw(mask).ellipse((0, 0) + size, fill=255)
            out = PILImage.new("RGBA", size, (0, 0, 0, 0))
            out.paste(im, (0, 0), mask=mask)
            return out

        bg_circle = process_circle(bg_src, size=(400, 400))
        dim_circle = process_circle('r.jpg', size=(85, 85))

        # Color calculation conversion mapping
        c = self.current_color
        rgb_color = (int(c[0]*255), int(c[1]*255), int(c[2]*255))

        for item in IMAGE_MAPPING:
            fim_circle = process_circle(item["fim"], size=(85, 85))
            frames = []
            
            for cx in range(-280, 158, 6): # Fast render step pace
                frame = PILImage.new("RGBA", (400, 400), (0, 0, 0, 0))
                frame.paste(bg_circle, (0, 0), bg_circle)
                frame.paste(dim_circle, (cx, 40), dim_circle)
                frame.paste(fim_circle, (cx, 275), fim_circle)
                
                draw = ImageDraw.Draw(frame)
                draw.text((cx - 70, 185), item["text"], fill=rgb_color)
                frames.append(frame)

            for cx in range(157, 421, 6):
                frame = PILImage.new("RGBA", (400, 400), (0, 0, 0, 0))
                frame.paste(bg_circle, (0, 0), bg_circle)
                frame.paste(dim_circle, (cx, 40), dim_circle)
                frame.paste(fim_circle, (cx, 275), fim_circle)
                
                draw = ImageDraw.Draw(frame)
                draw.text((cx - 70, 185), item["text"], fill=rgb_color)
                frames.append(frame)

            dest_file = os.path.join(self.export_path, item["filename"])
            frames[0].save(dest_file, save_all=True, append_images=frames[1:], duration=40, loop=0, disposal=2)
        
        self.gif_btn.text = "6 GIFs Saved to Downloads!"


class MainApp(App):
    def build(self):
        return MobileGreetingApp()

if __name__ == '__main__':
    MainApp().run()
