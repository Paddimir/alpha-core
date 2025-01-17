from game.world.managers.objects.creature.CreatureManager import CreatureManager
from game.world.managers.maps.MapManager import MapManager
from struct import unpack


class TrainerListHandler(object):

    @staticmethod
    def handle(world_session, socket, reader):
        if len(reader.data) >= 8:  # Avoid handling empty trainer list packet.
            guid = unpack('<Q', reader.data[:8])[0]

            # Player talents.
            if guid == world_session.player_mgr.guid:
                world_session.player_mgr.talent_manager.send_talent_list()
            # NPC offering.
            else:
                trainer: CreatureManager = MapManager.get_surrounding_unit_by_guid(world_session.player_mgr, guid)

                if trainer and trainer.is_within_interactable_distance(world_session.player_mgr):
                    if trainer.is_trainer() and trainer.is_quest_giver():
                        if trainer.is_trainer_for_class(world_session.player_mgr.player.class_):
                            quests: int = world_session.player_mgr.quest_manager.get_active_quest_num_from_quest_giver(trainer)
                            if quests > 0:
                                world_session.player_mgr.quest_manager.handle_quest_giver_hello(trainer, guid)
                            else:
                                trainer.send_trainer_list(world_session)
                        else:  # If trainer does not train player class, just send the quest giver greeting. Ineligible quests won't show up here, so this matches the behavior of classic WoW.
                            world_session.player_mgr.quest_manager.handle_quest_giver_hello(trainer, guid)
                    elif trainer.is_trainer() and not trainer.is_quest_giver():
                        if trainer.is_trainer_for_class(world_session.player_mgr.player.class_):
                            trainer.send_trainer_list(world_session)
        return 0
