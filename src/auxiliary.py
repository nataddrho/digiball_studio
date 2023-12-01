import numpy as np
import cv2

table_length_inches = 100
ball_diameter_inches = 2.25
tip_diameter_inches = 12 / 25.4
tip_radius_inches = 0.358 #dime
render_spin_mag_data = False

def degrees2clock(angle_deg):
    #Convert degrees into hours and minutes (o'clocks)
    a = angle_deg
    if a<0:
        a+=360
    hour = np.floor(a * 12/360.0)
    minutes = a*12/360.0 - hour
    if hour==0:
        hour = 12.0
    minutes = minutes*60
    return "%i:%s"%(hour,("%i"%minutes).zfill(2))

class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self._current_frame = 0
        self._vid = cv2.VideoCapture(video_source)
        self._total_frames = int(self._vid.get(cv2.CAP_PROP_FRAME_COUNT))
        self._frame_rate = self._vid.get(cv2.CAP_PROP_FPS)

        if not self._vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        # Get video source width and height
        self._width = int(self._vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_frame_time(self):
        return self._vid.get(cv2.CAP_PROP_POS_MSEC)/1000

    def get_frame_rate(self):
        return self._frame_rate

    def get_frame_dimensions(self):
        return (self._width, self._height)

    def get_frame(self):
        if self._vid.isOpened():
            ret, frame = self._vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                obj = (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                obj = (ret, None)
        else:
            obj = (ret, None)

        self._current_frame = self._vid.get(cv2.CAP_PROP_POS_FRAMES)
        return obj

    def get_dimensions(self):
        return (self._width, self._height)

    def get_frame_number(self):
        return (self._current_frame, self._total_frames)

    def goto_frame(self, frame_number):
        self._vid.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self._vid.isOpened():
            self._vid.release()