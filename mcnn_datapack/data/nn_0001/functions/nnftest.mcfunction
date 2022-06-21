scoreboard players set #exp_temp_0 nn_eval 786432
scoreboard players operation #exp_temp_0 nn_eval -= exp_test nn_eval
scoreboard players set exp_test_result nn_eval 786432
scoreboard players operation #exp_temp_1 nn_eval = exp_test nn_eval
scoreboard players operation #exp_temp_1 nn_eval *= #TWO nn_eval
scoreboard players operation exp_test_result nn_eval += #exp_temp_1 nn_eval
scoreboard players operation #exp_temp_2 nn_eval = exp_test nn_eval
scoreboard players operation #exp_temp_2 nn_eval /= #TWO nn_eval
scoreboard players operation #exp_temp_2 nn_eval /= #sqrtFPSF nn_eval
scoreboard players operation #exp_temp_2 nn_eval *= exp_test nn_eval
scoreboard players operation #exp_temp_2 nn_eval /= #sqrtFPSF nn_eval
scoreboard players operation exp_test_result nn_eval += #exp_temp_2 nn_eval
scoreboard players operation #exp_temp_0 nn_eval /= #sqrtFPSF nn_eval
scoreboard players operation exp_test_result nn_eval *= #sqrtFPSF nn_eval
scoreboard players operation exp_test_result nn_eval /= #exp_temp_0 nn_eval
