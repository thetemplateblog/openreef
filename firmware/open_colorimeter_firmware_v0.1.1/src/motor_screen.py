"""
Motor Control Screen - Memory Optimized Version

Minimal interface for controlling DC motors
"""

import board
import displayio
import constants
import fonts
from adafruit_display_text import label


class MotorScreen:
    """
    Minimal screen for motor control - optimized to use less memory
    Shows: Motor number, speed, and direction
    """

    def __init__(self):
        # Initialize state
        self.motor_num = 1
        self.speed = 0
        self.status = 'STOP'

        # Setup minimal color palette
        self.color_to_index = {k: i for (i, k) in enumerate(constants.COLOR_TO_RGB)}
        self.palette = displayio.Palette(len(constants.COLOR_TO_RGB))
        for i, palette_tuple in enumerate(constants.COLOR_TO_RGB.items()):
            self.palette[i] = palette_tuple[1]

        # Create tile grid
        self.bitmap = displayio.Bitmap(
            board.DISPLAY.width,
            board.DISPLAY.height,
            len(constants.COLOR_TO_RGB)
        )
        self.bitmap.fill(self.color_to_index['black'])
        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)

        # Create single combined label to save memory
        combined_str = 'M1 0% STOP'
        self.display_label = label.Label(
            fonts.font_14pt,
            text=combined_str,
            color=constants.COLOR_TO_RGB['orange'],
            scale=1,
            anchor_point=(0.5, 0.5),
        )
        self.display_label.anchored_position = (board.DISPLAY.width // 2, board.DISPLAY.height // 2)

        # Create display group with minimal elements
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.group.append(self.display_label)

    def set_motor_number(self, motor_num):
        """Set which motor number is being controlled (1-4)"""
        self.motor_num = motor_num
        self._update_display()

    def _update_display(self):
        """Update the combined display label"""
        motor_str = f'M{self.motor_num}'
        speed_str = f'{int(self.speed)}%'
        self.display_label.text = f'{motor_str} {speed_str} {self.status}'

        # Color code based on status
        if self.status == 'STOP':
            self.display_label.color = constants.COLOR_TO_RGB['orange']
        elif self.status == 'FWD':
            self.display_label.color = constants.COLOR_TO_RGB['green']
        elif self.status == 'REV':
            self.display_label.color = constants.COLOR_TO_RGB['blue']

    def update(self, throttle):
        """
        Update display based on throttle value

        Args:
            throttle: -1.0 to 1.0 (negative = reverse, positive = forward)
        """
        self.speed = abs(throttle) * 100

        if throttle > 0.01:
            self.status = 'FWD'
        elif throttle < -0.01:
            self.status = 'REV'
        else:
            self.status = 'STOP'

        self._update_display()

    def show(self):
        """Display this screen"""
        board.DISPLAY.show(self.group)
