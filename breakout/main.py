from random import randint, random

import kivy
kivy.require('1.10.0')  # replace with your current kivy version !

from kivy.base import EventLoop
from kivy.app import App
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView

from kivy.properties import (NumericProperty,
                             ReferenceListProperty,
                             ObjectProperty)


class Solid(object):
    '''
        Mixin for objects we want to treat as solid.  Solid objects for this
        purpose are bricks or paddles which a ball will bounce off of.
        So the code for figuring out how the bounce will happen is here.
    '''
    def get_bounce_vector(self, other):
        '''
            Calculate the vector at which an object will reflect or 'bounce'
            off our object.  This requires the other object have a velocity
            attribute.
            (Note: we will assume that the other object is coming toward our
                   object for now.)
        '''
        n = self.get_surface_normal(other)
        d = Vector(other.velocity)

        return d - 2.0 * (d.dot(n)) * n

    def get_surface_normal(self, other):
        return self.get_surface_vector(other).normalize()

    def get_surface_vector(self, other):
        '''
           Calculate a vector which points outward and perpendicular
           to the closest surface
        '''
        start = self.get_surface_point(other)
        end = self.get_end_point(start, other)

        return Vector(end[0] - start[0],
                      end[1] - start[1])

    def get_surface_point(self, other):
        '''
            Here we determine the point location on the surface of
            the paddle that is closest to our touch position.
            This needs to work even if the touch position is
            inside the paddle.
        '''
        pos_x = self.clamp(other.center_x, self.x, self.right)
        pos_y = self.clamp(other.center_y, self.y, self.top)

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

    def get_end_point(self, start, other):
        '''
            Here we determine the endpoint of the line that represents
            the surface perpendicular vector.
            - Normal case is that we will simply use the other object's
              center position.
            - If the other object's center position is inside the paddle,
              we will reverse the direction of our line relative to the
              starting point.
        '''
        if self.inside_paddle(other):
            # reversed position relative to start
            return (start[0] + (start[0] - other.center_x),
                    start[1] + (start[1] - other.center_y))
        else:
            return other.center_x, other.center_y

    def inside_paddle(self, other):
        return Vector.in_bbox((other.center_x, other.center_y),
                              (self.x, self.y),
                              (self.right, self.top))

    def clamp(self, x, lower, upper):
        return max(lower, min(upper, x))


class StartGameModal(ModalView):
    root = ObjectProperty(None)

    def dismiss(self, *args, **kwargs):
        self.root.reset_game()
        self.root.game_in_play = True
        self.root.serve_ball()

        super(StartGameModal, self).dismiss(*args, **kwargs)

    def quit(self):
        self.root.app.stop()


