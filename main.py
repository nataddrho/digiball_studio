#Nathan Rhoades LLC

import tkinter as tk
from tkinter import filedialog
import cv2
import PIL.Image, PIL.ImageTk
import time
import numpy as np
import pickle
import src.file_access as file_access
import src.auxiliary as auxiliary
import src.alignment_tool as alignment_tool
import src.render as render


class App:
    def __init__(self, window, video_source=0, project_name=None):

        window_title = "DigiBall Studio v1.0.0"

        # Open file
        self.dataLog = file_access.DataLog()

        self.table_length_inches = auxiliary.table_length_inches
        self.ball_diameter_inches = auxiliary.ball_diameter_inches
        self.tip_diameter_inches = auxiliary.tip_diameter_inches
        self.tip_radius_inches = auxiliary.tip_radius_inches

        self.play_video = True
        self.auto_update_slider = True
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        # open video source (by default this will try to open the computer webcam)
        self.vid = auxiliary.VideoCapture(self.video_source)
        # Create a canvas that can fit the above video source size
        self.width, self.height = self.vid.get_dimensions()
        self.homographic_points = [[self.width-5,5],[self.width-5,self.height-5],[5,self.height-5],[5,5]]
        self.homographic_point_move = None
        self.distance_normalized_to_table_length = 0
        self.distance_points = [[5,5],[10,10]]
        self.canvas = tk.Canvas(window, width = self.width, height = self.height)
        self.canvas.bind("<Button-1>",self.canvas_mouse_left_down)
        self.canvas.bind("<B1-Motion>", self.canvas_mouse_left_moved)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_mouse_left_up)
        self.canvas.bind("<Button-3>", self.canvas_mouse_right_down)
        self.canvas.bind("<B3-Motion>", self.canvas_mouse_right_moved)
        self.canvas.bind("<ButtonRelease-3>", self.canvas_mouse_right_up)
        self.canvas.pack()
        self.timeslider = tk.Canvas(window, width = 400, height = 50, bg='black')
        self.timeslider.bind("<Button-1>", self.timeslider_mouse_left_down)
        self.timeslider.bind("<B1-Motion>", self.timeslider_mouse_left_moved)
        self.timeslider.bind("<ButtonRelease-1>", self.timeslider_mouse_left_up)
        self.timeslider.pack()

        self.build_video_controls(window)
        self.time_after_shot = None
        self.time_selected = None
        self.time_slider_position = None


        # Text boxes
        self.txt_distance_value = tk.StringVar()
        self.txt_distance=tk.Entry(window, width=10, textvariable=self.txt_distance_value)
        self.txt_distance.pack(side=tk.LEFT)

        self.txt_frame_time_value = tk.StringVar()
        self.txt_frame_time = tk.Entry(window, width=10, textvariable=self.txt_frame_time_value)
        self.txt_frame_time.pack(side=tk.LEFT)

        self.txt_degrees_value = tk.StringVar()
        self.txt_degrees = tk.Entry(window, width=15, textvariable=self.txt_degrees_value)
        self.txt_degrees.pack(side=tk.LEFT)

        self.txt_rpm_value = tk.StringVar()
        self.txt_rpm = tk.Entry(window, width=10, textvariable=self.txt_rpm_value)
        self.txt_rpm.pack(side=tk.LEFT)

        self.txt_feet_value = tk.StringVar()
        self.txt_feet = tk.Entry(window, width=10, textvariable=self.txt_feet_value)
        self.txt_feet.pack(side=tk.LEFT)

        self.txt_mph_value = tk.StringVar()
        self.txt_mph = tk.Entry(window, width=10, textvariable=self.txt_mph_value)
        self.txt_mph.pack(side=tk.LEFT)

        self.txt_tipper_value = tk.StringVar()
        self.txt_tipper = tk.Entry(window, width=10, textvariable=self.txt_tipper_value)
        self.txt_tipper.pack(side=tk.LEFT)

        self.txt_time_selected_value = tk.StringVar()
        self.txt_time_selected = tk.Entry(window, width=10, textvariable=self.txt_time_selected_value)
        self.txt_time_selected.pack(side=tk.LEFT)

        #Load project settings
        if project_name is not None:
            self.load_project(project_name)

        self.window_update_delay = 15
        self.after_handle = None
        self.update()
        #self.window.attributes('-topmost', True) #Keep window on top
        self.window.mainloop()

    def save_project(self, project_file_name):
        with open(project_file_name, 'wb') as fp:
            projData = {}
            projData["Shot Data"] = self.dataLog.get_all_shot_data()
            projData["HCoords"] = self.homographic_points
            projData["DCoords"] = self.distance_points
            projData["Video File Name"] = self.video_source
            pickle.dump(projData, fp)

    def load_project(self, project_file_name):
        try:
            with open(project_file_name, 'rb') as fp:
                projData = pickle.load(fp)
                self.dataLog.set_all_shot_data(projData["Shot Data"])
                self.homographic_points = projData["HCoords"]
                self.distance_points = projData["DCoords"]
                return True
        except:
            return False



    def build_video_controls(self, window):
        frame = tk.Frame(window)
        frame.pack()

        # Position slider
        current_frame, total_frames = self.vid.get_frame_number()
        self.sld_position = tk.Scale(frame, from_=0, to_=total_frames, orient='horizontal',
                                     length=self.width)
        self.sld_position.bind("<B1-Motion>", self.slider_moved)
        self.sld_position.bind("<Button-1>", self.slider_down)
        self.sld_position.bind("<ButtonRelease-1>", self.slider_up)
        self.sld_position.pack(anchor=tk.CENTER, expand=True)

        # Button that lets the user take a snapshot
        frame_buttons = tk.Frame(frame)
        frame_buttons.pack(anchor=tk.CENTER, expand=True)
        self.btn_align_data = tk.Button(frame_buttons, text="Align Data", command=self.align_data)
        self.btn_align_data.pack(side=tk.LEFT)
        self.btn_snapshot = tk.Button(frame_buttons, text="Snapshot", command=self.snapshot)
        self.btn_snapshot.pack(side=tk.LEFT)
        self.btn_flip = tk.Button(frame_buttons, text="Flip", command=self.flip)
        self.btn_flip.pack(side=tk.LEFT)
        self.btn_rewind = tk.Button(frame_buttons, text="<<", width=5, command=self.rewind)
        self.btn_rewind.pack(side=tk.LEFT)
        self.btn_rewind_single = tk.Button(frame_buttons, text="<", width=5, command=self.rewind_single)
        self.btn_rewind_single.pack(side=tk.LEFT)
        self.btn_pause = tk.Button(frame_buttons, text="||", width=5, command=self.pause)
        self.btn_pause.pack(side=tk.LEFT)
        self.btn_play = tk.Button(frame_buttons, text="Play", width=5, command=self.play)
        self.btn_play.pack(side=tk.LEFT)
        self.btn_forward_single = tk.Button(frame_buttons, text=">", width=5, command=self.forward_single)
        self.btn_forward_single.pack(side=tk.LEFT)
        self.btn_forward = tk.Button(frame_buttons, text=">>", width=5, command=self.forward)
        self.btn_forward.pack(side=tk.LEFT)
        self.btn_export = tk.Button(frame_buttons, text="Export Video", command=self.export)
        self.btn_export.pack(side=tk.LEFT)


    def export(self):
        self.pause()
        out = render.Renderer(self.dataLog)
        out.render_video(self.video_source)

    def draw_on_timeslider(self):
        canvas = self.timeslider
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        #Plot gyromag data
        if 'gymag' in self.shot_data:
            data = self.shot_data['gymag']
            N = len(data)

            #Update slider time
            if self.time_slider_position is not None:
                self.time_selected = self.time_slider_position/width * N/104 #104 Hz sample rate
                if self.time_selected<0:
                    self.time_selected = 0
                self.txt_time_selected_value.set('%.2f s'%self.time_selected)

            for i in range(N-1):
                y1 = height - int(height * data[i] / 256)
                y2 = height - int(height * data[i+1] / 256)
                x1 = i * width/N
                x2 = (i + 1) * width/N
                self.draw_line_on_canvas(canvas, "plot_%i"%i, x1, y1, x2, y2, 1, 'cyan')
                if data[i]&1==1:
                    self.draw_line_on_canvas(canvas, "impact_%i", x1, height, x1, height*0.8, 1, 'orange')

        #Draw selected slider position
        if self.time_slider_position is not None:
            x = self.time_slider_position
            self.draw_line_on_canvas(canvas, "slider", x, 0, x, height, 2, 'green')


    def draw_on_canvas(self):

        #Draw homographic polygon
        line_width = 2
        a = self.homographic_points
        b = self.distance_points
        canvas = self.canvas
        line_color = 'cyan'
        self.draw_line_on_canvas(canvas,"hom1", a[0][0], a[0][1], a[1][0], a[1][1], line_width, line_color)
        line_color = 'blue'
        self.draw_line_on_canvas(canvas,"hom2", a[1][0], a[1][1], a[2][0], a[2][1], line_width, line_color)
        line_color = 'cyan'
        self.draw_line_on_canvas(canvas,"hom3", a[2][0], a[2][1], a[3][0], a[3][1], line_width, line_color)
        line_color = 'blue'
        self.draw_line_on_canvas(canvas,"hom4", a[3][0], a[3][1], a[0][0], a[0][1], line_width, line_color)

        line_color = 'red'
        self.draw_line_on_canvas(canvas,"dist", b[0][0], b[0][1], b[1][0], b[1][1], line_width, line_color)


        #Draw ball graphic
        if self.time_after_shot is not None:

            if self.time_after_shot>0 and self.time_after_shot<10:

                ang = self.corrected_deg(self.shot_data['deg'])
                r = 45
                center = 50
                x = r * np.sin(ang*np.pi/180)
                y = -r * np.cos(ang*np.pi/180)

                line_color = 'black'
                fill_color = 'white'
                self.draw_oval_on_canvas(canvas,"ball_circle",center, center, r, line_width, line_color, fill_color)

                line_color = 'gray'
                self.draw_line_on_canvas(canvas, "grid_1", center, center - r, center, center + r, 1, line_color)
                self.draw_line_on_canvas(canvas, "grid_2", center - r, center, center + r, center, 1, line_color)

                line_color = 'red'
                self.draw_line_on_canvas(canvas, "spin_angle", center, center, center + x, center + y, line_width,
                                         line_color)

                if 'tip' in self.shot_data:
                    tip_percent = self.shot_data['tip']
                    tip_norm = tip_percent / 100
                    tip_outline_offset = tip_norm * r * 2 * self.tip_radius_inches / self.ball_diameter_inches
                    tip_outline_offset_radius = r * tip_norm + tip_outline_offset
                    to_x = tip_outline_offset_radius * np.sin(ang * np.pi / 180)
                    to_y = tip_outline_offset_radius * -np.cos(ang * np.pi / 180)
                    tip_outline_draw_radius = r * self.tip_diameter_inches/self.ball_diameter_inches

                    x = tip_norm * r * np.sin(ang * np.pi / 180)
                    y = tip_norm * -r * np.cos(ang * np.pi / 180)

                    line_color = 'black'
                    fill_color = 'blue'
                    self.draw_oval_on_canvas(canvas,"tip_outline",center+to_x, center+to_y, tip_outline_draw_radius, line_width, line_color)
                    self.draw_oval_on_canvas(canvas,"tip",center+x, center+y, 3, line_width, line_color, fill_color)

                # Draw text
                clock = auxiliary.degrees2clock(self.corrected_deg(self.shot_data['deg']))
                self.draw_text_on_canvas(canvas, "text1", 5, 2 * r + 20, clock)
                rpm = self.shot_data['rpm']
                self.draw_text_on_canvas(canvas, "text2", 5, 2 * r + 40, "%i rpm"%rpm)
                if 'tip' in self.shot_data:
                    feet = self.shot_data['inch']/12
                    self.draw_text_on_canvas(canvas, "text3", 5, 2 * r + 60, "%.2f ft" % feet)
                    mph = self.shot_data['mph']
                    self.draw_text_on_canvas(canvas, "text4", 5, 2 * r + 80, "%.2f mph"%mph)
                    tipper = self.shot_data['tip']
                    self.draw_text_on_canvas(canvas, "text5", 5, 2 * r + 100, "%.1f%%"%tipper)                    
                    srf = np.pi * self.ball_diameter_inches / 1056 * rpm / mph
                    self.draw_text_on_canvas(canvas, "text6", 5, 2 * r + 120, "%.2f SRF" % srf)

    def draw_text_on_canvas(self,canvas,text_name,x1,y1,text,fill_color='white'):
        #Updates text if they already exist rather than wasting memory redrawing text over and over again
        item_id = canvas.find_withtag(text_name)
        font = ('Helvetica 15')
        if item_id:
            canvas.itemconfigure(item_id, text=text)
            canvas.tag_raise(text_name)
        else:
            canvas.create_text(x1,y1,text=text,fill=fill_color,tags=text_name, font=font, anchor="w")

    def draw_line_on_canvas(self,canvas,line_name,x1,y1,x2,y2,line_width,line_color):
        #Updates lines if they already exist rather than wasting memory redrawing lines over and over again
        item_id = canvas.find_withtag(line_name)
        if item_id:
            canvas.coords(line_name,x1,y1,x2,y2)
            canvas.tag_raise(line_name)
        else:
            canvas.create_line(x1,y1,x2,y2,width=line_width,fill=line_color,tags=line_name)

    def draw_rect_on_canvas(self,canvas,line_name,x1,y1,x2,y2,line_width,line_color):
        #Updates lines if they already exist rather than wasting memory redrawing lines over and over again
        item_id = canvas.find_withtag(line_name)
        if item_id:
            canvas.coords(line_name,x1,y1,x2,y2)
            canvas.tag_raise(line_name)
        else:
            canvas.create_rectangle(x1,y1,x2,y2,width=line_width,fill=line_color,tags=line_name)

    def draw_oval_on_canvas(self,canvas,line_name,x,y,r,line_width,line_color,fill_color=''):
        #Updates lines if they already exist rather than wasting memory redrawing lines over and over again
        x1 = x-r
        x2 = x+r
        y1 = y-r
        y2 = y+r
        item_id = canvas.find_withtag(line_name)
        if item_id:
            canvas.coords(line_name,x1,y1,x2,y2)
            canvas.tag_raise(line_name)
        else:
            canvas.create_oval(x1,y1,x2,y2,width=line_width,outline=line_color,fill=fill_color,tags=line_name)

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if ret:
            rClass = render.Renderer(self.dataLog)
            rendered_frame = rClass.draw_hud_on_frame(frame, self.time_after_shot, self.shot_data)
            cv2.imwrite("frame-" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".jpg", cv2.cvtColor(rendered_frame, cv2.COLOR_RGB2BGR))

    def align_data(self):
        self.pause()
        dialog = alignment_tool.AlignmentDialog(self.window,
                                                self.dataLog.get_all_tags(),
                                                self.vid.get_frame_time(),
                                                self.dataLog)


    def copy_frame_to_canvas(self):

        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        frame_time_seconds = self.vid.get_frame_time()
        self.txt_frame_time_value.set('%.3fs'%frame_time_seconds)
        self.shot_index, self.shot_data, tmp = self.dataLog.get_next_shot_data(frame_time_seconds)
        shot_time_seconds = self.shot_data['time']
        self.time_after_shot = frame_time_seconds - shot_time_seconds

        return ret

    def calculate_and_save_tip_position(self, dist_norm, time_sec, spin_rpm):

        speed_mph = 3600/63360 * self.table_length_inches * dist_norm / time_sec
        tip_percent = 0.0030122 * spin_rpm / (1.125 * speed_mph) * 1.1
        tip_inches = tip_percent * 1.125

        #Save data to memory
        self.dataLog.set_shot_data(self.shot_index, 'mph', speed_mph)
        self.dataLog.set_shot_data(self.shot_index, 'inch', self.table_length_inches * dist_norm)
        self.dataLog.set_shot_data(self.shot_index, 'tip', tip_percent*100)
        self.dataLog.set_shot_data(self.shot_index, 'secsl', time_sec)


    def flip(self):
        ret = self.dataLog.get_shot_data(self.shot_index, 'flip')
        if (ret is None):
            flip = True
        else:
            flip = not ret
        self.dataLog.set_shot_data(self.shot_index, 'flip', flip)   

    def is_flipped(self):
        ret = self.dataLog.get_shot_data(self.shot_index, 'flip')
        if (ret is None):
            flip = False
        else:
            flip = ret
        return flip
        
    def corrected_deg(self, angle_deg):        
        if (self.is_flipped()):
            return auxiliary.flip_angle(angle_deg)
        else:
            return angle_deg
        

    def update_shot_data_info(self):
        data = self.shot_data
        if data is not None:
            if 'rpm' in data:
                self.txt_rpm_value.set('%.1f rpm'%self.shot_data['rpm'])
            else:
                self.txt_rpm_value.set('')

            if 'deg' in data:
                clock = auxiliary.degrees2clock(self.corrected_deg(self.shot_data['deg']))
                if (self.is_flipped()):
                    clock = "%s flipped"%clock
                             
                self.txt_degrees_value.set(clock)
            else:
                self.txt_degrees_value.set('')

            if 'mph' in data:
                self.txt_mph_value.set('%.2f mph'%self.shot_data['mph'])
            else:
                self.txt_mph_value.set('')

            if 'inch' in data:
                self.txt_feet_value.set('%.2f ft'%(self.shot_data['inch']/12))
            else:
                self.txt_feet_value.set('')

            if 'tip' in data:
                self.txt_tipper_value.set('%.2f%%'%self.shot_data['tip'])
            else:
                self.txt_tipper_value.set('')

    def update(self):
        if self.play_video:
            ret = self.copy_frame_to_canvas()
            if ret:
                frame,total = self.vid.get_frame_number()
                if self.auto_update_slider:
                    self.sld_position.set(frame)

        self.draw_on_canvas()
        self.draw_on_timeslider()
        self.update_shot_data_info()
        self.after_handle = self.window.after(self.window_update_delay, self.update)

    def update_if_paused(self):
        if not self.play_video:
            ret = self.copy_frame_to_canvas()
            frame, total = self.vid.get_frame_number()
            self.sld_position.set(frame)
            self.draw_on_canvas()
            self.draw_on_timeslider()
            self.update_shot_data_info()

    def move_frame_delta(self, frames):
        frame, total = self.vid.get_frame_number()
        self.vid.goto_frame(frame + frames - 1)

    def slider_down(self, event):
        self.auto_update_slider = False

    def slider_moved(self, event):
        position_frame = self.sld_position.get()
        self.vid.goto_frame(position_frame)
        if not self.play_video:
            ret = self.copy_frame_to_canvas()

    def slider_up(self, event):
        self.auto_update_slider = True

    def pause(self):
        self.play_video = False

    def play(self):
        if not self.play_video:
            self.play_video = True

    def rewind(self):
        self.move_frame_delta(-100)
        self.update_if_paused()

    def rewind_single(self):
        self.move_frame_delta(-1)
        self.update_if_paused()

    def forward(self):
        self.move_frame_delta(100)
        self.update_if_paused()

    def forward_single(self):
        self.move_frame_delta(1)
        self.update_if_paused()

    def timeslider_mouse_left_down(self, event):
        x, y = event.x, event.y


    def timeslider_mouse_left_moved(self, event):
        x, y = event.x, event.y
        self.time_slider_position = x

        if self.distance_normalized_to_table_length > 0 and self.time_selected is not None:
            dist_norm = self.distance_normalized_to_table_length
            time_sec = self.time_selected
            spin_rpm = self.shot_data['rpm']
            self.calculate_and_save_tip_position(dist_norm, time_sec, spin_rpm)



    def timeslider_mouse_left_up(self, event):
        x, y = event.x, event.y


    def canvas_mouse_left_down(self, event):
        x, y = event.x, event.y
        self.distance_points[0][0] = x
        self.distance_points[0][1] = y
        self.distance_points[1][0] = x
        self.distance_points[1][1] = y
        self.update_homographic_distance()

    def canvas_mouse_left_moved(self, event):
        x, y = event.x, event.y
        self.distance_points[1][0] = x
        self.distance_points[1][1] = y
        self.update_homographic_distance()

    def canvas_mouse_left_up(self, event):
        x, y = event.x, event.y
        self.distance_points[1][0] = x
        self.distance_points[1][1] = y
        self.update_homographic_distance()

    def canvas_mouse_right_down(self, event):
        #Choose homographic point closest to mouse
        x1, y1 = event.x, event.y
        r = None
        index = 0
        for i in range(0,4):
            x2 = self.homographic_points[i][0]
            y2 = self.homographic_points[i][1]
            dist = np.sqrt((x1-x2)**2+(y1-y2)**2)
            if r is None:
                r = dist
                index = i
            else:
                if dist<r:
                    r=dist
                    index = i
        self.homographic_point_move = index
        self.update_homographic_distance()

    def canvas_mouse_right_moved(self, event):
        x, y = event.x, event.y
        i = self.homographic_point_move
        self.homographic_points[i][0] = x
        self.homographic_points[i][1] = y
        self.update_homographic_distance()

    def canvas_mouse_right_up(self, event):
        self.homographic_point_move = None
        self.update_homographic_distance()

    def update_homographic_distance(self):
        self.distance_normalized_to_table_length = self.get_homographic_distance(1,0.5)
        self.txt_distance_value.set('%.3f\u2662'%(self.distance_normalized_to_table_length*8))

    def get_homographic_distance(self, scaleX, scaleY):
        #Calculates the distance selected based on the homographic bounding polygon
        #ScaleX and ScaleY are the units to multiply the X and Y axes by

        pts1 = np.array(self.homographic_points, dtype = 'f')
        ratio = 1.6
        self._pH = np.sqrt((pts1[2][0] - pts1[1][0]) * (pts1[2][0] - pts1[1][0]) + (pts1[2][1] - pts1[1][1]) * (
                pts1[2][1] - pts1[1][1]))
        self._pW = ratio * self._pH
        self._pts2 = np.float32([[pts1[0][0], pts1[0][1]], [pts1[0][0] + self._pW, pts1[0][1]],
                                 [pts1[0][0] + self._pW, pts1[0][1] + self._pH],
                                 [pts1[0][0], pts1[0][1] + self._pH]])
        self._M = cv2.getPerspectiveTransform(pts1, self._pts2)

        points = np.array([[[self.distance_points[0][0],self.distance_points[0][1]]],
                           [[self.distance_points[1][0],self.distance_points[1][1]]]])

        hpoints = self._M.dot(np.array([[x, y, 1] for [[x, y]] in points]).T)
        hpoints /= hpoints[2]
        result = np.array([[[x, y]] for [x, y] in hpoints[:2].T])

        x1 = scaleX * (result[0][0][0] - self._pts2[0][0]) / self._pW
        y1 = scaleY * (result[0][0][1] - self._pts2[0][1]) / self._pH
        x2 = scaleX * (result[1][0][0] - self._pts2[0][0]) / self._pW
        y2 = scaleY * (result[1][0][1] - self._pts2[0][1]) / self._pH

        distance_normalized = np.sqrt((x1-x2)**2+(y1-y2)**2)
        return distance_normalized





if __name__=='__main__':

    filetypes = [("Video",".mp4")]
    file_path = filedialog.askopenfilename(title='Select video', filetypes=filetypes)
    video_file_name = file_path
    project_file_name = "%s.proj" % video_file_name

    #Main app
    app = App(tk.Tk(), video_file_name, project_file_name)
    app.save_project(project_file_name) #Save project on close

