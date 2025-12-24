import random

_dots= [ [], [(4, 4)], [(2, 2), (6, 6)], [(2, 2), (4, 4), (6, 6)],
        [(2, 2), (2, 6), (6, 2), (6, 6)], [(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)],
        [(2, 2), (2, 6), (4, 2), (4, 6), (6, 2), (6, 6)] ]

def image( face ):
    img= [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    for i, j in _dots[face] :
        img[i][j]= 1
    return img

def fullFloatingImage( dices, xPix= 9, yPix= 9 ):
    # Init :
    ndices= len(dices)
    handimg= [ [ 0 for i in range(xPix*ndices+ndices+3) ] 
              for j in range(yPix+4) ]
    xFuzzy= (xPix-5)
    yFuzzy= (yPix-5)
    # Copy dices :
    xx= 0
    for d in dices :
        dimg= image(d)
        x= xx+random.randint(0, xFuzzy)
        y= random.randint(0, yFuzzy)
        for i in range(len(dimg)):
            for j in range(len(dimg[i])):
                handimg[y+i][x+j]= dimg[i][j]
        xx+= xPix
    return handimg

def floatingImage( dices, xPix= 9, yPix= 9 ):
    handimg= fullFloatingImage(dices, xPix, yPix)
    return [ line[2:-2] for line in handimg[2:-2] ]

def shell( img ):
    pixs= [ [ ' ', '▄' ], ['▀', '█'] ]

    shellimg= '┌' + '─'*len(img[0]) +'┐\n'
    for i in range( 1, len(img), 2 ) :
        shellimg+='│'
        for a, b in zip( img[i-1], img[i] ) :
            shellimg+= pixs[a][b]
        shellimg+='│\n'

    if len( img ) % 2 == 1 :
        shellimg+='│'
        for a in img[-1] :
            shellimg+= pixs[a][0]
        shellimg+='│\n'

    shellimg+= '└' + '─'*len(img[-1]) +'┘'
    
    return shellimg

