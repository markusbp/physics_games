import numpy as np
import cv2
import PIL.Image, PIL.ImageTk
import tkinter as tk
from scipy import ndimage


class Screen(object):
    def __init__(self, x = 680, y = 480, source = 0):
        self.source = source
        self.cam = cv2.VideoCapture(source)
        self.x = x
        self.y = y

        if not self.cam.isOpened():
            raise ValueError('Cannot open camera!')

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.x);
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.y);
        self.width = self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print('Camera Resolution:', self.width, 'x', self.height)

    def terminator(self):
        self.cam.release()

    def get_cam_frame(self):
        if self.cam.isOpened():
            ret, frame = self.cam.read() # ret is int
        return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)) # Return ret for safety

class VelPong(object):
    def __init__(self, master, viewer, ball, thresh, w, h):
        self.master = master
        self.viewer = viewer
        self.ball = ball
        self.thresh = thresh
        self.w = w
        self.h = h
        self.score = np.zeros(2).astype(int)
        # Init screen/ label
        success, initframe = self.viewer.get_cam_frame()
        if success:
            self.previmg = initframe
            initframe = PIL.Image.fromarray(initframe)
            initframe = PIL.ImageTk.PhotoImage(initframe)
            self.imglab = tk.Label(image = initframe)
            self.imglab.image = initframe
            self.imglab.pack()
        self.stop = tk.Button(self.master, text = 'Stop', command = self.stop)
        self.stop.pack()
        # Update screen
        self.update()
        self.master.mainloop()

    def update(self):
        success, frame = self.viewer.get_cam_frame() # success if camera can aquire frame

        if success:
            gameframe = self.frame_change(frame) # Find change in image
            self.ball.position()  # Update ball position
            if self.ball.pos[0] <= 1:
                self.ball.v[0] = -self.ball.v[0]
                self.ball.pos[0] = 1
                self.score[0] = self.score[0] + 1
                print('Player 1:', self.score[0])
                print('Player 2:', self.score[1], '\n')

            if self.ball.pos[0] >= self.w - 1:
                self.ball.v[0] = -self.ball.v[0]
                self.ball.pos[0] = self.w - 1
                self.score[1] = self.score[1] + 1
                print('Player 1:', self.score[0])
                print('Player 2:', self.score[1], '\n')

            if self.ball.pos[1] <= 1:
                self.ball.v[1] = -self.ball.v[1]
                self.ball.pos[1] = 1

            if self.ball.pos[1] >= self.h - 1:
                self.ball.v[1] = -self.ball.v[1]
                self.ball.pos[1] = self.h - 1
            self.previmg = frame  # Set previous frame, for finding change

            x = int(self.ball.pos[0])
            y = int(self.ball.pos[1]) # Quantum ball

            gameframe, contours  = self.find_contours(gameframe, self.ball.pos)
            if np.array_equal(gameframe[y, x], [255, 0, 0]) or np.array_equal(gameframe[y, x], [255, 255, 255]):
                contour, ind = self.closest_contour(contours, self.ball.pos)
                #np.save('contourtest.npy', contour) # For testing contours and normal vectors
                xx = contour[:,0,0]
                yy = contour[:,0,1]
                u = np.zeros((len(xx), 3))
                try:
                    # Find normal vector of surface at collision
                    u[:,0] = np.gradient(xx)
                    u[:,1] = np.gradient(yy)
                    u[:, 2] = 1
                    z = np.array([0, 0, 1])
                    uu = u[:, 0]
                    v = np.cross(u, z)[:, :2] # Keep only x, y, gives normal vector to contour
                    normal  = -v[ind]
                    norm = np.linalg.norm(normal)
                    if norm == 0:
                        self.ball.v = -self.ball.v
                    else:
                        dir = normal/norm
                        self.ball.v = np.linalg.norm(self.ball.v)*dir#*2 # Change only ball direction
                        self.ball.pos = np.array([contour[ind, 0, 0], contour[ind, 0, 1]]) + dir # Teleport ball to safety
                except:
                    print('I made a boboo') # Oops
                    normal = -self.ball.v # Better to just fling it off
            #gameframe = frame # Regular camera view
            cv2.circle(gameframe,(x, y), 10, (0, 212, 49), -1) # Draw ball
            photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv2.flip(gameframe,1)))
            self.imglab.configure(image = photo)
            self.imglab.image = photo # Label image

        self.master.after(1, self.update) # Update GUI

    def frame_change(self, img):
        # Convert as inefficiently as possible
        img = np.int8(img)
        previmg = np.int8(self.previmg)
        change = np.abs(img - previmg)
        change = cv2.medianBlur(np.uint8(change),53)
        change[change < self.thresh] = 0
        change[change >= self.thresh] = 255
        return change

    def find_contours(self, img, pos):
        # Finds contours, uses simple contour approximation to save space
        contours, hier = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return cv2.drawContours(img, contours, -1, (255, 0, 0), 12), contours

    def closest_contour(self, contours, pos):
        # Finds the contour and closest location in it to ball position (pos)
        closest_contour = contours[0] # First guess
        closest = 0 # First guess, index
        mindist = 1e6 # Big initial value
        for num, contour in enumerate(contours):
            distance = np.linalg.norm(pos - contour[:, 0], axis = 1)
            closeind = np.argmin(distance)
            if distance[closeind] < mindist:
                closest = closeind
                mindist = distance[closeind]
                closest_contour = contours[num]
        return closest_contour, closest

    def stop(self):
        self.viewer.terminator()
        self.master.destroy()

class Ball(object):
    def __init__(self, pos, v0, dt):
        self.dt = dt
        self.v = v0
        self.pos = pos

    def position(self):
        # Updates ball position
        self.v = self.v#*0.92 + np.array([0, 1300])
        self.pos =  self.pos + self.v*self.dt

if __name__ == '__main__':
    w = 640; h = 480
    screen = Screen(w, h, source = 0)
    master = tk.Tk()
    x0 = np.array([int(w/2), int(h/2)])
    v0 = np.array([-1, 2])*10000
    ball = Ball(x0, v0, dt = 0.001)
    viewer = VelPong(master, screen, ball, thresh = 10, w = w, h = h)
