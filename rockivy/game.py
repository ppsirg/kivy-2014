from collections import namedtuple
import math
from random import random as rand, choice as randc

from kivy.clock import Clock
from kivy.graphics import Mesh
from kivy.graphics.instructions import RenderContext
from kivy.uix.widget import Widget

from .util import load_tex_uv

CURSOR_OFFSET_X = 16
CURSOR_OFFSET_Y = -16

R9 = namedtuple('Renderable', 'x y rot size op tex')

g_window = None


class Game(Widget):
    '''Game renderer'''

    def __init__(self, **kwargs):
        self.canvas = RenderContext(use_parent_projection=True)
        self.canvas.shader.source = 'multiquad.glsl'

        Widget.__init__(self, **kwargs)

        self.vertex_format = (
            ('vCenter', 2, 'float'),
            ('vRotation', 1, 'float'),
            ('vScale', 1, 'float'),
            ('vOpacity', 1, 'float'),
            ('vPosition', 2, 'float'),
            ('vTexCoords0', 2, 'float'),
        )
        self.tex, self.tex_uv = load_tex_uv('a.atlas')

        Clock.schedule_interval(self.update_glsl, 60 ** -1)

        from kivy.core.window import Window
        global g_window
        g_window = Window

    def update_glsl(self, nap):
        self.canvas.clear()
        objects = self.random_fill(96)
        cur_x, cur_y = g_window.mouse_pos
        objects.append(R9(x=cur_x + CURSOR_OFFSET_X,
                          y=cur_y + CURSOR_OFFSET_Y,
                          rot=0, size=1, op=1, tex='cursor'))
        self.render(objects)

    def random_fill(self, count):
        width, height = self.size
        tex_list = self.tex_uv.keys()
        return [R9(x=rand() * width,
                   y=rand() * height,
                   rot=rand() * math.pi * 2,
                   size=rand() + 0.5,
                   op=rand() + 0.5,
                   tex=randc(tex_list)) for c in xrange(count)]

    def render(self, objects):
        indices = []
        ix = indices.extend
        for c in xrange(0, len(objects) << 2, 4):
            ix((c, c + 1, c + 2, c + 2, c + 3, c))

        vertices = []
        vx = vertices.extend
        for o in objects:
            uv = self.tex_uv[o[5]]
            vx((
                o[0], o[1], o[2], o[3], o[4], -uv[4], -uv[5], uv[0], uv[1],
                o[0], o[1], o[2], o[3], o[4],  uv[4], -uv[5], uv[2], uv[1],
                o[0], o[1], o[2], o[3], o[4],  uv[4],  uv[5], uv[2], uv[3],
                o[0], o[1], o[2], o[3], o[4], -uv[4],  uv[5], uv[0], uv[3],
            ))

        self.canvas.add(Mesh(indices=indices, vertices=vertices,
                             fmt=self.vertex_format, mode='triangles',
                             texture=self.tex))
