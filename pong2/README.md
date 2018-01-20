
# A Slightly Better Pong Game

This is a very simple Pong Game that is written in Python using the
[Kivi](https://kivy.org/)
graphical application library.  
Ok, we've started with the
[Pong demo](https://kivy.org/docs/tutorials/pong.html)
taken from their tutorials, and are adding some features to it.

With the Kivi library installed in your Python environment, you can run the
program like this:

```
> cd <pong_directory>
> python pong.py
```

# Improvements

- None yet

# Todo Items

- Make it an actual game, with a start and an end.
  The game might contain a modal button that starts a game,
  and the game could end when one player achieves a certain score.
- While we're at it, a Quit button would be nice.
- Right now the ball speeds up as the game progresses.
  This is most likely a side-effect of the paddle collision behavior,
  but it does make the game more interesting.  But if the ball goes
  too fast, it will go through the paddle in a single step, making
  the player 'miss' the ball even if the paddle is in front of the ball.
  Enforcing a top ball speed would fix this, or maybe a smarter
  algorithm for the ball-to-paddle collision detection.
- If the application loses focus, the game does not pause.  This can
  happen quite easily when playing with a mouse on a windowing environment,
  and it is annoying to lose a ball just because you clicked on a window
  in the background.
