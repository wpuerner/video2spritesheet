from tkinter import *


def gui(command_queue, frames_length):

    root = Tk()

    frame = Frame(root)
    frame.pack()

    scale = DoubleVar()
    scale.set(1.0)
    scale.trace_add('write', lambda var, index, mode: command_queue.put(
        {"command": "update", "key": "scale", "value": scale.get()}))
    Scale(root, from_=0.05, to=1.0, resolution=0.01,
          label="Scale", orient=HORIZONTAL, variable=scale, length=500).pack()

    sprite_size = IntVar()
    sprite_size.set(8)
    sprite_size.trace_add('write', lambda var, index, mode: command_queue.put(
        {"command": "update", "key": "sprite_size", "value": sprite_size.get()}))
    Scale(root, from_=4, to=128, label="Sprite Size",
          orient=HORIZONTAL, variable=sprite_size, length=500).pack()

    sprite_pos_x = IntVar()
    sprite_pos_x.set(0)
    sprite_pos_x.trace_add('write', lambda var, index, mode: command_queue.put(
        {"command": "update", "key": "sprite_pos_x", "value": sprite_pos_x.get()}))
    Scale(root, from_=0, to=800, label="Sprite Pos X",
          orient=HORIZONTAL, variable=sprite_pos_x, length=500).pack()

    sprite_pos_y = IntVar()
    sprite_pos_y.set(0)
    sprite_pos_y.trace_add('write', lambda var, index, mode: command_queue.put(
        {"command": "update", "key": "sprite_pos_y", "value": sprite_pos_y.get()}))
    Scale(root, from_=0, to=800, label="Sprite Pos Y",
          orient=HORIZONTAL, variable=sprite_pos_y, length=500).pack()

    start_frame = IntVar()
    start_frame.set(0)
    start_frame.trace_add('write', lambda var, index, mode: command_queue.put(
        {"command": "update", "key": "start_frame", "value": start_frame.get()}))
    Scale(root, from_=0, to=frames_length-2, label="Start Frame",
          orient=HORIZONTAL, variable=start_frame, length=500).pack()

    end_frame = IntVar()
    end_frame.set(frames_length-1)
    end_frame.trace_add('write', lambda var, index, mode: command_queue.put(
        {"command": "update", "key": "end_frame", "value": end_frame.get()}))
    Scale(root, from_=1, to=frames_length-1, label="End Frame",
          orient=HORIZONTAL, variable=end_frame, length=500).pack()

    def save():
        command_queue.put({"command": "save"})
        root.destroy()
        return
    Button(root, text="Save", command=save).pack()

    def exit():
        command_queue.put({"command": "exit"})
        root.destroy()
        return
    Button(root, text="Exit", command=exit).pack()

    mainloop()
