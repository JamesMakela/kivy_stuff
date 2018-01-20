from random import randint

import kivy
kivy.require('1.10.1')  # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.properties import (NumericProperty,
                             ReferenceListProperty,
                             ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock


class StartGameModal(ModalView):
    root = ObjectProperty(None)

    def dismiss(self, *args, **kwargs):
        self.root.game_in_play = True
        self.root.player1.score = 0
        self.root.player2.score = 0

        super(StartGameModal, self).dismiss(*args, **kwargs)

    def quit(self):
        self.root.app.stop()


class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            speedup = 1.1
            offset = 0.02 * Vector(0, ball.center_y - self.center_y)
            ball.velocity = speedup * (offset - ball.velocity)


class PongBall(Widget):
    # velocity of the ball on x and y axis
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    # referencelist property so we can use ball.velocity as
    # a shorthand, just like e.g. w.pos for w.x and w.y
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        # 'move' function will move the ball one step.  This
        # will be called in equal intervals to animate the ball
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    app = ObjectProperty(None)

    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    game_in_play = ObjectProperty(False)

    start_dlg = None

    def show_start_buttons(self):
        if self.start_dlg is None:
            self.start_dlg = StartGameModal(auto_dismiss=False,
                                            root=self)

        self.start_dlg.open()

    def serve_ball(self):
        self.ball.center = self.center
        self.ball.velocity = Vector(4, 0).rotate(randint(0, 360))

    def update(self, _dt):
        self.ball.move()

        # bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce off top and bottom
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1

        if self.game_in_play is True:
            self.out_of_bounds()
            if self.game_is_over():
                self.game_in_play = False
                self.serve_ball()
                self.show_start_buttons()
        else:
            # demo game play
            self.out_of_bounds(score_point=False)
            self.follow_ball()

    def out_of_bounds(self, score_point=True):
        # went out-of-bounds to score point?
        if self.ball.x < self.x:
            if score_point:
                self.player2.score += 1
            self.serve_ball()
        if self.ball.x > self.width:
            if score_point:
                self.player1.score += 1
            self.serve_ball()

    def follow_ball(self):
        # Here we have the appropriate paddle try
        # to hit the ball back.  This is just for demo play.
        if self.ball.velocity_x >= 0.0:
            if self.player2.center_y > self.ball.center_y:
                self.player2.y -= 2

            if self.player2.center_y < self.ball.center_y:
                self.player2.y += 2
        else:
            if self.player1.center_y > self.ball.center_y:
                self.player1.y -= 2

            if self.player1.center_y < self.ball.center_y:
                self.player1.y += 2

    def game_is_over(self):
        return (self.player1.score >= 5 or
                self.player2.score >= 5)

    def on_touch_down(self, touch):
        if self.is_player1(touch):
            self.old_y1 = touch.y

        if self.is_player2(touch):
            self.old_y2 = touch.y

    def on_touch_move(self, touch):
        if self.is_player1(touch):
            move_to = touch.y - self.old_y1
            self.move_player(self.player1, move_to)
            self.old_y1 = touch.y

        if self.is_player2(touch):
            move_to = touch.y - self.old_y2
            self.move_player(self.player2, move_to)
            self.old_y2 = touch.y

    def is_player1(self, touch):
        return touch.x < self.width / 3

    def is_player2(self, touch):
        return touch.x > self.width - self.width / 3

    def move_player(self, player, move_to):
        new_pos = player.center_y + move_to
        player.center_y = min(self.height - player.height / 2,
                              max(player.height / 2, new_pos))


class PongApp(App):
    def build(self):
        game = PongGame(app=self)

        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        Clock.schedule_once(self.show_start_buttons, 2)

        return game

    def show_start_buttons(self, _instance):
        self.root.show_start_buttons()


if __name__ == '__main__':
    PongApp().run()
