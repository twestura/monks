"""Creates a scenario for running Monk tests."""


from AoE2ScenarioParser.aoe2_scenario import AoE2Scenario
from AoE2ScenarioParser.datasets.effects import Effect
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.units import Unit


FILE_INPUT = 'monk-test.aoe2scenario'
FILE_OUTPUT = 'out.aoe2scenario'


X_MAX = 10
Y_MAX = 10
# X_MAX = 1
# Y_MAX = 1


def create_out():
    """The main function to create the output file."""
    scn = AoE2Scenario.from_file(FILE_INPUT)
    tmgr = scn.trigger_manager
    umgr = scn.unit_manager

    # Adds initial triggers for No Attack Stance.
    no_attack_stance = tmgr.add_trigger('Set No Attack Stance')
    change_obj_stance = no_attack_stance.add_effect(Effect.CHANGE_OBJECT_STANCE)
    change_obj_stance.object_list_unit_id = Unit.MILITIA
    change_obj_stance.source_player = Player.TWO
    change_obj_stance.attack_stance = 3 # No Attack Stance

    # Adds the Monks and Militia to the scenario.
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
            convert = tmgr.add_trigger(f'Convert ({x}, {y}).')
            task = convert.add_effect(Effect.TASK_OBJECT)
            task.source_player = Player.ONE
            task.number_of_units_selected = 1
            task.selected_object_id = monk.reference_id
            # TODO proper setting of the Monk location directly on the Militia
            task.location_x = x + 1
            task.location_y = y
    scn.write_to_file(FILE_OUTPUT)


def view_out():
    """Debugging file to view the output file. Requires the output exists."""
    scn = AoE2Scenario.from_file(FILE_OUTPUT)
    tmgr = scn.trigger_manager
    overall_summary = tmgr.get_summary_as_string()
    print(overall_summary)

    detail_summary = tmgr.get_content_as_string()
    print(detail_summary)


def main():
    """Creates the test scenario."""
    create_out()
    # view_out()


if __name__ == '__main__':
    main()
