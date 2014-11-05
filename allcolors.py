import pygame as pg
import numpy as np
import time
from closecolors import CloseColors

def allcolors():
  pg.init()
  screen = pg.display.set_mode([512, 512])
  surf = pg.Surface((512, 512))
  surf.fill((0.,0.,0.))
  cc = CloseColors()
  #for i in range(1):
  #    (x, y) = np.random.randint(0, 512, 2)
  #    (r, g, b) = np.random.randint(0, 64, 3)
  #    col = cc.seed((x, y), (r, g, b))
#  col = cc.seed((170, 170), (0,0,0))
#  surf.set_at((170, 170), col)
  col = cc.seed((511,511), (0, 0, 0))
  surf.set_at((511,511), col)
  col = cc.seed((0,0), (63, 63, 63))
  surf.set_at((0,0), col)
#  col = cc.seed((255, 511), (63, 63, 63))
#  surf.set_at((255, 511), col)
#  for i in range(100):
  done = False
  num = 0
  while not done:
    for j in range(300):
        r = cc.iterate()
        if r is not None:
            coords, col = r
            surf.set_at(coords, col)
    if r is None:
        done = True
    screen.blit(surf, (0,0))
    pg.display.flip()
    pg.image.save(surf, 'frame-%04d.png' % (num,))
    num += 1
  time.sleep(2.0)
  pg.quit()
  return cc

if __name__ == '__main__':
  cc = allcolors()
