import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import DRONE, LARVA, HATCHERY, OVERLORD, EXTRACTOR


class ZergBot(sc2.BotAI):
    async def on_step(self, iteration):
        
        await self.distribute_workers()
        await self.build_workers()
        await self.build_overlords()
        await self.build_extractor()
        await self.expand()
        # await self.build_army()

    async def build_workers(self):
        larvae = self.units(LARVA)
        if len(larvae) > 0:
            for hatch in self.units(HATCHERY).ready.noqueue:
                if self.can_afford(DRONE):
                    await self.do(larvae.random.train(DRONE)) # select random larva and train it

    async def build_overlords(self):
        larvae = self.units(LARVA)
        if self.supply_left < 2:
            if self.can_afford(OVERLORD) and larvae.exists:
                await self.do(larvae.random.train(OVERLORD))

    async def build_extractor(self):
        for hatch in self.units(HATCHERY).ready:
            vasps = self.state.vespene_geyser.closer_than(15.0, hatch)
            for vasp in vasps:
                if not self.can_afford(EXTRACTOR):
                    break
                worker = self.select_build_worker(vasp.position)
                if worker is None:
                    break
                if not self.units(EXTRACTOR).closer_than(1.0, vasp).exists:
                    await self.do(worker.build(EXTRACTOR, vasp))
                    
    async def expand(self):
        if self.units(HATCHERY).amount < 3 and self.can_afford(HATCHERY):
            await self.expand_now()

    # async def build_army(self):
        






run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, ZergBot()),
    Computer(Race.Terran, Difficulty.Easy)],
    realtime=False)