class Ball(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        # move the ball one step in the direction of its velocity.
        self.pos = Vector(*self.velocity) + self.pos

    def move_to(self, vec):
        # move the ball to a relative vector position.
        self.pos = vec + self.pos


class Paddle(Widget, Solid):
    score = NumericProperty(0)
    missed_balls = NumericProperty(0)
    collided = False  # to 'debounce' the bounce logic

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            if not self.collided:
                ball.velocity = self.get_bounce_vector(ball)
                self.collided = True
        else:
            self.collided = False


class Brick(Widget, Solid):
    value = NumericProperty(0)
    hue = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            ball.velocity = self.get_bounce_vector(ball)


class BreakoutGame(Widget):
    app = ObjectProperty(None)

    ball = ObjectProperty(None)
    player = ObjectProperty(None)
    bricks = []
    game_in_play = ObjectProperty(False)

    start_dlg = None
    level_width = 8
    level_height = 5
    follow_speed = None

    def update(self, _dt):
        self.ball.move()
        self.player.bounce_ball(self.ball)
        self.bounce_off_walls()

        if self.game_in_play:
            self.hit_a_brick()
            self.out_of_bounds()

            if self.game_is_over():
                self.game_in_play = False
                self.serve_ball()
                self.show_start_buttons()
            elif self.player_won():
                self.reset_level()
                self.load_level()
                self.serve_ball()
        else:
            # demo mode
            self.hit_a_brick(score_point=False)
            self.out_of_bounds()
            self.follow_ball()
            if len(self.bricks) == 0:
                self.load_level()
                self.serve_ball()

    def show_start_buttons(self):
        if self.start_dlg is None:
            self.start_dlg = StartGameModal(auto_dismiss=False,
                                            root=self)

        self.start_dlg.open()

    def serve_ball(self):
        self.ball.center = (self.player.center_x,
                            self.player.top + self.ball.height / 2)
        direction = randint(15, 165)

        # velocity needs to scale with the resolution of the game window
        # or the ball will appear to be very fast on small screens and
        # very slow on hi-res screens.
        scaled_velocity = min(*self.size) * 0.0067
        self.ball.velocity = Vector(scaled_velocity, 0).rotate(direction)

    def bounce_off_walls(self):
        ''' bounce off left, right, and top walls '''
        if self.ball.x < 0 or self.ball.right > self.width:
            self.ball.velocity_x *= -1

        if self.ball.top > self.height:
            self.ball.velocity_y *= -1

    def hit_a_brick(self, score_point=True):
        for b in self.bricks:
            if b.collide_widget(self.ball):
                b.bounce_ball(self.ball)
                self.remove_brick(b)

                if score_point:
                    self.player.score += b.value

                break

    def out_of_bounds(self):
        # went out-of-bounds?
        if self.ball.y < self.y:
            self.player.missed_balls += 1
            self.serve_ball()

    def load_level(self):
        grid_padding = 2
        cell_padding = 2
        cell_width = (self.width - grid_padding * 2) / self.level_width
        cell_height = (self.height - grid_padding * 2) / 4 / self.level_height

        for x in range(self.level_width):
            for y in range(self.level_height):
                num_colors = 5
                hue = (1.0 / num_colors) * (y % num_colors)

                pos_x, pos_y = (cell_width * x + cell_padding + grid_padding,
                                cell_height * y + cell_padding + grid_padding)
                w, h = (cell_width - (cell_padding * 2),
                        cell_height - (cell_padding * 2))

                brick = Brick(pos=(pos_x, pos_y + self.height / 2),
                              size=(w, h),
                              value=y + 1,
                              hue=hue)

                self.add_widget(brick)
                self.bricks.append(brick)

    def reset_level(self):
        for b in self.bricks[:]:
            self.remove_brick(b)

    def reset_game(self):
        self.player.missed_balls = 0
        self.player.score = 0
        self.reset_level()
        self.load_level()

    def remove_brick(self, b):
        self.remove_widget(b)
        self.bricks.remove(b)

    def follow_ball(self):
        # Here we have the paddle try to hit the ball back.
        # This is just for demo play.
        if self.follow_speed is None:
            # we should be able to catch up to the ball if it is traveling
            # in a vertical slope of 55 degrees or more
            self.follow_speed = Vector(*self.ball.velocity).length() * 0.57

        if self.player.center_x > self.ball.center_x:
            self.player.x -= self.follow_speed

        if self.player.center_x < self.ball.center_x:
            self.player.x += self.follow_speed

    def game_is_over(self):
        return self.player_lost()

    def player_lost(self):
        return self.player.missed_balls >= 3

    def player_won(self):
        return len(self.bricks) == 0

    def on_touch_down(self, touch):
        self.old_x = touch.x

    def on_touch_move(self, touch):
        move_to = touch.x - self.old_x
        self.move_player(self.player, move_to)
        self.old_x = touch.x

    def move_player(self, player, move_to):
        new_pos = player.center_x + move_to
        player.center_x = min(self.width - player.width / 2,
                              max(player.width / 2, new_pos))


class BreakoutApp(App):
    def build(self):
        EventLoop.ensure_window()
        self.window = EventLoop.window
        game = BreakoutGame(app=self)

        game.load_level()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        Clock.schedule_once(self.show_start_buttons, 2)

        return game

    def show_start_buttons(self, _instance):
        self.root.show_start_buttons()


if __name__ == '__main__':
    BreakoutApp().run()
