
from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from character import Character

import random
from time import sleep
from math import floor

class CharacterAction(Enum):

    Wait = (0, 100)
    Walk = (1, 100)
    Duplicate = (3, 10)

    def do(self, character: "Character"):

        match self:
                
            # ------>

            case CharacterAction.Wait:

                # keep waiting.
                if character.getTimeInAction() < character.action_package.get('wait_delay'):
                    return
                
                new_action = CharacterAction.getRandomAction(notActionAllow = {
                    CharacterAction.Wait,
                    (None if character.is_allow_to_duplicate else CharacterAction.Duplicate)
                })
                new_action.setNewAction(character)
                
            # ------>

            case CharacterAction.Walk:

                # increase walk.
                character.pos_float[0] += (
                    character.action_package.get('speed_walk') *
                    (1 if character.action_package.get('is_walk_right') else -1)
                )

                # reach the end of walk.
                if (
                    (
                        character.action_package.get('is_walk_right') and 
                        int(character.pos_float[0]) >= character.action_package.get('pos_x_to')
                    ) or (
                        not character.action_package.get('is_walk_right') and 
                        int(character.pos_float[0]) <= character.action_package.get('pos_x_to')
                    )
                ):
                    character.pos_float[0] = float(character.action_package.get('pos_x_to'))
                    character.setPosX(character.action_package.get('pos_x_to'))  # snap to end walk.

                    # set new action.
                    new_action = CharacterAction.getRandomAction(notActionAllow = {
                        CharacterAction.Walk
                    })
                    new_action.setNewAction(character)

                    return
                
                # apply walk (float value).
                character.updatePosFromFloat()

                # set sprite anime walk, based on time.
                time_walking = character.getTimeInAction()
                dellay_cycle_walk = 0.600
                interpolate_walk = time_walking % dellay_cycle_walk
                interpolate_walk /= dellay_cycle_walk
                sprites_walk_anime = ['walk1', 'default', 'walk2', 'default']
                interpolate_walk *= len(sprites_walk_anime)
                interpolate_walk = floor(interpolate_walk)
                character.setSprite(sprites_walk_anime[interpolate_walk])

            # ------>

            case CharacterAction.Duplicate:

                character.spawn(character.action_package.get('sprites_new_instance'))

                # set new action.
                new_action = CharacterAction.getRandomAction(notActionAllow = {
                    CharacterAction.Walk
                })
                new_action.setNewAction(character)

    # ------>

    @staticmethod
    def getRandomAction(
        setActionAllow: set["CharacterAction"]|None = None, 
        notActionAllow:set["CharacterAction"]|None = None
    ) -> "CharacterAction":
        action_allow = setActionAllow or set(CharacterAction)

        if notActionAllow != None:
            action_allow -= notActionAllow

        action_allow -= {None}

        l_allow = list(action_allow)
        max_sum = sum([ e.value[1] for e in l_allow ])
        rand_val = random.randint(1, max_sum)
        for e in l_allow:
            rand_val -= e.value[1]
            if rand_val > 0:
                continue
            return e

        # old vertion (therocally never use).
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

            # ------>

            case CharacterAction.Duplicate:

                character.action_package = {
                    'sprites_new_instance': None  # TODO: choose randomely a list of str sprite.
                }
                character.setSprite('default')


