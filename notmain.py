import sys
from instance_manager.satplan_instance import SatPlanInstance, SatPlanInstanceMapper
from pysat.solvers import Glucose3

def create_literal_for_level(level, literal):
    pure_atom = literal.replace("~","")
    return f"{level}_{pure_atom}" if literal[0] != "~" else f"{-level}_{pure_atom}"

def create_literals_for_level_from_list(level, literals):
    return [create_literal_for_level(level, literal) for literal in literals]

def create_state_from_true_atoms(true_atoms, all_atoms):
    initial_state = [f"~{atom}" for atom in all_atoms if atom not in true_atoms]
    return true_atoms + initial_state

def create_state_from_literals(literals, all_atoms):
    positive_literals = [literal for literal in literals if literal[0] != "~"]
    return create_state_from_true_atoms(positive_literals, all_atoms)

def add_clauses_for_action(solver, instanceMapper, action, level):
    action_int = instanceMapper.mapping[action]

    # Adicione cláusulas para as pré-condições da ação
    for precondition in instanceSatPlan.get_action_preconditions(action):
        precondition_int = instanceMapper.mapping[precondition]
        solver.add_clause([-action_int, precondition_int])

    # Adicione cláusulas para as pós-condições da ação
    for poscondition in instanceSatPlan.get_action_posconditions(action):
        poscondition_int = instanceMapper.mapping[poscondition]
        solver.add_clause([action_int, -poscondition_int])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <filename>")
        sys.exit(1)    

    instanceSatPlan = SatPlanInstance(sys.argv[1])
    instanceMapper = SatPlanInstanceMapper()
    solver = Glucose3()

    instanceMapper.add_list_of_literals_to_mapping(instanceSatPlan.get_atoms())

    # Adicione cláusulas para cada ação e suas condições
    for level, action in enumerate(instanceSatPlan.get_actions(), start=1):
        add_clauses_for_action(solver, instanceMapper, action, level)

    # Adicione cláusulas para as condições iniciais
    for initial_atom in instanceSatPlan.get_initial_state():
        initial_atom_int = instanceMapper.mapping[initial_atom]
        solver.add_clause([initial_atom_int])

    # Adicione cláusulas para as condições finais
    for final_atom in instanceSatPlan.get_final_state():
        final_atom_int = instanceMapper.mapping[final_atom]
        solver.add_clause([final_atom_int])

    # Verifique a satisfatibilidade
    if solver.solve():
        # A fórmula é satisfatível, a solução foi encontrada
        model = solver.get_model()

        # Extraia a sequência de ações da valoração das variáveis
        actions_sequence = []
        for level, action in enumerate(instanceSatPlan.get_actions(), start=1):
            action_int = instanceMapper.mapping[action]

            # Verifique se a ação é escolhida no nível atual
            if action_int in model:
                actions_sequence.append(f"{level}_{action}")

        # Imprima a sequência de ações
        print("Sequência de ações:")
        for action in actions_sequence:
            print(action)
    else:
        print("Não foi possível encontrar uma solução.")
