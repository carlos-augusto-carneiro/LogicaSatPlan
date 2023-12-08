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

    #Adicionando os literais da instância ao Mapping
    objetoSatPlanInstanceMapper.add_list_of_literals_to_mapping(objetoSatPlanInstance.get_atoms())

    #Adicionando todos os estados como negativos
    inicializacao = []
    for stateInt in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.get_state_atoms()):
        inicializacao.append(stateInt*(-1))

    print(f"Atoms inicializados negados: {inicializacao}")
    formula.add_clause(inicializacao)
    sequente.append(inicializacao)

    #Adicionando o estado inicial
    estadoInicial = []
    for inicialStateInt in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.get_initial_state()):
        estadoInicial.append(inicialStateInt)

    print(f"Estado inicial em int: {estadoInicial}")
    formula.add_clause(estadoInicial)
    sequente.append(estadoInicial)

    #Estado inicial em string
    esatdoInicialString = []
    for inicialStateString in objetoSatPlanInstance.get_initial_state():
        esatdoInicialString.append(inicialStateString)

    print(f"Estado inicial em String: {esatdoInicialString}")

    #Estadp final do atoms
    estadoFinal = []
    for finalStateInt in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.get_final_state()):
        estadoFinal.append(finalStateInt)

    print(f"Estado final em int: {estadoFinal}")
    formula.add_clause(estadoFinal)
    sequente.append(estadoFinal)

    #Estado final em string
    finalStateString = []
    for finalString in objetoSatPlanInstance.get_final_state():
        finalStateString.append(finalString)
    print(f"Estado final em string: {finalStateString}")

    #Verificar todas ações em int
    acoesTotalInt = []
    for actionstotal in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.get_actions()):
        acoesTotalInt.append(actionstotal)

    print(f"Todas as acoes em int: {acoesTotalInt}")

    #Verificar todas ações em String
    acoesTotalString = []
    for actionstotalString in objetoSatPlanInstance.get_actions():
        acoesTotalString.append(actionstotalString)

    print(f"Todas as acoes em string: {acoesTotalString}")

    #todos os estado em string 
    estadostotalstring = []
    for estadototal in objetoSatPlanInstance.get_state_atoms():
        estadostotalstring.append(estadototal)

    #Todos os estados em int
    estadostotalint = []
    for estadototalint in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.get_state_atoms()):
        estadostotalint.append(estadototalint)

    print(f"Todas os estados em string e int: {estadostotalint}: {estadostotalstring}")

    '''#Precondicoes em int
    precondioncs = []
    for actionsconditions in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.action_preconditions):
        precondioncs.append(actionsconditions)
    
    print(f"Todas as precondions em int: {precondioncs}")

    #Poscondicoes em int
    posconditions = []
    for poscond in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.action_posconditions):
        posconditions.append(poscond)
    
    print(f"Todas as poscondition em int: {posconditions}")'''


    #Adicionando regras para ações e suas respectivas pre e pos condicoes
    for action in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.get_actions()):
        clause = []
        
        clause.append(action)
        print(f"só para ver oq vai ter1: {clause}")
        for preCondition in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.get_action_preconditions(objetoSatPlanInstanceMapper.get_literal_from_mapping_reverse(action))):
            clause.append(preCondition*(-1))
        print(f"só para ver oq vai ter2: {clause}")
        for posCondition in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.get_action_posconditions(objetoSatPlanInstanceMapper.get_literal_from_mapping_reverse(action))):
            clause.append(posCondition)
        print(f"só para ver oq vai ter3: {clause}")
        formula.add_clause(clause)
        sequente.append(clause)
    print(f"só para ver oq vai ter4: {clause}")
    #Adicionando o estado final
    for atomFinalState in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.get_final_state()):
        formula.add_clause([atomFinalState])
        sequente.append(atomFinalState)
    
    print(sequente)

    print(objetoSatPlanInstanceMapper.mapping)

    if formula.solve():
        # A fórmula é satisfatível, a solução foi encontrada
        model = formula.get_model()
        print(formula.solve())
        print(model)

        # Extraia a sequência de ações da valoração das variáveis
        actions_sequence = []
        level = 1
        for action in model:
            for actionInt in objetoSatPlanInstanceMapper.get_list_of_literals_from_mapping(objetoSatPlanInstance.get_actions()):
                if actionInt in model:
                    actions_sequence.append(f"{level}_{objetoSatPlanInstanceMapper.mapping_reverse[actionInt]}")
                    level += 1
        
        # Imprima a sequência de ações
        print("Sequência de ações:")
        for j in actions_sequence:
            print(j)

    else:
        print("NÃO É SATISFAZÍVEL")

    

    

    

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


