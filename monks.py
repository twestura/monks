"""Creates a scenario for running Monk tests."""


from AoE2ScenarioParser.aoe2_scenario import AoE2Scenario
from AoE2ScenarioParser.datasets.conditions import Condition
from AoE2ScenarioParser.datasets.effects import Effect
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.techs import Tech
from AoE2ScenarioParser.datasets.units import Unit


# Scouts have 8 conversion resistance.
# Buildings have 3 conversion resistance.


FILE_INPUT = 'monk-test.aoe2scenario'
FILE_OUTPUT = 'out.aoe2scenario'

# Number of trials = X_MAX // 2 * Y_MAX
# X_MAX must be even.
# A Tiny map has 120 * 120 tiles.
X_MAX = 20
Y_MAX = 100
# X_MAX = 10
# Y_MAX = 10
# X_MAX = 1
# Y_MAX = 1
NUM_TRIALS = X_MAX // 2 * Y_MAX
assert not (X_MAX & 1), f'X_MAX "{X_MAX}" must be even.'

# The initial and final, inclusive, accuracy values to check.
# Requires 0 <= ACCURACY_INIT <= ACCURACY_FINAL <= 100.
# ACCURACY_INIT = 0
# ACCURACY_FINAL = 100
ACCURACY_INIT = 25
ACCURACY_FINAL = 25
assert 0 <= ACCURACY_INIT <= ACCURACY_FINAL <= 100

# The initial and final, inclusive, conversion resistance values.
# Requires 0 <= CONV_RES_INIT <= CONV_RES_FINAL.
CONV_RES_INIT = 0
# CONV_RES_FINAL = 15
CONV_RES_FINAL = 0
assert 0 <= CONV_RES_INIT <= CONV_RES_FINAL


