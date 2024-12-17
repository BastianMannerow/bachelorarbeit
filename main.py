#from iteration1.simulation.GeneralGameTheory import ClassicPublicGoodsGame
from iteration2.simulation.PublicGoodsGame import ClassicPublicGoodsGame

# Test multiple agent in the same round based environment
simulation = ClassicPublicGoodsGame((0, 2))
simulation.run_simulation()