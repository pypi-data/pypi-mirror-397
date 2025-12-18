from pioneergame import Window, Label, Button, Rect, Sprite, explode, explosion_update
from animator import Animation

window = Window(1300, 700)
fps = 80

box = Rect(window, 100, 100, 200, 200, 'red')

sprite = Sprite(window)
sprite.attach_to(box)

sprite2 = Sprite(window)
sprite2.attach_to(box)
sprite2.rotate(90)

while True:
    window.fill((80, 80, 100))

    window.set_caption(f'{window.get_fps():.1f}')

    window.update(fps)
