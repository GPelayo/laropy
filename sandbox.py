"""
DON"T COMMIT MEEEEEE
"""

import pyglet
import random
import math


class GLShape:
    def draw(self):
        raise NotImplementedError


class Rectangle(GLShape):
    def __init__(self, left_x, top_y, length, width):
        self.x = left_x
        self.y = top_y
        self._length = length
        self._width = width

    def draw(self):
        pyglet.graphics.vertex_list(4, ('v2f', [self.x, self.y,
                                                self.x + self._width, self.y,
                                                self.x + self._width, self.y + self._length,
                                                self.x, self.y + self._length]))


class Graphic:
    def __init__(self, width, length):
        self.x = 0
        self.y = 0
        self._length = width
        self._width = length

    def draw(self):
        pass

    @property
    def length(self):
        return self._length

    @property
    def width(self):
        return self._width

    def resize(self, width, length):
        self._length = width
        self._width = length

    def move(self, x, y):
        self.x = x
        self.y = y

    def move_offset(self, x, y):
        self.x += x
        self.y += y


class GLDrawnGraphic(Graphic):
    def __init__(self, width, length):
        super().__init__(width, length)
        self.shape_list = []

    def add_shape(self, shape: GLShape):
        self.shape_list.append(shape)


class GameObject:
    def __init__(self, name, graphic: Graphic):
        self.name = name
        self.x = 0
        self.y = 0
        self._graphic = graphic
        self._graphic.x = self.x
        self._graphic.x = self.y
        self._data_lib = DataLibrary()
        self._component_list = []
        self._tick = 0
        self._max_tick = 10000

    def update(self, tick):
        if self._tick > 10000:
            self._tick = 0
        self._tick += 1

        for cmp in self._component_list:
            cmp.update(self, tick)

    def draw(self):
        self._graphic.draw()

    def resize(self, width, length):
        self._graphic.resize(width, length)

    def move(self, x, y):
        self.x = x
        self.y = y
        self._graphic.move(x, y)

    def move_offset(self, x, y):
        self.x += x
        self.y += y
        self._graphic.move_offset(x, y)


class GameComponent:
    name = None

    def __init__(self, environment):
        self.env = environment

    def update(self, obj: GameObject, tick):
        raise NotImplementedError


def init_empty_gen():
    yield


class ZeroDistanceError(Exception):
    message = "Distance is zero."


test_path = []


def create_path(org_x, org_y, dest_x, dest_y, speed):
    global test_path
    time_to_dest = math.sqrt(math.pow(dest_y - org_y, 2) + math.pow(dest_y - org_y, 2))/speed

    if time_to_dest <= 0:
        raise ZeroDistanceError

    step_size_y = (dest_y - org_y) / time_to_dest
    step_size_x = (dest_x - org_x) / time_to_dest

    test_path = [(step_size_x * step + org_x, step_size_y * step + org_y)
                 for step in range(1, math.floor(time_to_dest) + 1)]

    return (path for path in test_path)


class WanderComponent(GameComponent):
    name = 'Wander'

    def __init__(self, speed, environment):
        super().__init__(environment)
        self.speed = speed
        self.destination_x = 0
        self.destination_y = 0
        self.random = random.Random()
        self.cur_step = 0
        self.path = init_empty_gen()
        self.max_distance = 100
        self.max_x = environment.width
        self.max_y = environment.length

    def get_path(self, obj: GameObject, farthest_left, farthest_right, farthest_south, farthest_north):
        while True:
            self.destination_x = obj.x + self.random.randint(farthest_left, farthest_right)
            self.destination_y = obj.y + self.random.randint(farthest_south, farthest_north)
            if self.destination_y - obj.y != 0 and self.destination_x - obj.x != 0 \
                    and 0 <= self.destination_x <= self.max_x and 0 <= self.destination_y < self.max_y:
                    break

        self.path = create_path(obj.x, obj.y, self.destination_x, self.destination_y, self.speed)

    def update(self, obj: GameObject, tick):
        next_step = next(self.path, None)
        if next_step:
            obj.move(next_step[0], next_step[1])
        else:
            self.get_path(obj, -self.max_distance, self.max_distance, -self.max_distance, self.max_distance)


class Environment:
    game_objects = []

    def __init__(self, window):
        self.width = window.width
        self.length = window.height

    def add_object(self, obj):
        self.game_objects.append(obj)

    def update_objects(self, dt):
        for obj in self.game_objects:
            obj.update(dt)

    def draw_objects(self):
        for obj in self.game_objects:
            obj.draw()


class SpriteGraphic(Graphic):
    def __init__(self, image_location: str, width, length):
        super().__init__(width, length)
        self._image = pyglet.image.load(image_location)
        self._sprite = pyglet.sprite.Sprite(self._image)
        self.resize(width, length)

    def draw(self):
        self._sprite.draw()

    def resize(self, width, length):
        self._image.get_texture().width = width
        self._image.get_texture().height = length
        self._image.height = length
        self._image.width = width
        self._width = width
        self._length = length
        self._sprite = pyglet.sprite.Sprite(self._image)

    def move(self, x, y):
        super().move(x, y)
        self._sprite.set_position(x, y)

    def move_offset(self, x, y):
        super().move_offset(x, y)
        self._sprite.set_position(self.x + x, self.y + y)


class DataLibrary:
    def __init__(self):
        self.data_list = {}

    def add_data(self, component: GameComponent, field_name, data):
        self.data_list.setdefault(component.name, {})[field_name] = data

    def get_entry(self, component: GameComponent, field_name):
        return self.data_list[component.name][field_name]


class Tangle(GameObject):
    def __init__(self):
        global env
        super().__init__(self, SpriteGraphic('images.png', 25, 25))
        self._component_list.append(WanderComponent(2, env))
        self.move(250, 250)

w = pyglet.window.Window()
env = Environment(w)
env.add_object(Tangle())


@w.event
def on_draw():
    global env
    global test_path
    w.clear()
    env.draw_objects()
    for point in test_path:
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
                             ('v2i', (int(point[0]) + 12, int(point[1]) + 12)),
                             ('c3B', (255, 255, 255))
                             )

def update_environment(dt):
    env.update_objects(dt)

pyglet.clock.schedule_interval(update_environment, 1/100.0)
pyglet.app.run()
