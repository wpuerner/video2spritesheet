import cv2 as cv
import imutils
import fire
import threading
from tkinter import *
import sys
import time

mutations = {
    'scale': 1,
    'contrast': 1,
    'brightness': 0
}
save = False
exit_app = False


class Video2Spritesheet:

    def mutate(self, frame):
        # there is an issue with color correction that affects the alpha channel
        frame = cv.convertScaleAbs(
            frame, alpha=contrast.get(), beta=brightness.get())

        fwidth = int(frame.shape[1] * scale.get())
        fheight = int(frame.shape[0] * scale.get())
        dim = (fwidth, fheight)
        frame = cv.resize(frame, dim, interpolation=cv.INTER_AREA)

        return frame

    def process(self, ifile, name, debug=False):

        cap = cv.VideoCapture('testdata/' + ifile)

        height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

        owidth = 800
        oheight = height

        fgbg = cv.bgsegm.createBackgroundSubtractorMOG()

        frames = []
        while True:
            ret, frame = cap.read()
            if frame is None:
                break

            fgmask = fgbg.apply(frame)
            frame = cv.cvtColor(frame, cv.COLOR_BGR2BGRA)
            frame = cv.bitwise_and(frame, frame, mask=fgmask)

            points = []
            contours = cv.findContours(
                fgmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)
            for contour in contours:
                moments = cv.moments(contour)
                if moments['m00'] != 0:
                    c_x = int(moments["m10"] / moments["m00"])
                    c_y = int(moments["m01"] / moments["m00"])
                    points.append(
                        {"x": c_x, "y": c_y, "area": cv.contourArea(contour)})
                    if debug:
                        cv.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                        cv.circle(frame, (c_x, c_y), 7, (255, 255, 255), -1)

            if len(points) == 0:
                continue   # skip this frame if we can't find a center

            center = {'x': int(sum([point['x'] * point['area']
                                    for point in points]) / sum([point['area'] for point in points])),
                      'y': int(sum([point['y'] * point['area']
                                    for point in points]) / sum([point['area'] for point in points]))}
            if debug:
                cv.circle(
                    frame, (center['x'], center['y']), 20, (0, 0, 255), -1)

            frame = cv.copyMakeBorder(frame, 0, 0, int(owidth/2), int(owidth/2),
                                      cv.BORDER_CONSTANT, value=[0, 0, 0])
            center['x'] = center['x'] + int(owidth/2)
            frame = frame[0:oheight, int(
                center['x']-owidth/2):int(center['x']+owidth/2)]

            frames.append(frame)

        cap.release()

        gui = threading.Thread(target=self.gui, args=[len(frames)], name='gui')
        gui.start()

        # wait for the gui to initialize globals
        time.sleep(3)

        i = 0
        while True:
            if save:
                break
            if exit_app:
                cv.destroyAllWindows()
                sys.exit()
            if i < start_frame.get():
                i = start_frame.get()

            frame = self.mutate(frames[i])

            cv.rectangle(frame, (sprite_pos_x.get(), sprite_pos_y.get()), (sprite_pos_x.get(
            )+sprite_size.get(), sprite_pos_y.get()+sprite_size.get()), color=(0, 0, 255), thickness=1)

            cv.imshow("Preview", cv.resize(
                frame, (owidth, oheight), interpolation=cv.INTER_NEAREST))
            cv.waitKey(30)
            i = i + 1
            if i == len(frames) or i > end_frame.get():
                i = 0

        for i in range(start_frame.get(), end_frame.get()+1):
            frame = self.mutate(frames[i])
            frame = frame[sprite_pos_x.get():sprite_pos_x.get(
            )+sprite_size.get(), sprite_pos_y.get():sprite_pos_y.get()+sprite_size.get()]
            cv.imwrite("output/" + name + "_" + str(i) + ".png", frame)

        cv.destroyAllWindows()

    def info(self, input):
        cap = cv.VideoCapture('testdata/' + input)
        print("=== Video Settings for ", input, "===")
        print("Width      ", cap.get(cv.CAP_PROP_FRAME_WIDTH))
        print("Height     ", cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        print("Frames     ", cap.get(cv.CAP_PROP_FRAME_COUNT))
        print("FPS        ", cap.get(cv.CAP_PROP_FPS))
        cap.release()

    def gui(self, frames_length):

        def save():
            global save
            save = True

        def exit():
            root.destroy()
            global exit_app
            exit_app = True

        root = Tk()

        frame = Frame(root)
        frame.pack()

        global scale
        scale = DoubleVar()
        scale.set(1.0)
        Scale(root, from_=0.05, to=1.0, resolution=0.01,
              label="Scale", orient=HORIZONTAL, variable=scale, length=500).pack()

        global brightness
        brightness = IntVar()
        brightness.set(0)
        Scale(root, from_=-127, to=127,
              label="Brightness", orient=HORIZONTAL, variable=brightness, length=500).pack()

        global contrast
        contrast = DoubleVar()
        contrast.set(1.0)
        Scale(root, from_=0.0, to=3.0, resolution=0.01,
              label="Contrast", orient=HORIZONTAL, variable=contrast, length=500).pack()

        global sprite_size
        sprite_size = IntVar()
        sprite_size.set(8)
        Scale(root, from_=4, to=128, label="Sprite Size",
              orient=HORIZONTAL, variable=sprite_size, length=500).pack()

        global sprite_pos_x
        sprite_pos_x = IntVar()
        sprite_pos_x.set(0)
        Scale(root, from_=0, to=800, label="Sprite Pos X",
              orient=HORIZONTAL, variable=sprite_pos_x, length=500).pack()

        global sprite_pos_y
        sprite_pos_y = IntVar()
        sprite_pos_y.set(0)
        Scale(root, from_=0, to=800, label="Sprite Pos Y",
              orient=HORIZONTAL, variable=sprite_pos_y, length=500).pack()

        global start_frame
        start_frame = IntVar()
        start_frame.set(0)
        Scale(root, from_=0, to=frames_length-2, label="Start Frame",
              orient=HORIZONTAL, variable=start_frame, length=500).pack()

        global end_frame
        end_frame = IntVar()
        end_frame.set(frames_length-1)
        Scale(root, from_=1, to=frames_length-1, label="End Frame",
              orient=HORIZONTAL, variable=end_frame, length=500).pack()

        Button(root, text="Save", command=save).pack()
        Button(root, text="Exit", command=exit).pack()

        mainloop()


if __name__ == '__main__':
    fire.Fire(Video2Spritesheet)
