import sys
from instance_manager.satplan_instance import SatPlanInstance, SatPlanInstanceMapper
from pysat.solvers import Glucose4
import time
from datetime import timedelta


def create_literal_for_level(level, literal):
    pure_atom = literal.replace("~","")
    return f"~{level}_{pure_atom}" if literal[0] == "~" else f"{level}_{pure_atom}"

def create_literals_for_level_from_list(level, literals):
    return [create_literal_for_level(level, literal) for literal in literals]

def create_state_from_true_atoms(true_atoms, all_atoms):
    initial_state = [f"~{atom}" for atom in all_atoms if atom not in true_atoms]
    return true_atoms + initial_state

def create_state_from_literals(literals, all_atoms):
    positive_literals = [literal for literal in literals if literal[0] != "~"]
    return create_state_from_true_atoms(positive_literals, all_atoms)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <filename>")
        sys.exit(1)

    object_satplan_instance = SatPlanInstance(sys.argv[1])
    level = 1

    start_time = time.time()

    while (True):
        formula = Glucose4()
        object_satplan_instance_mapper = SatPlanInstanceMapper()

        level_initial_state = create_literals_for_level_from_list(0,object_satplan_instance.get_initial_state())

        object_satplan_instance_mapper.add_list_of_literals_to_mapping(level_initial_state)

        #ADD INITIAL STATE
        for initial_atom in object_satplan_instance_mapper.get_list_of_literals_from_mapping(level_initial_state):
            formula.add_clause([initial_atom])

        other_states = create_literals_for_level_from_list(0,object_satplan_instance.get_state_atoms())

        #NEGA TODOS OS OUTROS ESTADOS
        for state in other_states:
            if (state not in level_initial_state):
                object_satplan_instance_mapper.add_literal_to_mapping(state)
                state_int = object_satplan_instance_mapper.get_literal_from_mapping(state)
                formula.add_clause([-state_int])

        #ADD FINAL STATE
        level_final_state = create_literals_for_level_from_list(level, object_satplan_instance.get_final_state())
        object_satplan_instance_mapper.add_list_of_literals_to_mapping(level_final_state)
        for final_atom in object_satplan_instance_mapper.get_list_of_literals_from_mapping(level_final_state):
            formula.add_clause([final_atom])
        

        all_actions = []

        for i in range(level):
            #ESCOLHER UMA AÇÃO
            actions_per_level = create_literals_for_level_from_list(i, object_satplan_instance.get_actions())

            for item in actions_per_level:
                all_actions.append(item)

            object_satplan_instance_mapper.add_list_of_literals_to_mapping(actions_per_level)
            actions_int = object_satplan_instance_mapper.get_list_of_literals_from_mapping(actions_per_level)
            formula.add_clause(actions_int)

            #SOMENTE UMA AÇÃO PODE SER ESCOLHIDA POR LEVEL
            for action in actions_int:
                for action_b in actions_int:
                    if (action_b != action):
                        formula.add_clause([-action, -action_b])

            #REGRA PARA PRE CONDICOES
            for action in object_satplan_instance.get_actions():
                preconditions_per_level = create_literals_for_level_from_list(i, object_satplan_instance.get_action_preconditions(action))
                object_satplan_instance_mapper.add_list_of_literals_to_mapping(preconditions_per_level)

                for precondition in preconditions_per_level:
                    formula.add_clause([-object_satplan_instance_mapper.get_literal_from_mapping(f"{i}_{action}"), object_satplan_instance_mapper.get_literal_from_mapping(precondition)])
                    
                posconditions_per_level = create_literals_for_level_from_list(i+1, object_satplan_instance.get_action_posconditions(action))
                object_satplan_instance_mapper.add_list_of_literals_to_mapping(posconditions_per_level)

                for poscondition in posconditions_per_level:
                    formula.add_clause([-object_satplan_instance_mapper.get_literal_from_mapping(f"{i}_{action}"), object_satplan_instance_mapper.get_literal_from_mapping(poscondition)])

                for state in object_satplan_instance.get_state_atoms():
                    state_in_next_level = create_literal_for_level(i+1, state)
                    state_in_this_level = create_literal_for_level(i, state)

                    if( state_in_next_level not in posconditions_per_level and f"~{state_in_next_level}" not in posconditions_per_level ):
                        object_satplan_instance_mapper.add_literal_to_mapping(state_in_next_level)
                        object_satplan_instance_mapper.add_literal_to_mapping(state_in_this_level)

                        state_in_next_level_int = object_satplan_instance_mapper.get_literal_from_mapping(state_in_next_level)
                        state_in_this_level_int = object_satplan_instance_mapper.get_literal_from_mapping(state_in_this_level)

                        formula.add_clause([-object_satplan_instance_mapper.get_literal_from_mapping(f"{i}_{action}"), -state_in_this_level_int, state_in_next_level_int])
                        formula.add_clause([-object_satplan_instance_mapper.get_literal_from_mapping(f"{i}_{action}"), state_in_this_level_int, -state_in_next_level_int])

        if formula.solve():
            print(f"SAT em {i+1} passos!")

            end_time = time.time()               

            model = formula.get_model()

            for action in object_satplan_instance_mapper.get_list_of_literals_from_mapping_reverse(model):
                if(action in all_actions):
                    print(action)

            print(f"Resolvido em {end_time - start_time} segundos")
            break
        else:
            print(f"NÃO-SAT para {i+1} passos...")
            level += 1