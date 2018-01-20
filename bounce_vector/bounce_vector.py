import kivy
kivy.require('1.10.1')  # replace with your current kivy version !

from kivy.lang import Builder
from kivy.app import App
from kivy.graphics import Line
from kivy.uix.widget import Widget
from kivy.properties import (NumericProperty,
                             ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock


Builder.load_file('bounce_vector.kv')


class Paddle(Widget):
    score = NumericProperty(0)
    bounce_vector = None

    def attach_bounce_vector(self, touch):
        start_pos = self.get_start_position(touch)
        end_pos = self.get_end_position(start_pos, touch)

        self.bounce_vector = BounceVector(points=[start_pos[0], start_pos[1],
                                                  end_pos[0], end_pos[1]])
        self.add_widget(self.bounce_vector)

        self.bounce_vector.center = start_pos

    def detach_bounce_vector(self):
        self.remove_widget(self.bounce_vector)
        self.bounce_vector = None

    def move_bounce_vector(self, touch):
        if self.bounce_vector is not None:
            start_pos = self.get_start_position(touch)
            end_pos = self.get_end_position(start_pos, touch)

            self.bounce_vector.center = start_pos
            self.bounce_vector.line.points = [start_pos[0], start_pos[1],
                                              end_pos[0], end_pos[1]]

    def get_start_position(self, touch):
        '''
            Here we determine the point location on the surface of
            the paddle that is closest to our touch position.
            This needs to work even if the touch position is
            inside the paddle.
        '''
        pos_x = self.clamp(touch.x, self.x, self.right)
        pos_y = self.clamp(touch.y, self.y, self.top)

        # this is a bit convoluted. We could probably do better
        d_left = abs(pos_x - self.x)
        d_right = abs(pos_x - self.right)
        d_top = abs(pos_y - self.top)
        d_bot = abs(pos_y - self.y)
        d_min = min(d_left, d_bot, d_right, d_top)

        if d_left == d_min:
            return self.x, pos_y
        elif d_right == d_min:
            return self.right, pos_y
        elif d_top == d_min:
            return pos_x, self.top
        else:
            return pos_x, self.y

    def get_end_position(self, start, touch):
        '''
            Here we determine the endpoint of the line that represents
            the direction of our bounce.
            - Normal case is that we will simply use the touch position.
            - If the touch position is inside the paddle, we will reverse
              the direction of our line relative to the starting point.
        '''
        if self.inside_paddle(touch):
            # reversed position relative to start
            return (start[0] + (start[0] - touch.x),
                    start[1] + (start[1] - touch.y))
        else:
            return touch.x, touch.y

    def inside_paddle(self, touch):
        return ((self.x < touch.x < self.right) and
                (self.y < touch.y < self.top))

    def clamp(self, x, lower, upper):
        return max(lower, min(upper, x))


class BounceVector(Widget):
    def __init__(self, **kwargs):
        super(BounceVector, self).__init__(**kwargs)
        points = kwargs.get('points', [100, 100, 200, 200])

        with self.canvas:
            self.line = Line(points=points, width=1)


class BounceVectorGame(Widget):
    player = ObjectProperty(None)

    def add_bounce_vector(self):
        pass

    def update(self, _dt):
        pass

    def on_touch_down(self, touch):
        self.player.attach_bounce_vector(touch)

    def on_touch_up(self, touch):
        self.player.detach_bounce_vector()

    def on_touch_move(self, touch):
        self.player.move_bounce_vector(touch)


class BounceVectorApp(App):
    def build(self):
        game = BounceVectorGame()

        Clock.schedule_interval(game.update, 1.0 / 60.0)

        return game


if __name__ == '__main__':
    BounceVectorApp().run()
