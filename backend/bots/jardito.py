from bots.alphabeta import AlphaBetaAgent


class JardineritoAgent(AlphaBetaAgent):
    id = 2
    name = "Jardinerito"
    icon = "☘️"
    description = "Jardinerito is a clever little bot who loves planting winning moves and weeding out the bad ones. Watch out, he's got a green thumb for victory!"
    difficulty = 3
    depth_local = 5
    depth_global = 4
