import cv2
import numpy as np
import src.auxiliary as auxiliary
class Renderer:

    def __init__(self, dataLog, hud_size=100):
        self._dataLog = dataLog
        self._hud_size = hud_size
        self._ball_diameter = int(self._hud_size * 0.9)
        self._ball_x = int(self._hud_size / 2)
        self._ball_y = int(self._ball_x)
        self._cueball_image = self._load_cueball_image()
        self._font = cv2.FONT_HERSHEY_SIMPLEX
        test_text = "12345678"
        self._font_thickness = 1
        self._font_scale = self._get_optimal_font_scale(test_text, self._hud_size, self._font, self._font_thickness)
        textSize = cv2.getTextSize(test_text, fontFace=self._font, fontScale=self._font_scale, thickness=self._font_thickness)
        self._font_height = textSize[0][1]


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

    def _get_optimal_font_scale(self, text, width, font, thickness):
        for scale in reversed(range(0, 30, 1)):
            textSize = cv2.getTextSize(text, fontFace=font, fontScale=scale / 10, thickness=thickness)
            new_width = textSize[0][0]
            if (new_width <= width):
                return scale/10
        return 1

    def _draw_spin_mag_data(self, frame, shot_data):
        left = self._hud_size + 5
        top = 5
        height = int(self._hud_size/2)-top
        width = height*4

        #Darken background
        overlay = frame.copy()
        cv2.rectangle(overlay, (left, top), (left+width, top+height), (0,0,0), -1)
        cv2.rectangle(overlay, (left,top), (left+width, top+height), (255,255,255), 1)
        alpha = 0.5
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        #Draw data
        if 'gymag' in shot_data:
            data = shot_data['gymag']
            N = len(data)

            for i in range(N-1):
                y1 = int(top + height - int(height * data[i] / 256))
                y2 = int(top + height - int(height * data[i+1] / 256))
                x1 = int(left + i * width/N)
                x2 = int(left + (i + 1) * width/N)
                frame = cv2.line(frame, (x1,y1), (x2,y2), (0,255,255), 1)

                #Draw impact marks
                #if data[i]&1==1:
                #    frame = cv2.line(frame, (x1, top+height), (x1, top+int(height*0.8)),(255,165,0),1)

        return frame


    def draw_hud_on_frame(self, frame, time_after_shot, shot_data):

        if time_after_shot is not None:
            if time_after_shot>0 and time_after_shot<10:

                #Draw ball image
                frame = self._draw_ball_on_frame(frame)

                # Draw spin mag data
                if auxiliary.render_spin_mag_data:
                    frame = self._draw_spin_mag_data(frame, shot_data)

                #Draw on ball
                ball_x = self._ball_x
                ball_y = self._ball_y
                ball_r = int(self._ball_diameter/2)
                frame = cv2.line(frame, (ball_x-ball_r,ball_y), (ball_x+ball_r,ball_y), (128,128,128), 1)
                frame = cv2.line(frame, (ball_x,ball_y-ball_r), (ball_x, ball_y+ball_r), (128, 128, 128), 1)

                ang = shot_data['deg']
                x = int(ball_r * np.sin(ang*np.pi/180))
                y = int(-ball_r * np.cos(ang*np.pi/180))

                #Draw tip angle line
                frame = cv2.line(frame, (ball_x, ball_y), (ball_x+x, ball_y+y), (255,0,0), 2)

                if 'tip' in shot_data:
                    tip_percent = shot_data['tip']
                    tip_norm = tip_percent / 100
                    tip_outline_offset = tip_norm * ball_r * 2 * auxiliary.tip_radius_inches / auxiliary.ball_diameter_inches
                    tip_outline_offset_radius = ball_r * tip_norm + tip_outline_offset
                    to_x = int(tip_outline_offset_radius * np.sin(ang * np.pi / 180))
                    to_y = int(tip_outline_offset_radius * -np.cos(ang * np.pi / 180))
                    tip_outline_draw_radius = int(ball_r * auxiliary.tip_diameter_inches / auxiliary.ball_diameter_inches)

                    x = int(tip_norm * ball_r * np.sin(ang * np.pi / 180))
                    y = int(tip_norm * -ball_r * np.cos(ang * np.pi / 180))

                    #frame = cv2.circle(frame, (ball_x+to_x, ball_y+to_y), tip_outline_draw_radius, (0,0,0), 2)
                    overlay = frame.copy()
                    cv2.circle(overlay, (ball_x+to_x, ball_y+to_y), tip_outline_draw_radius, (0,0,0), -1)
                    alpha = 0.45
                    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

                    frame = cv2.circle(frame, (ball_x+x, ball_y+y), 3, (0,0,255), -1)

                # Draw text
                clock = auxiliary.degrees2clock(shot_data['deg'])
                rpm = "%i rpm"%(shot_data['rpm'])

                if 'tip' in shot_data:
                    feet = "%.2f ft" % (shot_data['inch'] / 12)
                    mph = "%.2f mph" % (shot_data['mph'])
                    tipper = "%.1f%%" % (shot_data['tip'])
                    sfr = np.pi * auxiliary.ball_diameter_inches / 1056 * shot_data['rpm'] / shot_data['mph']
                    sfrt = "%.2f SFR"%sfr
                    texts = (clock, rpm, feet, mph, tipper, sfrt)
                else:
                    texts = (clock, rpm)

                for i in range(0,len(texts)):
                    x = 3
                    y = ball_x + ball_r + (self._font_height + 3)*(i+1)
                    frame, cv2.putText(frame, texts[i], (x,y), self._font, self._font_scale, (255,255,255), self._font_thickness, cv2.LINE_AA)


        return frame

    def render_video(self, video_file_name):

        file_prefix = video_file_name[:video_file_name.rfind(".")]
        output_file_name = "%s_out.mp4" % file_prefix
        vid = auxiliary.VideoCapture(video_file_name)
        frame_rate = vid.get_frame_rate()
        frame_dimensions = vid.get_dimensions()

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_file_name, fourcc, frame_rate, frame_dimensions)

        while 1:
            ret, frame = vid.get_frame()
            frame_time_seconds = vid.get_frame_time()
            frame_current, frame_total = vid.get_frame_number()
            percentage_complete = 100*frame_current/frame_total
            shot_index, shot_data, tmp = self._dataLog.get_next_shot_data(frame_time_seconds)
            shot_time_seconds = shot_data['time']
            time_after_shot = frame_time_seconds - shot_time_seconds

            #Add HUD to frame
            frame_hud = self.draw_hud_on_frame(frame, time_after_shot, shot_data)

            #Write frame
            writer.write(cv2.cvtColor(frame_hud,cv2.COLOR_RGB2BGR))

            #End of video
            if frame_current>=frame_total:
                print("%s complete."%output_file_name)
                break
            else:
                if frame_current%100==0:
                    print("Processing... %.1f%%"%percentage_complete)

        #Clean up
        del vid
        writer.release()

