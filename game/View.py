import numpy as np
import pyglet
from pyglet.gl import glClearColor, glClear, glColor4f, GL_LINE_LOOP
from math import radians, cos, sin

GREEN = list(np.array([0, 255, 0, 123]))
BLUE = list(np.array([0, 0, 128, 255]))
BLACK = list(np.array([0, 0, 0, 255]))


class PygletWindow:
    def __init__(self, X, Y):
        self.active = True
        self.display_surface = pyglet.window.Window(width=X, height=Y + 50)
        glClearColor(255, 255, 255, 1.0)
        self.top = Y

        self.display_surface.switch_to()
        self.reset()

    def circle(self, x_pos, y_pos, radius, color, thickness, numPoints=100):
        verts = []
        y_pos = self.top - y_pos
        glColor4f(*[int(c) for c in color])
        for i in range(numPoints):
            angle = radians(float(i) / numPoints * 360.0)
            x = radius * cos(angle) + x_pos
            y = radius * sin(angle) + y_pos
            verts += [x, y]
        circle = pyglet.graphics.vertex_list(numPoints, ('v2f', verts))
        circle.draw(GL_LINE_LOOP)

    def text(self, text, x, y, font_size=20, color=None):
        y = self.top - y
        label = pyglet.text.Label(text, font_name='Times New Roman', font_size=font_size,
                                  x=x, y=y, anchor_x='left', anchor_y='top',
                                  color=[int(c) for c in color])
        label.draw()

    def rectangle(self, x, y, dx, dy, color):
        y = self.top - y
        x = int(round(x))
        y = int(round(y))
        glColor4f(*[int(c) for c in color])
        rect = pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [x, y, x + dx, y, x + dx, y + dy, x, y + dy]))
        rect.draw()

    def reset(self):
        pyglet.clock.tick()
        self.display_surface.dispatch_events()
        glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)

    def update(self):
        self.display_surface.flip()