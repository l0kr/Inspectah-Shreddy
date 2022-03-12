import sc2
from sc2.bot_ai import BotAI
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.player import Bot, Computer
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
import random


class ZergBot(BotAI):
    async def on_step(self, iteration):
        
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pool()
        await self.build_lings()
        await self.build_overlords()
        await self.build_extractor()
        await self.expand()
        await self.destroy()

    async def build_workers(self):
        larva = self.units(UnitTypeId.LARVA)
        if len(larva) > 0 and self.workers.amount < 36:
                if self.can_afford(UnitTypeId.DRONE):
                     self.larva.random.train(UnitTypeId.DRONE) # select random larva and train it

    async def build_lings(self):
        larva = self.units(UnitTypeId.LARVA)
        if len(larva) > 0:
                if self.can_afford(UnitTypeId.ZERGLING):
                     self.larva.random.train(UnitTypeId.ZERGLING)

    async def build_overlords(self):
        larva = self.units(UnitTypeId.LARVA)
        if self.supply_left < 2 and self.supply_cap < 200:
            if self.can_afford(UnitTypeId.OVERLORD) and larva.exists:
                 self.train(UnitTypeId.OVERLORD)

    async def build_pool(self):
        if self.can_afford(UnitTypeId.SPAWNINGPOOL) and self.already_pending(UnitTypeId.SPAWNINGPOOL) + self.structures.filter(lambda structure: structure.type_id == UnitTypeId.SPAWNINGPOOL and structure.is_ready).amount == 0:
            worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
            # Worker_candidates can be empty
            if worker_candidates:
                map_center = self.game_info.map_center
                position_towards_map_center = self.start_location.towards(map_center, distance=5)
                placement_position = await self.find_placement(UnitTypeId.SPAWNINGPOOL, near=position_towards_map_center, placement_step=1)
                # Placement_position can be None
                if placement_position:
                    build_worker = worker_candidates.closest_to(placement_position)
                    build_worker.build(UnitTypeId.SPAWNINGPOOL, placement_position)


    async def build_extractor(self):
        for hatch in self.units(UnitTypeId.HATCHERY).ready:
            vasps = self.vespene_geyser.closer_than(15.0, hatch)
            for vasp in vasps:
                if not self.can_afford(UnitTypeId.EXTRACTOR): break
                worker = self.select_build_worker(vasp.position)
                if worker is None:
                    break
                if not self.units(UnitTypeId.EXTRACTOR).closer_than(1.0, vasp).exists:
                    await self.build_extractor()

    async def destroy(self):
        if self.units(UnitTypeId.ZERGLING).amount >= 30:
            if self.enemy_units:
                for ling in self.units(UnitTypeId.ZERGLING).idle:
                    ling.attack(random.choice(self.enemy_units))

    async def expand(self):
        if self.structures(UnitTypeId.HATCHERY).amount < 3 and self.can_afford(UnitTypeId.HATCHERY): await self.expand_now()

    def is_built(self,  building: UnitTypeId):
       return bool(self.already_pending(building) + self.structures.filter(lambda structure: structure.type_id == building and structure.is_ready).amount == 0)

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, ZergBot()),
    Computer(Race.Zerg, Difficulty.Hard)],
    realtime=False
    )

