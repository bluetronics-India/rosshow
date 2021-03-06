#!/usr/bin/env python3

import time
import numpy as np
import sensor_msgs.point_cloud2 as pcl2
import librosshow.termgraphics as termgraphics

class PointCloud2Viewer(object):
    def __init__(self, title = ""):
        self.g = termgraphics.TermGraphics()
        self.scale = 20
        self.spin = 0.0
        self.tilt = 3.14159 * 2/3
        self.target_scale = self.scale
        self.target_spin = self.spin
        self.target_tilt = self.tilt
        self.target_time = 0
        self.calculate_rotation()
        self.msg = None
        self.last_update_shape_time = 0
        self.title = title

    def keypress(self, c):
        if c == "[":
            self.target_scale *= 1.5
        elif c == "]":
            self.target_scale /= 1.5
        elif c == "1":
            self.target_spin -= 0.1
        elif c == "2":
            self.target_spin += 0.1
        elif c == "3":
            self.target_tilt -= 0.1
        elif c == "4":
            self.target_tilt += 0.1

        self.target_time = time.time()

        self.calculate_rotation()

    def calculate_rotation(self):
        rotation_spin = \
          np.array([[np.cos(self.spin), -np.sin(self.spin), 0],
                    [np.sin(self.spin), np.cos(self.spin), 0],
                    [0, 0, 1]], dtype = np.float16)

        rotation_tilt = \
          np.array([[1, 0, 0],
                    [0, np.cos(self.tilt), -np.sin(self.tilt)],
                    [0, np.sin(self.tilt), np.cos(self.tilt)]], dtype = np.float16)

        self.rotation = np.matmul(rotation_tilt, rotation_spin)

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
        if self.scale != self.target_scale or self.tilt != self.target_tilt or self.spin != self.target_spin:
            animation_fraction = (time.time() - self.target_time) / 1.0
            if animation_fraction > 1.0:
                self.scale = self.target_scale
                self.tilt = self.target_tilt
                self.spin = self.target_spin
            else:
                self.scale = (1 - animation_fraction) * self.scale + animation_fraction * self.target_scale
                self.tilt = (1 - animation_fraction) * self.tilt + animation_fraction * self.target_tilt
                self.spin = (1 - animation_fraction) * self.spin + animation_fraction * self.target_spin
            self.calculate_rotation()

        points = np.array(list(pcl2.read_points(self.msg, skip_nans = True, field_names = ("x", "y", "z"))), dtype = np.float16)
        self.g.clear()
        w = self.g.shape[0]
        h = self.g.shape[1]
        xmax = self.scale
        ymax = xmax * h/w
        rot_points = np.matmul(self.rotation, points.T).T
        screen_is = ((0.5 * w + rot_points[:,0] * self.scale)).astype(np.int16)
        screen_js = ((0.5 * h - rot_points[:,1] * self.scale)).astype(np.int16)
        zmax = np.max(points[:,2])
        zmin = np.min(points[:,2])
        screen_c =  np.clip((255.0 / 8 * (points[:,2] + 5)), 0.0, 255.0).astype(np.uint8)
        where_valid = (screen_is > 0) & (screen_js > 0) & (screen_is < w) & (screen_js < h)
        screen_is = screen_is[where_valid]
        screen_js = screen_js[where_valid]
        screen_c = screen_c[where_valid]
        last_c = None
        for i in range(screen_is.shape[0]):
            if screen_c[i] != last_c:
                self.g.set_color((255, screen_c[i], screen_c[i]))
                last_c = screen_c[i]
            self.g.point((screen_is[i], screen_js[i]))

        if self.title:
            self.g.set_color((0, 127, 255))
            self.g.text(self.title, (0, self.g.shape[1] - 4))

        self.g.draw()

