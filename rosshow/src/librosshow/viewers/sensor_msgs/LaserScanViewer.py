import math
import time

import librosshow.termgraphics as termgraphics

class LaserScanViewer(object):
    def __init__(self, title = ""):
        self.g = termgraphics.TermGraphics()
        self.scale = 10.0
        self.target_scale = 10.0
        self.target_scale_time = 0
        self.msg = None
        self.last_update_shape_time = 0
        self.title = title

    def keypress(self, c):
        if c == "[":
            self.target_scale *= 1.5
            self.target_scale_time = time.time()
        elif c == "]":
            self.target_scale /= 1.5
            self.target_scale_time = time.time()

    def update(self, msg):
        self.msg = msg

    def draw(self):
        if not self.msg:
            return

        t = time.time()

        # capture changes in terminal shape at least every 0.25s
        if t - self.last_update_shape_time > 0.25:
            self.g.update_shape()
            self.last_update_shape_time = t

        # animation over 0.5s when zooming in/out
        if self.scale != self.target_scale:
            animation_fraction = (time.time() - self.target_scale_time) / 0.5
            if animation_fraction > 1.0:
                self.scale = self.target_scale
            else:
                self.scale = (1 - animation_fraction) * self.scale + animation_fraction * self.target_scale

        self.g.clear()
        self.g.set_color(termgraphics.COLOR_WHITE)

        w = self.g.shape[0]
        h = self.g.shape[1]

        xmax = self.scale
        ymax = self.scale * h/w

        for n in range(len(self.msg.ranges)):
            if math.isinf(self.msg.ranges[n]) or math.isnan(self.msg.ranges[n]):
                continue
            x = self.msg.ranges[n]*math.cos(self.msg.angle_min + n*self.msg.angle_increment)
            y = self.msg.ranges[n]*math.sin(self.msg.angle_min + n*self.msg.angle_increment)
            i = int(w * (x + xmax) / (2 * xmax))
            j = int(h * (1 - (y + ymax) / (2 * ymax)))
            self.g.point((i, j))

        if self.title:
            self.g.set_color((0, 127, 255))
            self.g.text(self.title, (0, self.g.shape[1] - 4))
        self.g.draw()

        self.g.draw()
