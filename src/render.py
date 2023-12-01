import cv2
import numpy as np

class Renderer:

    def __init__(self, dataLog):
        self._dataLog = dataLog
        self._hud_width = 100
        self._ball_diameter = int(self._hud_width * 0.9)
        self._ball_x = int(self._hud_width / 2)
        self._ball_y = int(self._ball_x)
        self._cueball_image = self._load_cueball_image()

    def _load_cueball_image(self):
        img = cv2.imread("img/cueball.png", cv2.IMREAD_UNCHANGED) #Includes alpha channel
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        resized = cv2.resize(img, (self._ball_diameter, self._ball_diameter))
        return resized

    def _draw_ball_on_frame(self, frame):
        ball_x = self._ball_x
        ball_y = self._ball_y
        ball_d = self._ball_diameter
        ball_r = ball_d/2

        #Overlay ball with alpha channel. First need to add ball to image with same size, then "over" composite
        background = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
        foreground = np.zeros_like(background)
        overlay = self._cueball_image
        x_offset = int(ball_x-ball_r)
        y_offset = int(ball_y-ball_r)
        foreground[y_offset:y_offset+overlay.shape[0], x_offset:x_offset+overlay.shape[1]] = overlay

        # normalize alpha channels from 0-255 to 0-1
        alpha_background = background[:, :, 3] / 255.0
        alpha_foreground = foreground[:, :, 3] / 255.0

        # set adjusted colors
        for color in range(0, 3):
            background[:, :, color] = alpha_foreground * foreground[:, :, color] + \
                                      alpha_background * background[:, :, color] * (1 - alpha_foreground)

        # set adjusted alpha and denormalize back to 0-255
        background[:, :, 3] = (1 - (1 - alpha_foreground) * (1 - alpha_background)) * 255

        return background

    def draw_hud_on_frame(self, frame, time_after_shot, shot_data):

        if time_after_shot is not None:
            if time_after_shot>0 and time_after_shot<10:

                #Draw ball image
                frame = self._draw_ball_on_frame(frame)

                #Draw lines on ball

                #Draw text
                ang = shot_data['deg']
                r = 45
                center = 50
                x = r * np.sin(ang*np.pi/180)
                y = -r * np.cos(ang*np.pi/180)

                if 'tip' in shot_data:
                    tip_percent = shot_data['tip']
                    tip_norm = tip_percent / 100





        return frame

