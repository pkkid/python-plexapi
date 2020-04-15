import logging

from plexapi.server import PlexServer

logging.basicConfig(level=logging.INFO)


p = PlexServer()


t = p.library.section('Movies')
x = t.collection()
print(x)
ass = x[0]
#print(vars(t))
#print(vars(x[0]))
print(ass)
print(vars(ass))
ass.reload()
ass.modeUpdate("hideItems")
ass.reload()
print(vars(ass))

#print(t[0])
#print(dir(t[0]))
#print(vars(t[0]))
