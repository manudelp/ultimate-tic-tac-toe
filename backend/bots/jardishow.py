from bots.alphabeta import AlphaBetaAgent


class JardiShowAgent(AlphaBetaAgent):
    id = 3
    name = "Jardinero"
    icon = "🍀"
    description = "Jardinero is a mischievous plant enthusiast who always has a trick up his sleeve. Watch out, he's here to turn your game into his garden!"
    depth_local = 8
    depth_global = 7
