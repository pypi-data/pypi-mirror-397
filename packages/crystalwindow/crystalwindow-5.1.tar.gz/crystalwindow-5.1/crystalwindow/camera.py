class Camera:
    def __init__(self, target, speed=0.1):
        self.target = target  # sprite or obj w/ x,y
        self.offset_x = 0
        self.offset_y = 0
        self.speed = speed  # smoothness

    def update(self, win_width, win_height, dt):
        # camera aims for target center
        target_x = self.target.x - win_width // 2
        target_y = self.target.y - win_height // 2

        # smooth lerp follow
        self.offset_x += (target_x - self.offset_x) * self.speed
        self.offset_y += (target_y - self.offset_y) * self.speed

        if hasattr(self, "shake"):
            self.shake.update(dt)

    def apply(self, obj):
        # shift object's draw position by camera offset
        sx, sy = (0, 0)
        if hasattr(self, "shake"):
            sx, sy = self.shake.offset

        return (
            obj.x -self.offset_x + sx,
            obj.y -self.offset_y + sy
        )    

    def shake_scrn(self, intensity=5, secs=1):
        # the shake screen effect shakes the screen for an ammount of time/secs
        from .draw_helpers import CameraShake
        self.shake = CameraShake(intensity, secs)

    def move_to(self, x, y):
        self.offset_x = x
        self.offset_y = y

    def reset_pos(self):
        self.offset_x = 0
        self.offset_y = 0