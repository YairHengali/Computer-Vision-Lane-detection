import numpy as np
import cv2

#draw the current lane on res frame by r_rho, l_rho, r_theta, l_theta, move, shape.
def draw_lane(res, r_rho, l_rho, r_theta, l_theta, move, shape):
    y = 50
    x = (r_rho- y*np.sin(r_theta))/np.cos(r_theta)+move//3 #calculated by rho and theta, added move parameter to match to lane change
    r_dot_1 = [x,y+res.shape[0]//2]
    x = (l_rho- y*np.sin(l_theta))/np.cos(l_theta)+move//3 #calculated by rho and theta, added move parameter to match to lane change
    l_dot_1 = [x,y+res.shape[0]//2]
    y =  res.shape[0] // 2
    x=(r_rho- y*np.sin(r_theta))/np.cos(r_theta)+move+shape #calculated by rho and theta, added move and shape parameters to match to lane change
    r_dot_2 = [x,y+res.shape[0]//2]
    x = (l_rho- y*np.sin(l_theta))/np.cos(l_theta)+move+shape #calculated by rho and theta, added move and shape parameters to match to lane change
    l_dot_2 = [x,y+res.shape[0]//2]
    points = [np.array([r_dot_1, r_dot_2, l_dot_2, l_dot_1])]
    overlay = res.copy()
    res = cv2.fillPoly(res, pts=np.int32(points), color=(255, 0, 0)) #draw lane by dots calculated above
    alpha = 0.4 #for transparency
    res = cv2.addWeighted(overlay, alpha, res, 1 - alpha, 0)
    return res

#preproccessing frame and return lines found by HoughLines on it.
def find_lines(frame):
    cropped_frame = frame[frame.shape[0]//2:,:]
    gray_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
    th_frame = np.where(gray_frame > 160, 255, 0)

    canny_frame = cv2.Canny(np.uint8(th_frame), 80, 130)

    lines = cv2.HoughLines(canny_frame, 1, np.pi / 180, 75)

    return lines

video_name = "input_video.mp4"
cap = cv2.VideoCapture(video_name)

ret, frame = cap.read()
height, width, layers = frame.shape
frameSize=(width, height)
fps = cap.get(cv2.CAP_PROP_FPS)
video_out = cv2.VideoWriter('output_video.avi',fourcc=cv2.VideoWriter_fourcc(*'DIVX'),fps=fps, frameSize=frameSize)

#range for r_rhos and l_rhos
r_rho_min = -365
r_rho_max = -250
l_rho_max = 387
l_rho_min = 302

move = 0
shape = 0

font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 1
fontColor = (0,0,0)

while(ret): #for each frame:
    lines = find_lines(frame)

    res = frame.copy()
    left_border = False
    right_border = False
    for r_t in lines:  #finding valid theta
        rho = r_t[0, 0]
        theta = r_t[0, 1]
        if (right_border and left_border):
            break
        elif not right_border and np.pi-np.pi/3.3 < theta < np.pi-np.pi/4.01:
            r_rho = rho
            r_theta = theta
            right_border = True
        elif not left_border and np.pi/4.7 < theta < np.pi/3.5:
            l_rho = rho
            l_theta = theta
            left_border = True


    if r_rho_min <= r_rho <= r_rho_max and l_rho_min <= l_rho <= l_rho_max: #if rhos in range
        move = 0
        shape = 0
    elif r_rho > r_rho_max or l_rho < l_rho_min:
        move -= 1.4
        shape -= 1.2
        res = cv2.putText(res, "Moving to right lane", (30, 70), font, fontScale, fontColor,2)
    else:
        move += 4
        shape += 2
        res = cv2.putText(res, "Moving to left lane", (30, 70), font, fontScale, fontColor,2)

    res = draw_lane(res, r_rho, l_rho, r_theta, l_theta,  move, shape)    
    video_out.write(res)
    ret, frame = cap.read()


cap.release()
video_out.release()

