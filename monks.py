"""Creates a scenario for running Monk tests."""


from AoE2ScenarioParser.aoe2_scenario import AoE2Scenario
from AoE2ScenarioParser.datasets.conditions import Condition
from AoE2ScenarioParser.datasets.effects import Effect
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.techs import Tech
from AoE2ScenarioParser.datasets.units import Unit


FILE_INPUT = 'monk-test.aoe2scenario'
FILE_OUTPUT = 'out.aoe2scenario'

# Number of trials = X_MAX // 2 * Y_MAX
# X_MAX must be even.
# A Tiny map has 120 * 120 tiles.
X_MAX = 20
Y_MAX = 100
# X_MAX = 1
# Y_MAX = 1
NUM_TRIALS = X_MAX // 2 * Y_MAX


def create_out():
    """The main function to create the output file."""
    scn = AoE2Scenario.from_file(FILE_INPUT)
    tmgr = scn.trigger_manager
    umgr = scn.unit_manager

    # Initializes Militia Attack Stance and Monk Accuracy.
    init = tmgr.add_trigger('Init')
    change_obj_stance = init.add_effect(Effect.CHANGE_OBJECT_STANCE)
    change_obj_stance.object_list_unit_id = Unit.MILITIA
    change_obj_stance.source_player = Player.TWO
    change_obj_stance.attack_stance = 3 # No Attack Stance
    accuracy_init = init.add_effect(Effect.MODIFY_ATTRIBUTE)
    accuracy_init.quantity = 0
    accuracy_init.object_list_unit_id = Unit.MONK
    accuracy_init.source_player = Player.ONE
    accuracy_init.operation = 1 # Set
    accuracy_init.object_attributes = 11 # Accuracy Percent
    tmgr.add_variable('Accuracy Percent', 0)
    count_init = init.add_effect(Effect.CHANGE_VARIABLE)
    count_init.quantity = 0
    count_init.operation = 1 # Set
    count_init.message = 'Accuracy Percent'
    count_init.from_variable = 0
    illumination = init.add_effect(Effect.RESEARCH_TECHNOLOGY)
    illumination.source_player = Player.ONE
    illumination.technology = Tech.ILLUMINATION
    illumination.force_research_technology = 1
    redemption = init.add_effect(Effect.RESEARCH_TECHNOLOGY)
    redemption.technology = Tech.REDEMPTION
    redemption.force_research_technology = 1

    # Displays the current Accuracy Percent as an objective.
    display = tmgr.add_trigger('Display Accuracy Percent')
    display.display_on_screen = 1
    display.short_description = 'Accuracy Percent: <Accuracy Percent>'
    gaia_defeated = display.add_condition(Condition.PLAYER_DEFEATED)
    gaia_defeated.source_player = Player.GAIA

    # TODO Monk conversion speed
    # TODO trigger to "reset" the loop

    # Adds the Monks and Militia to the scenario.
    convert = tmgr.add_trigger('Convert')
    advance_loop = tmgr.add_trigger('Advance Loop')

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

    activate_advance_loop = convert.add_effect(Effect.ACTIVATE_TRIGGER)
    activate_advance_loop.trigger_id = advance_loop.trigger_id

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

    advance_loop.enabled = 0
    advance_loop.looping = 1

    p2_0_militia = advance_loop.add_condition(Condition.OWN_FEWER_OBJECTS)
    p2_0_militia.amount_or_quantity = 0
    p2_0_militia.object_list = Unit.MILITIA
    p2_0_militia.source_player = Player.TWO

    accuracy_sub_100 = advance_loop.add_condition(Condition.VARIABLE_VALUE)
    accuracy_sub_100.amount_or_quantity = 100
    accuracy_sub_100.comparison = 1 # Less
    accuracy_sub_100.variable = 0

    deactivate_advance_loop = advance_loop.add_effect(Effect.DEACTIVATE_TRIGGER)
    deactivate_advance_loop.trigger_id = advance_loop.trigger_id

    inc_acc_attr = advance_loop.add_effect(Effect.MODIFY_ATTRIBUTE)
    inc_acc_attr.quantity = 1
    inc_acc_attr.object_list_unit_id = Unit.MONK
    inc_acc_attr.source_player = Player.ONE
    inc_acc_attr.operation = 2 # Add
    inc_acc_attr.object_attributes = 11 # Accuracy Percent

    inc_acc_var = advance_loop.add_effect(Effect.CHANGE_VARIABLE)
    inc_acc_var.quantity = 1
    inc_acc_var.operation = 2 # Add
    inc_acc_var.from_variable = 0

    militia_ownership = advance_loop.add_effect(Effect.CHANGE_OWNERSHIP)
    militia_ownership.object_list_unit_id = Unit.MILITIA
    militia_ownership.source_player = Player.ONE
    militia_ownership.target_player = Player.TWO

    reactivate_convert = advance_loop.add_effect(Effect.ACTIVATE_TRIGGER)
    reactivate_convert.trigger_id = convert.trigger_id

    # Ends the Scenario when all conversions have been performed
    end_scenario = tmgr.add_trigger('End Scenario')

    accuracy100 = end_scenario.add_condition(Condition.VARIABLE_VALUE)
    accuracy100.amount_or_quantity = 100
    accuracy100.comparison = 0 # Equal
    accuracy100.variable = 0

    p2_0_militia_end = end_scenario.add_condition(Condition.OWN_FEWER_OBJECTS)
    p2_0_militia_end.amount_or_quantity = 0
    p2_0_militia_end.object_list = Unit.MILITIA
    p2_0_militia_end.source_player = Player.TWO

    declare_victory = end_scenario.add_effect(Effect.DECLARE_VICTORY)
    declare_victory.source_player = Player.ONE

    scn.write_to_file(FILE_OUTPUT)


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
    create_out()
    # view_out()


if __name__ == '__main__':
    main()
