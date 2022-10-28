from urllib.parse import ParseResult
import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips:

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical
  board states. Though, we recommended making a copy of the map to preserve
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []
        self.algo_2_init_turrets = [[1, 12], [8,12], [19, 12], [26, 12]]
        self.algo_2_init_walls = [[0,13],[1,13],[2,13],[7,13],[8,13],[9,13],[18,13], [19,13], [20,13], [25,13], [26,13], [27,13]]
        self.algo_2_turrets = [[ 1, 12],[ 4, 12],[ 8, 12],[ 11, 12],[ 16, 12],[ 19, 12],[ 23, 12],[ 26, 12]]
        self.algo_2_turret_protection = [[t[0], t[1]+1] for t in self.algo_2_turrets]
        self.algo_2_fixed_walls_first_layer = [[0,13], [2,13], [3,13], [5,13], [7,13], [9,13], [10,13], [12, 13], [14,13], [15,13], [17, 13], [18, 13], [20, 13], [22, 13], [24, 13], [25, 13], [27,13]]
        self.algo_2_fixed_walls_second_layer = [[2,12], [3,12], [5,12], [7,12], [9,12], [10,12], [12, 12], [14,12], [15,12], [17, 12], [18, 12], [20, 12], [22, 12], [24, 12], [25, 12]]
        self.algo_2_left_openers = [[6,13], [6,12]]
        self.algo_2_right_openers = [[21, 13], [21, 12]]
        self.algo_2_mid_openers = [[13, 13], [13,12]]
        self.algo_2_supports_lvl_1 = [[9, 10],[11, 10],[17,10],[19,10]]
        self.algo_2_supports_lvl_2 = [[9, 9],[11, 9],[17,9],[19,9]]
        self.algo_2_left_extra_wall = [[5,11], [5,10], [6,9], [7,9]]
        self.algo_2_right_extra_wall  = [[22, 11], [22, 10], [21, 9], [20,9]]
        self.algo_2_mid_extra_wall = [[12, 11], [12, 10], [14, 11], [14, 10]]
        self.algo_2_turret_rich = [[2,12], [3,12], [9,12], [10,12], [17,12], [18,12], [24, 12], [25, 12]]
        self.algo_2_X = {i for i in range(0, 28)}
        self.algo_2_upper_Y = {i for i in range(17, 28)}
        self.algo_2_bottom_Y = {i for i in range(14, 17)}
        self.algo_2_left_X = {i for i in range(0, 14)}
        self.algo_2_right_X = {i for i in range(14, 28)}
        self.algo_2_Y = {i for i in range(14, 28)}
        self.algo_2_attack_left_side = [[15,1]]
        self.algo_2_attack_left_mid = [[24, 10]]
        self.algo_2_attack_right_side = [[12, 1]]
        self.algo_2_attack_right_mid = [[3, 10]]
        self.algo_2_placed_demolisher = False



        # Algorithm 3 Moving Units + Sneak
        self.algo3_starting_turret = [[ 0, 13],[ 27, 13],[ 1, 12],[ 26, 12],[ 2, 11],[ 25, 11]]
        self.algo3_starting_wall = [[ 5, 13],[ 6, 13],[ 7, 13],[ 8, 13],[ 9, 13],[ 10, 13],[ 11, 13],[ 12, 13],[ 13, 13],[ 14, 13],[ 15, 13],[ 16, 13],[ 17, 13],[ 18, 13],[ 19, 13],[ 20, 13],[ 21, 13],[ 22, 13]]
        self.algo3_v_wall = [[ 5, 12],[ 22, 12],[ 7, 10],[ 20, 10],[ 8, 9],[ 19, 9],[ 9, 8],[ 18, 8],[ 10, 7],[ 17, 7],[ 11, 6],[ 16, 6],[ 12, 5],[ 15, 5],[ 13, 4],[ 14, 4]]
        self.algo3_v_wall2 = [[ 0, 13],[ 1, 13],[ 2, 13],[ 3, 13],[ 24, 13],[ 25, 13],[ 26, 13],[ 27, 13]]
        self.algo3_v_turret = [[ 1, 12],[ 2, 12],[ 3, 12],[ 24, 12],[ 25, 12],[ 26, 12],[ 6, 11],[ 21, 11]]
        self.algo3_v_turret2 = [[ 6, 12],[ 21, 12],[ 3, 11],[ 24, 11],[ 5, 10],[ 22, 10]]
        self.algo3_v_turret3 = [[ 3, 11],[ 7, 11],[ 20, 11],[ 24, 11],[ 5, 10],[ 22, 10]]

        self.algo3_counter = 0
        global LEFT, RIGHT, UP, BOTTOM
        LEFT = 0; RIGHT = 1; UP = 2; BOTTOM = 3


    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        #game_state.attempt_spawn(DEMOLISHER, [24, 10], 3)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        # self.algo1_v(game_state)

        self.algo3_sneak(game_state)
        #game_state.warn("Game INFO {}{}".format(self.side, self.action_turn))
        game_state.submit_turn()


    def algo3_round0(self, game_state):
        """
        Round 0 strategy: defense
        """
        game_state.attempt_spawn(WALL, self.algo3_starting_wall)
        game_state.attempt_spawn(TURRET, self.algo3_starting_turret, 1000)
        game_state.attempt_remove(self.algo3_starting_wall)
        game_state.attempt_remove(self.algo3_starting_turret)

    def algo3_round1(self, game_state):
        """
        Round 1 Strategy
        """
        support_pos = [[ 11, 12],[ 10, 11],[ 9, 10],[ 8, 9],[ 7, 8],[ 6, 7]]
        support_upgrade_pos = [[ 11, 12],[ 10, 11],[ 9, 10]]
        deploy_pos = [[ 7, 6]]
        game_state.attempt_spawn(SUPPORT, support_pos)
        game_state.attempt_upgrade(support_upgrade_pos)
        game_state.attempt_spawn(SCOUT, deploy_pos)
        game_state.attempt_remove(support_pos)

    def algo3_defense_round(self, game_state):
        game_state.attempt_spawn(WALL, self.algo3_v_wall)
        game_state.attempt_spawn(TURRET, self.algo3_v_turret)
        game_state.attempt_spawn(WALL, self.algo3_v_wall2)
        game_state.attempt_spawn(TURRET, self.algo3_v_turret2)
        game_state.attempt_upgrade(self.algo3_v_turret)
        game_state.attempt_upgrade(self.algo3_v_wall2)
        game_state.attempt_upgrade(self.algo3_v_turret2)
        game_state.attempt_spawn(TURRET, self.algo3_v_turret3)
        game_state.attempt_upgrade(self.algo3_v_turret3)

        if game_state.project_future_MP() >= 18:
            game_state.attempt_remove(self.algo3_v_wall)
            game_state.attempt_remove(self.algo3_v_wall2)
            game_state.attempt_remove(self.algo3_v_turret)
            game_state.attempt_remove(self.algo3_v_turret2)
            game_state.attempt_remove(self.algo3_v_turret3)

    def algo3_demolisher_attack_round(self, game_state):
        # SP >= 50
        wall_pos = [[ 0, 13],[ 1, 13],[ 2, 13],[ 3, 13],[ 4, 13],[ 5, 13],[ 7, 13],[ 8, 13],[ 9, 13],[ 10, 13],[ 11, 13],[ 13, 13],[ 14, 13],[ 16, 13],[ 17, 13],[ 18, 13],[ 19, 13],[ 21, 13],[ 22, 13],[ 23, 13],[ 24, 13],[ 26, 13],[ 27, 13],[ 1, 12],[ 26, 12],[ 2, 11],[ 5, 11],[ 6, 11],[ 7, 11],[ 8, 11],[ 9, 11],[ 10, 11],[ 11, 11],[ 12, 11],[ 13, 11],[ 14, 11],[ 15, 11],[ 16, 11],[ 17, 11],[ 18, 11],[ 19, 11],[ 20, 11],[ 21, 11],[ 22, 11],[ 23, 11],[ 24, 11],[ 25, 11],[ 3, 10],[ 4, 9]]
        turret_pos = [[6, 13], [12, 13], [15, 13], [20, 13]]
        support_pos = [[ 5, 9],[ 6, 9],[ 7, 9],[ 8, 9],[ 9, 9],[ 10, 9],[ 11, 9],[ 12, 9],[ 13, 9]]
        deploy_pos = [[24, 10]]
        game_state.attempt_spawn(WALL, wall_pos)
        game_state.attempt_spawn(TURRET, turret_pos)
        game_state.attempt_upgrade(turret_pos)
        game_state.attempt_spawn(SUPPORT, support_pos)
        game_state.attempt_upgrade(support_pos)

        game_state.attempt_spawn(DEMOLISHER, deploy_pos, 1000)

        game_state.attempt_remove(wall_pos)
        game_state.attempt_remove(turret_pos)
        game_state.attempt_remove(support_pos)

    def algo3_attack_round(self, game_state):
        support_pos = [[ 12, 11],[ 12, 10],[ 12, 9],[ 12, 8],[ 12, 7],[ 12, 6],[ 12, 5],[ 12, 4],[ 12, 3], [11, 2]]
        wall_pos = [[ 11, 13],[ 12, 13],[ 13, 13]]
        support_upgrade_pos = [[12, 11], [ 12, 10],[ 12, 9],[ 12, 8]]
        deploy_pos = [[10, 3]]
        guard_turret_pos = [[ 11, 12],[ 13, 12],[ 11, 11],[ 13, 11]]
        guard_turret_pos2 = [[ 3, 12],[ 7, 12],[ 20, 12],[ 24, 12]]
        wall_guard_turret_pos2 = [ 2, 13],[ 3, 13],[ 4, 13],[ 6, 13],[ 7, 13],[ 8, 13],[ 19, 13],[ 20, 13],[ 21, 13],[ 23, 13],[ 24, 13],[ 25, 13]
        # Protection and Support
        game_state.attempt_spawn(SUPPORT, support_pos)
        game_state.attempt_spawn(TURRET, guard_turret_pos)
        game_state.attempt_upgrade(guard_turret_pos)
        #game_state.attempt_spawn(WALL, wall_pos)
        game_state.attempt_upgrade(support_upgrade_pos)
        #game_state.attempt_upgrade(wall_pos)
        game_state.attempt_spawn(TURRET, guard_turret_pos2)
        game_state.attempt_spawn(WALL, wall_guard_turret_pos2)
        game_state.attempt_upgrade(guard_turret_pos2)
        game_state.attempt_upgrade(wall_guard_turret_pos2)
        game_state.attempt_spawn(SCOUT, deploy_pos, 1000)

        game_state.attempt_remove(support_pos)
        #game_state.attempt_remove(wall_pos)
        game_state.attempt_remove(deploy_pos)
        game_state.attempt_remove(support_pos)
        game_state.attempt_remove(guard_turret_pos)
        game_state.attempt_remove(guard_turret_pos2)
        game_state.attempt_remove(wall_guard_turret_pos2)

    def algo3_attack_round_demo(self, game_state):
        support_pos = [[ 12, 11],[ 12, 10],[ 12, 9],[ 12, 8],[ 12, 7],[ 12, 6],[ 12, 5],[ 12, 4],[ 12, 3], [11, 2]]
        wall_pos = [[ 11, 13],[ 12, 13],[ 13, 13]]
        support_upgrade_pos = [[12, 11], [ 12, 10],[ 12, 9],[ 12, 8]]
        deploy_pos = [[10, 3]]
        guard_turret_pos = [[ 11, 12],[ 13, 12],[ 11, 11],[ 13, 11]]
        guard_turret_pos2 = [[ 3, 12],[ 7, 12],[ 20, 12],[ 24, 12]]
        wall_guard_turret_pos2 = [ 2, 13],[ 3, 13],[ 4, 13],[ 6, 13],[ 7, 13],[ 8, 13],[ 19, 13],[ 20, 13],[ 21, 13],[ 23, 13],[ 24, 13],[ 25, 13]
        # Protection and Support
        game_state.attempt_spawn(SUPPORT, support_pos)
        game_state.attempt_spawn(TURRET, guard_turret_pos)
        game_state.attempt_upgrade(guard_turret_pos)
        #game_state.attempt_spawn(WALL, wall_pos)
        game_state.attempt_upgrade(support_upgrade_pos)
        #game_state.attempt_upgrade(wall_pos)
        game_state.attempt_spawn(TURRET, guard_turret_pos2)
        game_state.attempt_spawn(WALL, wall_guard_turret_pos2)
        game_state.attempt_upgrade(guard_turret_pos2)
        game_state.attempt_upgrade(wall_guard_turret_pos2)

        game_state.attempt_spawn(DEMOLISHER, deploy_pos, 1000)

        game_state.attempt_remove(support_pos)
        #game_state.attempt_remove(wall_pos)
        game_state.attempt_remove(deploy_pos)
        game_state.attempt_remove(support_pos)
        game_state.attempt_remove(guard_turret_pos)
        game_state.attempt_remove(guard_turret_pos2)
        game_state.attempt_remove(wall_guard_turret_pos2)

    def algo3_sneak(self, game_state):
        if game_state.turn_number == 0:
            self.algo3_round0(game_state)
        elif game_state.turn_number == 1:
            self.algo3_round1(game_state)
        else:
            self.algo3_counter += 1
            if game_state.get_resource(MP) < 18:
                self.algo3_defense_round(game_state)
            else:
                if self.detect_enemy_unit(game_state, None, valid_x = {i for i in range(0, 28)}, valid_y = [14, 15, 16]) >= 30 and game_state.get_resource(SP) >= 54:
                    self.algo3_demolisher_attack_round(game_state)
                else:
                    if self.algo3_counter % 4 == 0:
                        self.algo3_attack_round_demo(game_state)
                    else:
                        self.algo3_attack_round(game_state)







    def algo_2(self,game_state):
        # first get the enemy info about their defense
        enemy_info = self.algo_2_get_enemy_info(game_state)
        # then react to them with defense and attack strategy
        self.algo_2_defense(game_state, enemy_info)
        self.algo_2_attack(game_state, enemy_info)



    def algo_2_get_enemy_info(self, game_state):
        # obtain the left, right, bottom and up turrets information
        enemy_left_turrets = self.detect_enemy_unit(game_state, TURRET, self.algo_2_left_X , valid_y = self.algo_2_Y)
        enemy_right_turrets = self.detect_enemy_unit(game_state, TURRET, self.algo_2_right_X , valid_y = self.algo_2_Y)
        enemy_upper_turrets = self.detect_enemy_unit(game_state, TURRET, self.algo_2_X , valid_y = self.algo_2_upper_Y)
        enemy_bottom_turrets = self.detect_enemy_unit(game_state, TURRET, self.algo_2_X , valid_y = self.algo_2_bottom_Y)
        enemy_info = {LEFT:enemy_left_turrets,
                      RIGHT: enemy_right_turrets,
                      UP: enemy_upper_turrets,
                      BOTTOM: enemy_bottom_turrets}
        return enemy_info
    '''
    algo2 Defense handles the following:
    1. Place turrets
    2. Place walls
    3. Place interceptors
    4. place supports
    '''
    def algo_2_defense(self, game_state, enemy_info):
        # first round configuration
        if game_state.turn_number == 1:
            game_state.attempt_spawn(TURRET, self.algo_2_init_turrets)
            game_state.attempt_spawn(WALL, self.algo_2_init_walls)

        # for the first 4 rounds, do not upgrade turret, instead, try to upgrade walls in front of turrets
        elif game_state.turn_number < 4:
            game_state.attempt_spawn(TURRET,self.algo_2_turrets)
            game_state.attempt_spawn(WALL, self.algo_2_turret_protection)
            game_state.attempt_spawn(WALL, self.algo_2_fixed_walls_first_layer)
        else:
            '''
            # then after 4 rounds, we gradually build up the defense in the following strategy:
            # 1. build and upgrade turrets
            # 2. build and upgrade the walls in front of the turrets
            # 3. try build the first layer walls
            # 4. try build the second layer walls
            # 5. try build the level 1 supports
            # 4. try upgrade the first layer walls
            # 5. if the enemy's front is strong, we try to send demolishers and scouts from the middle
            #    if the enemy's back is strong, we try to send demolishers and scouts to the side
            # 6. delete the openers so we can redecide which side to open in the next round
            '''
            # 1. build and upgrade turrets
            game_state.attempt_spawn(TURRET, self.algo_2_turrets)
            game_state.attempt_upgrade(self.algo_2_turrets)

            # 2. build and upgrade the walls in front of the turrets
            game_state.attempt_spawn(WALL, self.algo_2_turret_protection)
            game_state.attempt_upgrade(self.algo_2_turret_protection)

            # 3. try build the first layer walls
            game_state.attempt_spawn(WALL,self.algo_2_fixed_walls_first_layer)
            # 4. try build the second layer walls
            game_state.attempt_spawn(WALL,self.algo_2_fixed_walls_second_layer)
            # 5. try build the level 1 supports
            game_state.attempt_spawn(SUPPORT, self.algo_2_supports_lvl_1)

            # 5. if the enemy's bottom is strong, we try to send demolishers and scouts from the middle opening
            #    if the enemy's up is strong, we try to send demolishers and scouts from the side opening
            #       if the left is strong, we open the right side
            #       if the right is strong, we open the left side

            if enemy_info[BOTTOM] >= enemy_info[UP]:
                # open the middle, thus close the left and right sides
                game_state.attempt_spawn(WALL, self.algo_2_left_openers)
                game_state.attempt_spawn(WALL, self.algo_2_right_openers)
            else:
                game_state.attempt_spawn(WALL, self.algo_2_mid_openers)
                if enemy_info[LEFT] >= enemy_info[RIGHT]:
                    game_state.attempt_spawn(WALL, self.algo_2_left_openers)
                else:
                    game_state.attempt_spawn(WALL, self.algo_2_right_openers)
            # 6. delete the openers so we can redecide which side to open in the next round
            game_state.attempt_remove(self.algo_2_left_openers)
            game_state.attempt_remove(self.algo_2_right_openers)
            game_state.attempt_remove(self.algo_2_mid_openers)
            # 7. try upgrade the level 1 support
            game_state.attempt_upgrade(self.algo_2_supports_lvl_1)

            # 8. try build and upgrade the level 2 support if we have extra SP
            game_state.attempt_spawn(SUPPORT, self.algo_2_supports_lvl_2)
            game_state.attempt_upgrade(self.algo_2_supports_lvl_2)

            # 9. if detecting that the enemy holds more than 14 MP, send one interceptor to defend the potential attack
            if game_state.get_resource(MP, 1) >= 14:
                if enemy_info[LEFT] >= enemy_info[RIGHT]:
                    game_state.attempt_spawn(INTERCEPTOR, self.algo_2_attack_left_side, 1)
                else:
                    game_state.attempt_spawn(INTERCEPTOR, self.algo_2_attack_right_side, 1)


    '''
    algo2 Attack handles the following:
    1. Place scouts
    2. Place demolisher
    '''
    def algo_2_attack(self, game_state, enemy_info):
        # in the early game, send demolisher to the strong side to harass them
        if game_state.turn_number <= 6:
            if enemy_info[LEFT] >= enemy_info[RIGHT]:
                if enemy_info[BOTTOM] >= enemy_info[UP]:
                    game_state.attempt_spawn(DEMOLISHER, self.algo_2_attack_left_side, 1)
                else:
                    game_state.attempt_spawn(DEMOLISHER, self.algo_2_attack_left_mid, 1)
            else:
                if enemy_info[BOTTOM] >= enemy_info[UP]:
                    game_state.attempt_spawn(DEMOLISHER, self.algo_2_attack_right_side, 1)
                else:
                    game_state.attempt_spawn(DEMOLISHER, self.algo_2_attack_right_mid, 1)
        # in late game, do the opposite. We send scouts to the weak side to quickly score
        # but also send demolisher to the strong side to harass
        else:
            # don't attack when we have too few MP
            if game_state.get_resource(MP) < 12:
                return
            # if the previous attack we placed demolisher, this round we place scout

            if enemy_info[BOTTOM] >= enemy_info[UP]:
                if enemy_info[LEFT] >= enemy_info[RIGHT]:
                    game_state.attempt_spawn(SCOUT if self.algo_2_placed_demolisher else DEMOLISHER, self.algo_2_attack_left_side ,1000)
                else:
                    game_state.attempt_spawn(SCOUT if self.algo_2_placed_demolisher else DEMOLISHER, self.algo_2_attack_right_side, 1000)
            else:

                if enemy_info[LEFT] >= enemy_info[RIGHT]:
                    game_state.attempt_spawn(SCOUT if self.algo_2_placed_demolisher else DEMOLISHER, self.algo_2_attack_left_mid ,1000)
                else:
                    game_state.attempt_spawn(SCOUT if self.algo_2_placed_demolisher else DEMOLISHER, self.algo_2_attack_right_mid ,1000)
            self.algo_2_placed_demolisher = not self.algo_2_placed_demolisher






    """
    Pre-defined function for detect enemy
    to help us change algo
    """
    def which_side_is_weak(self, game_state, unit_type = None):
        left_enemy = self.detect_enemy_unit(game_state, unit_type, valid_x = self.Area_left_x, valid_y = self.Area_left_y)
        right_enemy = self.detect_enemy_unit(game_state, unit_type, valid_x = self.Area_right_x, valid_y = self.Area_right_y)
        middle_enemy = self.detect_enemy_unit(game_state, unit_type, valid_x = self.Area_middle_x, valid_y = self.Area_middle_y)
        middle_enemy = middle_enemy * self.algo1_judgeSide_weighted
        list_weak = [left_enemy, right_enemy , middle_enemy]
        # return 0, 1, 2
        return list_weak.index(min(list_weak))

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """
    def algo1_v(self, game_state):
        """
        V - version algo
        Using scouts to attack sides
        """
        # Defence
        # Round 1
        if game_state.turn_number == 0:
            game_state.attempt_spawn(TURRET, self.algo1_starting_turrent)
            game_state.attempt_upgrade(self.algo1_starting_turrent)
            game_state.attempt_spawn(WALL, self.algo1_starting_wall)

        # Round n
        else:
            if self.action_turn != game_state.turn_number:
                game_state.attempt_spawn(TURRET, self.algo1_moving_turrent_left)
                game_state.attempt_spawn(TURRET, self.algo1_moving_turrent_right)
                game_state.attempt_spawn(WALL, self.algo1_moving_wall)
                game_state.attempt_upgrade(self.algo1_moving_turrent_left)
                game_state.attempt_upgrade(self.algo1_moving_turrent_right)

            game_state.attempt_spawn(TURRET, self.algo1_starting_turrent)
            game_state.attempt_upgrade(self.algo1_starting_turrent)

            game_state.attempt_spawn(WALL, self.algo1_regular_wall)
            game_state.attempt_spawn(SUPPORT, self.algo1_regular_support)
            game_state.attempt_upgrade(self.algo1_critical_support)
            game_state.attempt_upgrade(self.algo1_regular_support)

        # Attack
        # <= Round 5  Mainly defense, wait for our structures to build up
        if game_state.turn_number <= 5:
            deploy_index = random.randint(0, len(self.algo1_deploy_mid_bottom) - 1)
            deploy_location = self.algo1_deploy_mid_bottom[deploy_index]
            while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP]:
                game_state.attempt_spawn(INTERCEPTOR, deploy_location)

        elif game_state.turn_number == self.action_turn:
            self.algo1_v_attack(game_state)

        else:
            if game_state.turn_number % 4 == 0:
                self.side = self.which_side_is_weak(game_state, unit_type = TURRET)
                self.action_turn = game_state.turn_number + 1

                if self.side == 0:
                    game_state.attempt_remove(self.algo1_moving_turrent_left)
                elif self.side == 1:
                    game_state.attempt_remove(self.algo1_moving_turrent_right)
                else:
                    game_state.attempt_remove(self.algo1_moving_wall)

            deploy_index = random.randint(0, len(self.algo1_deploy_bottom_all) - 1)
            deploy_location = self.algo1_deploy_bottom_all[deploy_index]
            #while game_state.get_resource(MP) >= 12:
            game_state.attempt_spawn(INTERCEPTOR, deploy_location, num = int(game_state.get_resource(MP) - 15))
            #game_state.attempt_spawn(INTERCEPTOR, deploy_location)

    def algo1_v_attack(self, game_state):

        if self.side == 0: # Go left
            #while game_state.get_resource(MP) >= game_state.type_cost(SCOUT)[MP]:
            #if self.detect_enemy_unit(game_state, TURRET, valid_x = self.Area_left_x, valid_y = self.Area_left_y) + self.detect_enemy_unit(game_state, WALL, valid_x = self.Area_left_x, valid_y = self.Area_left_y) >= 3:
            if self.detect_enemy_unit(game_state, unit_type = WALL, valid_x = self.Area_left_x, valid_y = self.Area_left_y) + self.detect_enemy_unit(game_state, TURRET, valid_x = self.Area_left_x, valid_y = self.Area_left_y) >= 4:
                game_state.attempt_spawn(DEMOLISHER, self.algo1_deploy_right, 1000)
            game_state.attempt_spawn(SCOUT, self.algo1_deploy_right, 1000)

        elif self.side == 1: # Go right_enemy
            #while game_state.get_resource(MP) >= game_state.type_cost(SCOUT)[MP]:
            #game_state.attempt_spawn(DEMOLISHER, self.algo1_deploy_upper_right)
            #if self.detect_enemy_unit(game_state, TURRET, valid_x = self.Area_right_x, valid_y = self.Area_right_y) + self.detect_enemy_unit(game_state, WALL, valid_x = self.Area_right_x, valid_y = self.Area_right_y) >= 3:

            if self.detect_enemy_unit(game_state, unit_type = WALL, valid_x = self.Area_right_x, valid_y = self.Area_right_y) + self.detect_enemy_unit(game_state, TURRET, valid_x = self.Area_right_x, valid_y = self.Area_right_y) >= 4:
                game_state.attempt_spawn(DEMOLISHER, self.algo1_deploy_left, 1000)
            #game_state.attempt_spawn(DEMOLISHER, self.algo1_deploy_upper_right, 2)
            game_state.attempt_spawn(SCOUT, self.algo1_deploy_left, 1000)

        else: # Go middle
            #while game_state.get_resource(MP) >= game_state.type_cost(SCOUT)[MP]:
            #deploy_index = random.randint(0, len(self.algo1_deploy_middle) - 1)
            #deploy_location = self.algo1_deploy_middle[deploy_index]

            #game_state.attempt_spawn(DEMOLISHER, self.algo1_deploy_upper_right, 2)
            deploy_index = random.randint(0, len(self.algo1_deploy_bottom_all) - 1)
            deploy_location = self.algo1_deploy_bottom_all[deploy_index]
            if self.detect_enemy_unit(game_state, unit_type = WALL, valid_x = self.Area_middle_x, valid_y = self.Area_middle_y) + self.detect_enemy_unit(game_state, TURRET, valid_x = self.Area_middle_x, valid_y = self.Area_middle_y) >= len(self.Area_middle_x) * len(self.Area_middle_y) / 4:
                game_state.attempt_spawn(DEMOLISHER, deploy_location, 1000)
            game_state.attempt_spawn(SCOUT, deploy_location, 1000)


    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units



    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