def create_out():
    """The main function to create the output file."""
    scn = AoE2Scenario.from_file(FILE_INPUT)
    tmgr = scn.trigger_manager
    umgr = scn.unit_manager

    # Adds an invisible object so P2 doesn't get defeated.
    # umgr.add_unit(Player.TWO, Unit.INVISIBLE_OBJECT, 0.0, 0.0)

    # Initializes Militia Attack Stance and Monk Accuracy.
    init = tmgr.add_trigger('Init')
    change_obj_stance = init.add_effect(Effect.CHANGE_OBJECT_STANCE)
    change_obj_stance.object_list_unit_id = Unit.MILITIA
    change_obj_stance.source_player = Player.TWO
    change_obj_stance.attack_stance = 3 # No Attack Stance
    accuracy_init = init.add_effect(Effect.MODIFY_ATTRIBUTE)
    accuracy_init.quantity = ACCURACY_INIT
    accuracy_init.object_list_unit_id = Unit.MONK
    accuracy_init.source_player = Player.ONE
    accuracy_init.operation = 1 # Set
    accuracy_init.object_attributes = 11 # Accuracy Percent
    tmgr.add_variable('Accuracy Percent', 0)
    tmgr.add_variable('Conversion Resistance', 1)
    count_init_acc = init.add_effect(Effect.CHANGE_VARIABLE)
    count_init_acc.quantity = ACCURACY_INIT
    count_init_acc.operation = 1 # Set
    count_init_acc.message = 'Accuracy Percent'
    count_init_acc.from_variable = 0
    count_init_res = init.add_effect(Effect.CHANGE_VARIABLE)
    count_init_res.quantity = CONV_RES_INIT
    count_init_res.operation = 1 # Set
    count_init_res.message = 'Conversion Resistance'
    count_init_res.from_variable = 1
    faith_regeneration = init.add_effect(Effect.MODIFY_RESOURCE)
    faith_regeneration.tribute_list = 35 # Faith
    faith_regeneration.source_player = Player.ONE
    faith_regeneration.operation = 1 # Set
    faith_regeneration.quantity = 3000
    redemption = init.add_effect(Effect.RESEARCH_TECHNOLOGY)
    redemption.technology = Tech.REDEMPTION
    redemption.force_research_technology = 1

    # Displays the current Accuracy Percent as an objective.
    display = tmgr.add_trigger('Display Accuracy Percent')
    display.display_on_screen = 1
    display.short_description = '\n'.join([
        'Conversion Resistance: <Conversion Resistance>',
        'Accuracy Percent: <Accuracy Percent>'
    ])
    gaia_defeated = display.add_condition(Condition.PLAYER_DEFEATED)
    gaia_defeated.source_player = Player.GAIA

    # Adds the Monks and Militia to the scenario.
    convert = tmgr.add_trigger('Convert')
    advance_loop_acc = tmgr.add_trigger('Advance Loop Accuracy')
    advance_loop_res = tmgr.add_trigger('Advance Loop Conversion Resistance')

    convert.enabled = 0 # Off
    activate_convert = init.add_effect(Effect.ACTIVATE_TRIGGER)
    activate_convert.trigger_id = convert.trigger_id
    convert.looping = 1 # Yes

    convert_timer = convert.add_condition(Condition.TIMER)
    convert_timer.timer = 1

    convert_p2_is_reset = convert.add_condition(Condition.OWN_OBJECTS)
    convert_p2_is_reset.amount_or_quantity = NUM_TRIALS
    convert_p2_is_reset.source_player = Player.TWO
    convert_p2_is_reset.object_list = Unit.MILITIA

    deactivate_convert = convert.add_effect(Effect.DEACTIVATE_TRIGGER)
    deactivate_convert.trigger_id = convert.trigger_id

    activate_advance_loop_acc = convert.add_effect(Effect.ACTIVATE_TRIGGER)
    activate_advance_loop_acc.trigger_id = advance_loop_acc.trigger_id
    activate_advance_loop_res = convert.add_effect(Effect.ACTIVATE_TRIGGER)
    activate_advance_loop_res.trigger_id = advance_loop_res.trigger_id

    for y in range(Y_MAX):
        for x in range(0, X_MAX, 2):
            monk = umgr.add_unit(
                player=Player.ONE,
                unit_id=Unit.MONK,
                x=x+0.5,
                y=y+0.5,
            )
            militia = umgr.add_unit(
                player=Player.TWO,
                unit_id=Unit.MILITIA,
                x=x+1.5,
                y=y+0.5,
                rotation=16
            )
            task = convert.add_effect(Effect.TASK_OBJECT)
            task.source_player = Player.ONE
            task.number_of_units_selected = 1
            task.selected_object_ids = monk.reference_id
            task.location_object_reference = militia.reference_id

    advance_loop_acc.enabled = 0
    advance_loop_acc.looping = 1

    p2_0_militia_acc = advance_loop_acc.add_condition(
        Condition.OWN_FEWER_OBJECTS
    )
    p2_0_militia_acc.amount_or_quantity = 0
    p2_0_militia_acc.object_list = Unit.MILITIA
    p2_0_militia_acc.source_player = Player.TWO

    accuracy_sub_100 = advance_loop_acc.add_condition(Condition.VARIABLE_VALUE)
    accuracy_sub_100.amount_or_quantity = ACCURACY_FINAL
    accuracy_sub_100.comparison = 1 # Less
    accuracy_sub_100.variable = 0

    deactivate_advance_loop_acc = advance_loop_acc.add_effect(
        Effect.DEACTIVATE_TRIGGER
    )
    deactivate_advance_loop_acc.trigger_id = advance_loop_acc.trigger_id
    deactivate_advance_loop_res = advance_loop_acc.add_effect(
        Effect.DEACTIVATE_TRIGGER
    )
    deactivate_advance_loop_res.trigger_id = advance_loop_res.trigger_id

    inc_acc_attr = advance_loop_acc.add_effect(Effect.MODIFY_ATTRIBUTE)
    inc_acc_attr.quantity = 1
    inc_acc_attr.object_list_unit_id = Unit.MONK
    inc_acc_attr.source_player = Player.ONE
    inc_acc_attr.operation = 2 # Add
    inc_acc_attr.object_attributes = 11 # Accuracy Percent

    inc_acc_var = advance_loop_acc.add_effect(Effect.CHANGE_VARIABLE)
    inc_acc_var.quantity = 1
    inc_acc_var.operation = 2 # Add
    inc_acc_var.from_variable = 0

    militia_ownership_acc = advance_loop_acc.add_effect(Effect.CHANGE_OWNERSHIP)
    militia_ownership_acc.object_list_unit_id = Unit.MILITIA
    militia_ownership_acc.source_player = Player.ONE
    militia_ownership_acc.target_player = Player.TWO

    reactivate_convert_acc = advance_loop_acc.add_effect(
        Effect.ACTIVATE_TRIGGER
    )
    reactivate_convert_acc.trigger_id = convert.trigger_id


    p2_0_militia_res = advance_loop_res.add_condition(
        Condition.OWN_FEWER_OBJECTS
    )
    p2_0_militia_res.amount_or_quantity = 0
    p2_0_militia_res.object_list = Unit.MILITIA
    p2_0_militia_res.source_player = Player.TWO

    accuracy_is_100 = advance_loop_res.add_condition(Condition.VARIABLE_VALUE)
    accuracy_is_100.amount_or_quantity = ACCURACY_FINAL
    accuracy_is_100.comparison = 0 # Equal
    accuracy_is_100.variable = 0

    res_sub_100 = advance_loop_res.add_condition(Condition.VARIABLE_VALUE)
    res_sub_100.amount_or_quantity = CONV_RES_FINAL
    res_sub_100.comparison = 1 # Less
    res_sub_100.variable = 1

    deactivate_advance_loop_acc2 = advance_loop_res.add_effect(
        Effect.DEACTIVATE_TRIGGER
    )
    deactivate_advance_loop_acc2.trigger_id = advance_loop_res.trigger_id
    deactivate_advance_loop_res2 = advance_loop_res.add_effect(
        Effect.DEACTIVATE_TRIGGER
    )
    deactivate_advance_loop_res2.trigger_id = advance_loop_res.trigger_id

    reset_acc_attr = advance_loop_res.add_effect(Effect.MODIFY_ATTRIBUTE)
    reset_acc_attr.quantity = 0
    reset_acc_attr.object_list_unit_id = Unit.MONK
    reset_acc_attr.source_player = Player.ONE
    reset_acc_attr.operation = 1 # Set
    reset_acc_attr.object_attributes = 11 # Accuracy Percent

    reset_acc_var = advance_loop_res.add_effect(Effect.CHANGE_VARIABLE)
    reset_acc_var.quantity = 0
    reset_acc_var.operation = 1 # Set
    reset_acc_var.from_variable = 0

    inc_res = advance_loop_res.add_effect(Effect.MODIFY_RESOURCE)
    inc_res.quantity = 1
    inc_res.tribute_list = 77 # Conversion Resistance
    inc_res.source_player = Player.ONE
    inc_res.operation = 2 # Add
    inc_res_var = advance_loop_res.add_effect(Effect.CHANGE_VARIABLE)
    inc_res_var.quantity = 1
    inc_res_var.operation = 2 # Add
    inc_res_var.from_variable = 1

    militia_ownership_res = advance_loop_res.add_effect(Effect.CHANGE_OWNERSHIP)
    militia_ownership_res.object_list_unit_id = Unit.MILITIA
    militia_ownership_res.source_player = Player.ONE
    militia_ownership_res.target_player = Player.TWO

    start_loop = advance_loop_res.add_effect(Effect.ACTIVATE_TRIGGER)
    start_loop.trigger_id = convert.trigger_id

    # Ends the Scenario when all conversions have been performed
    end_scenario = tmgr.add_trigger('End Scenario')

    accuracy_final_check = end_scenario.add_condition(Condition.VARIABLE_VALUE)
    accuracy_final_check.amount_or_quantity = ACCURACY_FINAL
    accuracy_final_check.comparison = 0 # Equal
    accuracy_final_check.variable = 0

    conv_res_final_check = end_scenario.add_condition(Condition.VARIABLE_VALUE)
    conv_res_final_check.amount_or_quantity = CONV_RES_FINAL
    conv_res_final_check.comparison = 0 # Equal
    conv_res_final_check.variable = 1

    p2_0_militia_end = end_scenario.add_condition(Condition.OWN_FEWER_OBJECTS)
    p2_0_militia_end.amount_or_quantity = 0
    p2_0_militia_end.object_list = Unit.MILITIA
    p2_0_militia_end.source_player = Player.TWO

    declare_victory = end_scenario.add_effect(Effect.DECLARE_VICTORY)
    declare_victory.source_player = Player.ONE

    scn.write_to_file(FILE_OUTPUT)


