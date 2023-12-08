import sys
from instance_manager.satplan_instance import SatPlanInstance, SatPlanInstanceMapper
from pysat.solvers import Glucose4
from pysat.formula import CNF

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
    solver = Glucose4()
    sal = CNF()

    instanceMapper.add_list_of_literals_to_mapping(instanceSatPlan.get_atoms())

    n_abacaxi = 5

    for i in range(n_abacaxi):
        add_literal_init = create_literals_for_level_from_list(i, instanceSatPlan.get_atoms())
        instanceMapper.add_list_of_literals_to_mapping(add_literal_init)
        lista_actions = instanceMapper.get_list_of_literals_from_mapping(add_literal_init)

        for acao in instanceSatPlan.get_actions():
            tomate = create_literals_for_level_from_list(i, instanceSatPlan.get_action_preconditions(acao))
            instanceMapper.add_list_of_literals_to_mapping(tomate)
            xuxu = create_literals_for_level_from_list(i, instanceSatPlan.get_initial_state())
            instanceMapper.add_list_of_literals_to_mapping(xuxu)
            for iroda in instanceMapper.get_list_of_literals_from_mapping(xuxu):
                sal.append([iroda])
                solver.add_clause([iroda])
                print("Literal adicionado a sal/iroda:", iroda)
            print("Precondi", tomate)
            print("Precondi", instanceMapper.get_list_of_literals_from_mapping(tomate))
            print("Na FNC:", sal)

            pitaya = create_literals_for_level_from_list(i, instanceSatPlan.get_action_posconditions(acao))
            instanceMapper.add_list_of_literals_to_mapping(pitaya)
            abobora = create_literals_for_level_from_list(i, instanceSatPlan.get_initial_state())
            instanceMapper.add_list_of_literals_to_mapping(abobora)
            for eitapapai in instanceMapper.get_list_of_literals_from_mapping(abobora):
                sal.append([eitapapai])
                solver.add_clause([eitapapai])
                print("Literal adicionado a sal/eitapapai:", eitapapai)
            print("Poscondi", pitaya)
            print("Poscondi", instanceMapper.get_list_of_literals_from_mapping(pitaya))
            print("Na FNC:", sal)

    sat_ou_nsat = solver.solve()
    model=solver.get_model()

    if sat_ou_nsat:
        print(solver.get_model())
        for i in model:
            if i in instanceMapper.mapping:
                print(instanceMapper.mapping_reverse[i])
        '''for i in instanceMapper.get_list_of_literals_from_mapping(instanceSatPlan.get_atoms()):
            if i in model:
                print("entrou")
                print(f"{instanceMapper.mapping_reverse[i]}")
'''

    else:
        print('Não foi dessa vez campeão')

    print(instanceMapper.mapping)