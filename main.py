import pyscreenshot as ImageGrab

# part of the screen
im = ImageGrab.grab(bbox=(0, 90, 2048, 1230))  # X1,Y1,X2,Y2

# save image file
im.save("box.png")
