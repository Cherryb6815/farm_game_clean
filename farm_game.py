from xvfbwrapper import Xvfb
vdisplay = Xvfb()
vdisplay.start()
from ursina import *
import math

# ---------------- Third-Person Controller ----------------
class ThirdPersonController(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        # Player model
        self.model = 'assets/character.obj'  # replace with your character model
        self.scale = 1.2
        self.collider = 'box'
        self.speed = 5

        # Camera settings
        self.camera_distance = 10
        self.camera_height = 4
        self.rotation_speed = 80
        self.yaw = 0
        self.pitch = 20

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        # --- Camera Orbit ---
        self.yaw -= mouse.velocity[0] * self.rotation_speed
        self.pitch -= mouse.velocity[1] * self.rotation_speed
        self.pitch = clamp(self.pitch, -20, 60)

        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        cam_x = self.x + self.camera_distance * math.cos(rad_yaw) * math.cos(rad_pitch)
        cam_y = self.y + self.camera_height + self.camera_distance * math.sin(rad_pitch)
        cam_z = self.z + self.camera_distance * math.sin(rad_yaw) * math.cos(rad_pitch)

        camera.position = (cam_x, cam_y, cam_z)
        camera.look_at(self.position + Vec3(0,1,0))

        # --- Player Movement ---
        forward = Vec3(math.cos(rad_yaw), 0, math.sin(rad_yaw)).normalized()
        right = Vec3(-forward.z, 0, forward.x).normalized()

        direction = Vec3(
            forward * (held_keys['w'] - held_keys['s']) +
            right * (held_keys['d'] - held_keys['a'])
        ).normalized()

        self.position += direction * time.dt * self.speed

        if direction != Vec3(0, 0, 0):
            self.look_at(self.position + direction)


# ---------------- Main Game Class ----------------
class FarmGame(Ursina):
    def __init__(self):
        super().__init__()
        window.color = color.rgb(120,200,255)
        self.load_progress = 0
        self.loading_screen()

    # --- Loading Screen ---
    def loading_screen(self):
        self.bg = Entity(model='quad', scale=(16,9), texture='shore', parent=camera.ui)
        self.progress = Text(text='Loading: 0%', origin=(0,0), scale=2, y=-0.3)

        def update_loading():
            if self.load_progress < 100:
                self.load_progress += 2
                self.progress.text = f'Loading: {self.load_progress}%'
            else:
                destroy(self.bg)
                destroy(self.progress)
                invoke(self.crop_selection, delay=0.2)
                destroy(self.loading_task)

        self.loading_task = invoke(update_loading, delay=0.05, repeat=True)

    # --- Crop Selection Screen ---
    def crop_selection(self):
        self.title = Text("Choose your Crop", y=0.4, scale=2)
        self.rice_btn = Button(text="Rice", scale=(0.2,0.1), y=0.1)
        self.wheat_btn = Button(text="Wheat", scale=(0.2,0.1), y=-0.1)

        self.rice_btn.on_click = Func(self.start_farm_world,'Rice')
        self.wheat_btn.on_click = Func(self.start_farm_world,'Wheat')

    # --- Farm World ---
    def start_farm_world(self, crop):
        destroy(self.title)
        destroy(self.rice_btn)
        destroy(self.wheat_btn)

        # Ground
        Entity(model='plane', texture='grass', scale=50)

        # Farm objects
        Entity(model='cube', color=color.brown, scale=(4,2,4), position=(5,1,5))    # house
        Entity(model='cube', color=color.azure, scale=(4,0.2,4), position=(-5,0,-5)) # pond
        Entity(model='cube', color=color.gray, scale=(6,3,4), position=(-8,1,6))    # warehouse
        Entity(model='cube', color=color.green, scale=(1,3,1), position=(2,1.5,-3)) # tree

        # Player
        self.player = ThirdPersonController(position=(0,1,0))
        self.crop_info = Text(text=f"You chose {crop}!", origin=(0,0), y=0.45)


# ---------------- Run the Game ----------------
if __name__ == "__main__":
    FarmGame()
vdisplay.stop()