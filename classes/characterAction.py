
from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from character import Character

import random
from time import sleep

class CharacterAction(Enum):

    Wait = 0,
    Walk = 1

    def do(self, character: "Character"):

        match self:
                
            # ------>

            case CharacterAction.Wait:

                # keep waiting.
                if character.getTimeInAction() < character.action_package['wait_delay']:
                    return
                
                new_action = CharacterAction.getRandomAction(notActionAllow = {
                    CharacterAction.Wait
                })
                new_action.setNewAction(character)
                
            # ------>

            case CharacterAction.Walk:

                # increase walk.
                character.pos_float[0] += (
                    character.action_package['speed_walk'] *
                    (1 if character.action_package['is_walk_right'] else -1)
                )

                # reach the end of walk.
                if (
                    (
                        character.action_package['is_walk_right'] and 
                        int(character.pos_float[0]) >= character.action_package['pos_x_to']
                    ) or (
                        not character.action_package['is_walk_right'] and 
                        int(character.pos_float[0]) <= character.action_package['pos_x_to']
                    )
                ):
                    character.pos_float[0] = float(character.action_package['pos_x_to'])
                    character.setPosX(character.action_package['pos_x_to'])  # snap to end walk.

                    # set new action.
                    new_action = CharacterAction.getRandomAction(notActionAllow = {
                        CharacterAction.Walk
                    })
                    new_action.setNewAction(character)

                    return
                
                # apply walk (float value).
                character.updatePosFromFloat()

                # TODO: set sprite anime walk, based on time.
                #character.setSprite('default')

    # ------>

    @staticmethod
    def getRandomAction(
        setActionAllow: set["CharacterAction"]|None = None, 
        notActionAllow:set["CharacterAction"]|None = None
    ) -> "CharacterAction":
        action_allow = setActionAllow or set(CharacterAction)

        if notActionAllow != None:
            action_allow -= notActionAllow
        
        return random.choice(list(action_allow))
    
    # ------>

    def setNewAction(self, character: "Character"):

        character.action = self
        character.time_from_last_action = character.time_from_lauch

        match self:

            # ------>

            case CharacterAction.Wait:

                character.action_package = {
                    'wait_delay': random.randint(2, 5)
                }
                character.setSprite('default')

            # ------>

            case CharacterAction.Walk:

                is_walk_right = random.randint(0, 1) == 1
                distance_walk = random.randint(4, 8) * 12

                # check overange screen dest.
                max_pos_screen = character.getMaxPosScreenX()
                if (
                    is_walk_right and ( character.x() + distance_walk > max_pos_screen )
                ):
                    distance_walk = max_pos_screen - character.x()
                elif (
                    not is_walk_right and ( character.x() - distance_walk < 0 )
                ):
                    distance_walk = character.x()
                    
                # switch direction.
                if is_walk_right ^ character.is_look_right:
                    character.is_look_right = not character.is_look_right

                character.action_package = {
                    'is_walk_right': is_walk_right,
                    'speed_walk': 1.0,  
                    'distance_walk': distance_walk,
                    'pos_x_from': character.x(),
                    'pos_x_to': character.x() + distance_walk * (1 if is_walk_right else -1)
                }
                character.setSprite('default')


