import cv2 as cv
import imutils
import fire
import threading
from tkinter import *
import sys

mutations = {
    'scale': 1,
    'contrast': 1,
    'brightness': 0
}
save = False
exit_app = False


class Video2Spritesheet:
    def process(self, ifile, ofile, debug=False):
        gui = threading.Thread(target=self.gui, name='gui')
        gui.start()

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

        i = 0
        while True:
            if save:
                break
            if exit_app:
                cv.destroyAllWindows()
                sys.exit()

            frame = frames[i]

            frame = cv.convertScaleAbs(
                frame, alpha=mutations['contrast'], beta=mutations['brightness'])

            fwidth = int(frame.shape[1] * mutations['scale'])
            fheight = int(frame.shape[0] * mutations['scale'])
            dim = (fwidth, fheight)
            frame = cv.resize(frame, dim, interpolation=cv.INTER_AREA)

            cv.imshow("Preview", cv.resize(
                frame, (owidth, oheight), interpolation=cv.INTER_NEAREST))
            cv.waitKey(30)
            i = i + 1
            if i == len(frames):
                i = 0

        output = cv.VideoWriter("output/" + ofile,
                                cv.VideoWriter_fourcc(*'mp4v'), 20.0, (owidth, oheight))
        for frame in frames:
            output.write(frame)
        output.release()

        cv.destroyAllWindows()

    def info(self, input):
        cap = cv.VideoCapture('testdata/' + input)
        print("=== Video Settings for ", input, "===")
        print("Width      ", cap.get(cv.CAP_PROP_FRAME_WIDTH))
        print("Height     ", cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        print("Frames     ", cap.get(cv.CAP_PROP_FRAME_COUNT))
        print("FPS        ", cap.get(cv.CAP_PROP_FPS))
        cap.release()

    def gui(self):
        def update():
            mutations['scale'] = scale.get()
            mutations['contrast'] = contrast.get()
            mutations['brightness'] = brightness.get()

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

        scale = Scale(root, from_=0.05, to=1.0, resolution=0.01,
                      label="Scale", orient=HORIZONTAL)
        scale.set(1.0)
        scale.pack()
        contrast = Scale(root, from_=0.0, to=3.0, resolution=0.01,
                         label="Contrast", orient=HORIZONTAL)
        contrast.set(1.0)
        contrast.pack()
        brightness = Scale(root, from_=-127, to=127,
                           label="Brightness", orient=HORIZONTAL)
        brightness.set(0)
        brightness.pack()

        Button(root, text="update", command=update).pack()
        Button(root, text="Save", command=save).pack()
        Button(root, text="Exit", command=exit).pack()

        mainloop()


if __name__ == '__main__':
    fire.Fire(Video2Spritesheet)
