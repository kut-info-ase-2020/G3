import pygame.mixer
import time


pygame.mixer.init()

pygame.mixer.music.load("alarm.mp3")

pygame.mixer.music.play(-1)

time.sleep(60)

pygame.mixer.music.stop()