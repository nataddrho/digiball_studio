# digiball_studio

Version 1.0.0

Usage example video: https://youtu.be/2rfpNHpOLc0?si=scOqSBXc5XAaWAz9

Rendered video example: https://youtu.be/rC_Oi0zrVlU

Information about the DigiBall: https://www.digicue.net/digiball

## Overview

This is an experimental python-based post-processing program for combining DigiBall data (shared from the mobile app) to a video recording. Distance is selected by the user as well as the collision time of the target, giving linear speed. Once linear speed is available, a lot of information about the shot can be shown in a heads-up display.

## How to run this project
1. Clone the code to the machine you'd like to run it from
2. Navigate to this project directory in a terminal window
3. Make sure you have Python and Pip installed on this machine
4. Run (while being in the project home directory) `python -m venv venv` to create a virtrual environment
5. Run `source venv/bin/activate` to activate this virtual environment
6. Run `pip install -r requirements.txt` to install project dependencies
7. Run `python main.py`

## How to update requirements.txt
1. Navigate to the project directory in a terminal and activate the virtualenv (step 5 above)
2. Run `pip freeze > requirements.txt`

## How To Generate Data for DigiBall Studio

1. Start video recording a practice session or a game.
2. Open the mobile DigiBall app and verify that the DigiBall is transmitting data.
3. Go to the Settings tab and press the Set Tag Button. Type in a description that describes this practice session / game / match.
4. Stand in front of the video camera, and simultaneously signal to the camera while pressing the OK button in the Set Tag dialog box. You can raise your arm, give a thumbs up, etc. This will create a visual queue used later to sync the data file to the video file.
5. Verify that the Keep Screen Awake setting is set to Yes (it is by default). This will keep focus on the app and allow Bluetooth to continously record data.
6. Set your phone down within 15 feet of the table and away from metallic objects.
7. Play or observe the game / match.
8. When the session is complete, press the End Tag button to close the session. This is optional.

## How to Import Data into DigiBall Studio

1. Clone or copy the code to your computer.
2. Copy both the video file and your digiball.log into the main folder (overwrite the existing demo digiball.log file). This data file can be shared from the app by clicking the Share Data button in the Settings tab.
3. Run main.py
4. Select the video file with the file select dialog.
5. Move the slider so that the video is on the frame with the visual queue sync you created earlier.
6. Click the Align Data button.
7. Select the tag description that you typed in earlier. (Alternatively, enter the epoch or date-time that aligns the DigiBall data with the current frame.)
8. Click Align and verify success.

## Configuring Distance and Impact Time
1. Adjust the blue lines with the right mouse button. Modify so that the dark blue lines are on the short rails. All lines should be on the slate-cushion interface.
2. Now go through the video and use the left mouse button to draw a red line between the cue ball and object ball / target. Then when the spin magnitude data is shown (in the black box), select the impact time. This is shown with a green vertical line in the black box.
3. Do this for each shot.
4. Your work is automatically saved as a .proj file extension of the video file.

## Meaning of Text Displayed in the HUD
1. Clock time, representing the spin applied if it were where an hour hand of a clock points
2. RPM (rotations per second) of ball when struck
3. Distance between ball and target
4. MPH (miles per hour). Translational speed of ball across surface of table
5. Tip Percentage. The percent of ball radius from center that the tip struck the ball (blue dot in the diagram)
6. Spin Factor Ratio. The ratio of rotational ball speed to linear ball speed in radians/radius.

## Rendering the Final video
1. When you are done, click the Export Video button. A video will be rendered with a similar heads-up display. Progress percentage is shown in the console. The filename is the same as the original video but with an _out extension before the suffix.
2. Sound is lost. Use ffmpeg to copy the audio from the original video to the new video.
