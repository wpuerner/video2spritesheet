import cv2 as cv
import imutils


def process_raw(filename, debug):
    cap = cv.VideoCapture('testdata/' + filename)

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

    return frames, oheight, owidth


def preview_frames(command_queue, frames, name, owidth, oheight):

    params = {
        "scale": 1,
        "start_frame": 0,
        "end_frame": len(frames) - 1,
        "sprite_pos_x": 0,
        "sprite_pos_y": 0,
        "sprite_size": 8
    }

    i = 0
    while True:
        while not command_queue.empty():
            command = command_queue.get()
            if (command["command"] == "exit"):
                cv.destroyAllWindows()
                return
            elif (command["command"] == "update"):
                params[command["key"]] = command["value"]

        if i < params['start_frame']:
            i = params['start_frame']

        frame = frames[i]

        fwidth = int(frame.shape[1] * params['scale'])
        fheight = int(frame.shape[0] * params['scale'])
        dim = (fwidth, fheight)
        frame = cv.resize(frame, dim, interpolation=cv.INTER_AREA)

        cv.rectangle(frame, (params['sprite_pos_x'], params['sprite_pos_y']), (params['sprite_pos_x'] +
                     params['sprite_size'], params['sprite_pos_y']+params['sprite_size']), color=(0, 0, 255), thickness=1)

        cv.imshow("Preview", cv.resize(
            frame, (owidth, oheight), interpolation=cv.INTER_NEAREST))
        cv.waitKey(30)
        i = i + 1
        if i == len(frames) or i > params['end_frame']:
            i = 0

    # for i in range(start_frame.get(), end_frame.get()+1):
    #     frame = self.mutate(frames[i])
    #     frame = frame[sprite_pos_x.get():sprite_pos_x.get(
    #     )+sprite_size.get(), sprite_pos_y.get():sprite_pos_y.get()+sprite_size.get()]
    #     cv.imwrite("output/" + name + "_" + str(i) + ".png", frame)
