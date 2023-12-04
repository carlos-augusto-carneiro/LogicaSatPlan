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
    # Crie uma instância do SatPlanInstanceMapper
    instanceMapper = SatPlanInstanceMapper()

    # Adquira os átomos e ações da instância
    all_atoms = instanceSatPlan.get_atoms()
    actions = instanceSatPlan.get_actions()

    # Mapeie os átomos para inteiros positivos
    for atom in all_atoms:
        instanceMapper.add_literal_to_mapping(atom)

    # Inicialize o solver Glucose3
    solver = Glucose3()

    # Crie a lista de cláusulas para a fórmula SAT
    clauses = []

    # Adicione as cláusulas para a configuração inicial
    initial_state_literals = create_state_from_literals(instanceSatPlan.get_initial_state(), all_atoms)
    clauses.append(instanceMapper.get_list_of_literals_from_mapping(initial_state_literals))

    # Adicione as cláusulas para a configuração final
    final_state_literals = create_state_from_literals(instanceSatPlan.get_final_state(), all_atoms)
    clauses.append(instanceMapper.get_list_of_literals_from_mapping(final_state_literals))

    # Adicione cláusulas para garantir que cada ação seja executada no máximo uma vez
    for idx in range(1, len(actions) + 1):
        action_literals = create_literals_for_level_from_list(idx, actions)
        clauses.append([-literal for literal in instanceMapper.get_list_of_literals_from_mapping(action_literals)])
        for j in range(1, len(actions) + 1):
            if j != idx:
                clauses.append([-literal for literal in instanceMapper.get_list_of_literals_from_mapping(action_literals)])

    # Adicione cláusulas para garantir que apenas uma ação seja tomada em cada nível
    for idx in range(1, len(actions) + 1):
        action_literals = create_literals_for_level_from_list(idx, actions)
        clauses.append(instanceMapper.get_list_of_literals_from_mapping(action_literals))

    # Adicione cláusulas para garantir a sequência correta de ações
    for idx in range(1, len(actions)):
        current_action_literals = create_literals_for_level_from_list(idx, actions)
        next_action_literals = create_literals_for_level_from_list(idx + 1, actions)
        for action_literal in current_action_literals:
            clauses.append([-instanceMapper.get_literal_from_mapping(action_literal)])
            clauses.append([instanceMapper.get_literal_from_mapping(action_literal), instanceMapper.get_literal_from_mapping(next_action_literals[0])])

    # Adicione cláusulas para garantir as pré-condições e pós-condições corretas
    for idx, action in enumerate(actions, start=1):
        preconditions_literals = create_state_from_literals(instanceSatPlan.get_action_preconditions(action), all_atoms)
        postconditions_literals = create_state_from_literals(instanceSatPlan.get_action_posconditions(action), all_atoms)
        action_literals = create_literals_for_level_from_list(idx, actions)

        # Pré-condições verdadeiras para executar a ação
        for precondition_literal in preconditions_literals:
            clauses.append([instanceMapper.get_literal_from_mapping(precondition_literal)] + [-literal for literal in instanceMapper.get_list_of_literals_from_mapping(action_literals)])

        # Pós-condições após executar a ação
        for postcondition_literal in postconditions_literals:
            clauses.append([instanceMapper.get_literal_from_mapping(postcondition_literal), instanceMapper.get_literal_from_mapping(action_literals)])

    # Adicione cláusulas para garantir a consistência entre os níveis
    for idx in range(1, len(actions)):
        current_action_literals = create_literals_for_level_from_list(idx, actions)
        next_action_literals = create_literals_for_level_from_list(idx + 1, actions)
        for current_literal, next_literal in zip(current_action_literals, next_action_literals):
            clauses.append([-instanceMapper.get_literal_from_mapping(current_literal), instanceMapper.get_literal_from_mapping(next_literal)])

    # Adicione todas as cláusulas ao solver
    for clause in clauses:
        solver.add_clause(clause)

    # Resolva o SAT
    if solver.solve():
        print("Solução encontrada:")
        model = solver.get_model()
        model_literals = instanceMapper.get_list_of_literals_from_mapping_reverse(model)
        print(model_literals)
    else:
        print("Não foi possível encontrar uma solução.")