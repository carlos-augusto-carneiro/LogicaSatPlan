import sys
from instance_manager.satplan_instance import SatPlanInstance, SatPlanInstanceMapper
from pysat.solvers import Glucose4

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

    objetoSatPlanInstance = SatPlanInstance(sys.argv[1])
    objetoSatPlanInstanceMapper = SatPlanInstanceMapper()
    formula = Glucose4()
    sequente = []

    levels = 1
    sequente = []

    #INITIAL STATE [CHECK]
    a = create_literals_for_level_from_list(0,objetoSatPlanInstance.get_initial_state())
    a_other_states = create_literals_for_level_from_list(0, objetoSatPlanInstance.get_state_atoms())
    objetoSatPlanInstanceMapper.add_list_of_literals_to_mapping(a)
    
    for state in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(a):
        formula.add_clause([state])
        sequente.append([state])

    for state in create_literals_for_level_from_list(0, objetoSatPlanInstance.get_state_atoms()):
        if state not in a:
            objetoSatPlanInstanceMapper.add_literal_to_mapping(state)
            state_value = objetoSatPlanInstanceMapper.get_literal_from_mapping(state)
            formula.add_clause([-state_value])
            sequente.append([-state_value])


    #FINAL STATE [CHECK]
    b = create_literals_for_level_from_list(levels,objetoSatPlanInstance.get_final_state())
    objetoSatPlanInstanceMapper.add_list_of_literals_to_mapping(b)

    for state in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(b):
        formula.add_clause([state])

    #ACTIONS
    for level in range(levels):
        
        c = create_literals_for_level_from_list(level, objetoSatPlanInstance.get_actions())
        state_atoms = []

        for action in c:
            state_atoms.append(objetoSatPlanInstance.get_state_atoms())

        objetoSatPlanInstanceMapper.add_list_of_literals_to_mapping(c)

        actions_list = objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(c)
        formula.add_clause(actions_list)

        for action in actions_list:
            if action != action+1:
                formula.add_clause([-action,-action+1])

        for action in objetoSatPlanInstance.get_actions():

            d = create_literals_for_level_from_list(level,objetoSatPlanInstance.get_action_preconditions(action))
            objetoSatPlanInstanceMapper.add_list_of_literals_to_mapping(d)
            action_level = f"{level}_"+action
            action_int = objetoSatPlanInstanceMapper.get_literal_from_mapping(action_level)

            for pre_condition in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(d):
                formula.add_clause([-action_int, pre_condition])

            e = create_literals_for_level_from_list(level+1,objetoSatPlanInstance.get_action_posconditions(action))
            objetoSatPlanInstanceMapper.add_list_of_literals_to_mapping(e)

            for pos_condition in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(e):
                formula.add_clause([-action_int, -pos_condition])

        new_state_atoms = create_literals_for_level_from_list(level, objetoSatPlanInstance.get_state_atoms())
        new_state_atoms_b = create_literals_for_level_from_list(level+1, objetoSatPlanInstance.get_state_atoms())
        objetoSatPlanInstanceMapper.add_list_of_literals_to_mapping(new_state_atoms)
        objetoSatPlanInstanceMapper.add_list_of_literals_to_mapping(new_state_atoms_b)
        
        for state in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(new_state_atoms):
            clause = [-action_int]
            clause.append(-state)
            for state_b in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(new_state_atoms_b):
                clause.append(state_b)
                formula.add_clause(clause)

        if formula.solve() == True:
            for action in formula.get_model():
                if action > 0:
                    print(objetoSatPlanInstanceMapper.get_literal_from_mapping_reverse(action))
            break
        else:
            print(f"level {level} não-sat")
            level += 1

    for clausula in sequente:
        print(clausula)