def single_scenario(x_max=X_MAX, y_max=Y_MAX,
        file_in=FILE_INPUT, file_out=FILE_OUTPUT):
    """
    Writes a single scenario to the output file.
    """
    if x_max < 0:
        raise ValueError(f'x_max "{x_max}" must be nonnegative.')
    if x_max & 1:
        raise ValueError(f'x_max "{x_max}" must be even.')
    if y_max < 0:
        raise ValueError(f'y_max "{y_max}" must be nonnegative.')

    scn = AoE2Scenario.from_file(file_in)
    tmgr = scn.trigger_manager
    umgr = scn.unit_manager

    init = tmgr.add_trigger('Init Set Attack Stance')
    init.add_effect(Effect.CHANGE_OBJECT_STANCE,
        object_list_unit_id = Unit.MILITIA,
        source_player = Player.TWO,
        attack_stance = 3 # No Attack Stance
    )

    convert = tmgr.add_trigger('Convert')
    convert.add_condition(Condition.TIMER, timer=10)

    for y in range(y_max):
        for x in range(0, x_max, 2):
            monk = umgr.add_unit(
                player=Player.ONE,
                unit_id=Unit.MONK,
                x=x+0.5,
                y=y+0.5,
            )
            militia = umgr.add_unit(
                player=Player.TWO,
                unit_id=Unit.MILITIA,
                x=x+1.5,
                y=y+0.5,
                rotation=16
            )
            convert.add_effect(Effect.TASK_OBJECT,
                source_player = Player.ONE,
                selected_object_ids = monk.reference_id,
                location_object_reference = militia.reference_id
            )

    scn.write_to_file(file_out)


def example():
    """Writes a single example scenario file."""
    # x, y = 20, 100
    # x, y = 2, 1
    # x, y = 20, 10
    # x, y = 120, 120
    x, y = 240, 240
    single_scenario(x, y,
        'monk-test-giant.aoe2scenario', 'out-giant.aoe2scenario')


def view_out():
    """Prints information about the output file. Requires the output exists."""
    scn = AoE2Scenario.from_file(FILE_OUTPUT)
    tmgr = scn.trigger_manager
    # overall_summary = tmgr.get_summary_as_string()
    # print(overall_summary)

    detail_summary = tmgr.get_content_as_string()
    print(detail_summary)


def main():
    """Creates the test scenario."""
    # create_out()
    example()
    # view_out()


if __name__ == '__main__':
    main()
