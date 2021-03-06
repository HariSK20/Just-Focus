import cv2
import mediapipe as mp
import numpy as np
import time
import sys
from flask import Flask, request
from flask_cors import cross_origin
import threading
# from playsound import playsound
app = Flask(__name__)

opencv_start_flag = False
state = 1
atten_flag = True

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
#for timing
global ind, t1, timeout
timeout = 15
tcount=0
#for timing
cap = cv2.VideoCapture(0)

def run_opencv():
	global drawing_spec, tcount, ind, mp_drawing, face_mesh, opencv_start_flag, atten_flag
	while cap.isOpened() and opencv_start_flag:
		success, image = cap.read()

		start = time.time()

		# Flip the image horizontally for a later selfie-view display
		# Also convert the color space from BGR to RGB
		image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

		# To improve performance
		image.flags.writeable = False

		# Get the result
		results = face_mesh.process(image)

		# To improve performance
		image.flags.writeable = True

		# Convert the color space from RGB to BGR
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

		img_h, img_w, img_c = image.shape
		face_3d = []
		face_2d = []

		if results.multi_face_landmarks:
			for face_landmarks in results.multi_face_landmarks:
				for idx, lm in enumerate(face_landmarks.landmark):
					if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
						if idx == 1:
							nose_2d = (lm.x * img_w, lm.y * img_h)
							nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)

						x, y = int(lm.x * img_w), int(lm.y * img_h)

						# Get the 2D Coordinates
						face_2d.append([x, y])

						# Get the 3D Coordinates
						face_3d.append([x, y, lm.z])

				# Convert it to the NumPy array
				face_2d = np.array(face_2d, dtype=np.float64)

				# Convert it to the NumPy array
				face_3d = np.array(face_3d, dtype=np.float64)

				# The camera matrix
				focal_length = 1 * img_w

				cam_matrix = np.array([ [focal_length, 0, img_h / 2],
										[0, focal_length, img_w / 2],
										[0, 0, 1]])

				# The distortion parameters
				dist_matrix = np.zeros((4, 1), dtype=np.float64)

				# Solve PnP
				success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

				# Get rotational matrix
				rmat, jac = cv2.Rodrigues(rot_vec)

				# Get angles
				angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

				# Get the y rotation degree
				x = angles[0] * 360
				y = angles[1] * 360
				z = angles[2] * 360


				# See where the user's head tilting
				if y < -10:
					text = "Looking Left"
					ind="left"
				elif y > 10:
					text = "Looking Right"
					ind="right"
				elif x < -10:
					text = "Looking Down"
					ind="down"
				elif x > 10:
					text = "Looking Up"
					ind="up"
				elif( x > -10 and x < 10 and y > -10 and y < 10 ):
					text = "Forward"
					ind="forward"
				else:
					text = "Away"
					ind = "away"


				# Display the nose direction
				nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)

				p1 = (int(nose_2d[0]), int(nose_2d[1]))
				p2 = (int(nose_2d[0] + y * 10) , int(nose_2d[1] - x * 10))

				cv2.line(image, p1, p2, (255, 0, 0), 3)

				# Add the text on the image
				cv2.putText(image, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
				cv2.putText(image, "x: " + str(np.round(x,2)), (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
				cv2.putText(image, "y: " + str(np.round(y,2)), (500, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
				cv2.putText(image, "z: " + str(np.round(z,2)), (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


			end = time.time()
			totalTime = end - start

			#fps = 1 / totalTime
			#print("FPS: ", fps)

			#cv2.putText(image, f'FPS: {int(fps)}', (20,450), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)

			mp_drawing.draw_landmarks(
						image=image,
						landmark_list=face_landmarks,
						connections=mp_face_mesh.FACEMESH_CONTOURS,
						landmark_drawing_spec=drawing_spec,
						connection_drawing_spec=drawing_spec)

		# print(tcount)
		# print(atten_flag)
		cv2.imshow('Head Pose Estimation', image)
		if tcount==18*timeout:
			# while( cv2.waitKey(2) & 0xFF !=ord("x") or opencv_start_flag):
			while(opencv_start_flag):
				if(atten_flag):
					print("ALERT!! PAY ATTENTION!!")
					atten_flag = False
				break
				# playsound(r"C:\Users\Sidharth\Desktop\opencvatom\commitment.wav")
				# time.sleep(3)
			tcount=0
			continue
		
		elif ind in ["forward"]:
			atten_flag = True
			tcount = 0
			status = timeout
		elif ind in ["right","left","down"]:
			#print("looking right")
			atten_flag = False
			tcount+=1
		else:
			atten_flag = False
			tcount+=1



		if cv2.waitKey(5) & 0xFF == 27:
			break
	cv2.destroyAllWindows()
	cap.release()


# creates a separate thread for opencv program
# to prevent it interfering with the main server
def create_opencv_thread():
	global t1
	t1 =  threading.Thread(target=run_opencv, args=())
	t1.start()


# sample status check
@app.route("/check")
@cross_origin()
def check():
	global state, opencv_start_flag, atten_flag
	if(not atten_flag and opencv_start_flag):
		if(state > 0):
			state -= 1
		return(str(state))
	return("1")


# Checking whether user is paying attention
@app.route("/atten")
@cross_origin()
def atten():
	global atten_flag
	return(str(atten_flag))


# Acts like a switch to turn on opencv
@app.route("/stop", methods = ['POST', 'GET'])
def stop():
	global opencv_start_flag, t1, state
	# prev_start_flag = opencv_start_flag
	# post request received, toggle switch
	if( request.method == 'POST'):
		opencv_start_flag = not opencv_start_flag
		state = timeout
	# read status of opencv thread
	elif( request.method == 'GET'):
		return(str(opencv_start_flag))
	else:
		pass

	if(opencv_start_flag):
		create_opencv_thread()
	# elif(prev_start_flag):
	else:
		t1.join(timeout=1.0)
	return("Nothing")


# if __name__ == '__main__':
#	 run_opencv()

# @app.before_first_request

if __name__ == "__main__":
	app.run(host='127.0.0.1', port=5001)
	# camera.release()
	cv2.destroyAllWindows()	