import sys
from instance_manager.satplan_instance import SatPlanInstance, SatPlanInstanceMapper
from pysat.solvers import Glucose3

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

    instanceSatPlan = SatPlanInstance(sys.argv[1])
    instanceMapper = SatPlanInstanceMapper()
    solver = Glucose3()

    instanceMapper.add_list_of_literals_to_mapping(instanceSatPlan.get_atoms())

    for initial_atom in instanceSatPlan.get_initial_state():
        if initial_atom[0] == "~":
            initial_atom_int = instanceMapper.mapping[initial_atom.replace("~", "")]    
        else:
            initial_atom_int = instanceMapper.mapping[initial_atom]
        solver.add_clause([initial_atom_int])

'''
    for action in instanceSatPlan.get_actions():
        if action[0] == '~':
            action_int = instanceMapper.mapping[action.replace("~", "")]    
        else:
            action_int = instanceMapper.mapping[action]

        # Adicione cláusulas para as pré-condições da ação
        for precondition in instanceSatPlan.get_action_preconditions(action):
            if precondition[0] == "~":
                precondition_int = instanceMapper.mapping[precondition.replace("~", "")]    
            else:
                precondition_int = instanceMapper.mapping[precondition]
            solver.add_clause([action_int*(-1), precondition_int])

        # Adicione cláusulas para as pós-condições da ação
        for poscondition in instanceSatPlan.get_action_posconditions(action):
            if poscondition[0] == "~":
                poscondition_int = instanceMapper.mapping[poscondition.replace("~", "")]
            else:
                poscondition_int = instanceMapper.mapping[poscondition]
            solver.add_clause([action_int, poscondition_int*(-1)])

    # Adicione cláusulas para as condições iniciais

    # Adicione cláusulas para as condições finais
    for final_atom in instanceSatPlan.get_final_state():
        if final_atom[0] == "~":
            final_atom_int = instanceMapper.mapping[final_atom.replace("~", "")]    
        else:
            final_atom_int = instanceMapper.mapping[final_atom]
        solver.add_clause([final_atom_int])

    # Verifique a satisfatibilidade
    if solver.solve():
        # A fórmula é satisfatível, a solução foi encontrada
        model = solver.get_model()
        print(model)
    else:
        print("Não foi possível encontrar uma solução.")
        '''
'''
        # Extraia a sequência de ações da valoração das variáveis
        actions_sequence = []
        for level, atom in enumerate(instanceSatPlan.get_actions(), start=1):
            atom_int = instanceMapper.mapping[atom]

            # Verifique se a ação é escolhida no nível atual
            if atom_int in model:
                actions_sequence.append(f"{level}_{atom}")

        # Imprima a sequência de ações
        print("Sequência de ações:")
        for action in actions_sequence:
            print(action)
'''




'''
    #o codigo a seguir é exemplo de uso
    satPlanInstance = SatPlanInstance(sys.argv[1])
    instanceMapper  = SatPlanInstanceMapper()
    instanceMapper.add_list_of_literals_to_mapping(satPlanInstance.get_atoms())
    print(instanceMapper.mapping)
    a = satPlanInstance.get_state_atoms()
    a = satPlanInstance.get_action_posconditions("pick-up_b")
    b = instanceMapper.get_list_of_literals_from_mapping(a)
    print(b)
    print(instanceMapper.get_literal_from_mapping_reverse(-8))
    print(create_literals_for_level_from_list(5,a))
    print(create_state_from_literals(['holding_b','on_a_b'],satPlanInstance.get_atoms()))
'''


