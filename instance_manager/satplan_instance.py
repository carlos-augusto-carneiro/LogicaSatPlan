class SatPlanInstance:
    def __init__(self,filename):
        self.actions = []     #list all actions
        self.action_preconditions = {} #pre conditions to use actions
        self.action_posconditions = {} #pos conditions
        self.initial_state = []
        self.final_state = []
        self.atoms = []
        self.__read_from_file(filename)
        self.__compute_atoms()

    def __compute_atoms(self):
        for action in self.actions:
            self.atoms.append(action)
        for pre_condition in self.action_preconditions.values():
            self.atoms += list(map(lambda x : x.replace("~",""), list(pre_condition)))
        for pos_condition in self.action_posconditions.values():
            self.atoms += list(map(lambda x : x.replace("~",""), list(pos_condition)))
        self.atoms = sorted(list(set(self.atoms)))
        
    def __read_from_file(self, filename):
        with open(filename, "r") as file:
            action = file.readline().strip()
            while action:
                if len(action) == 0:
                    break
                self.actions.append(action)
                self.action_preconditions[action] = file.readline().strip().split(";")
                self.action_posconditions[action] = file.readline().strip().split(";")
                action = file.readline().strip()
            self.initial_state = file.readline().strip().split(";")
            self.final_state = file.readline().strip().split(";")

    def get_atoms(self):
        return self.atoms
    
    def get_actions(self):
        return self.actions
    
    def get_state_atoms(self):
        return [atom for atom in self.atoms if atom not in self.actions]

    def get_action_preconditions(self, action):
        return self.action_preconditions[action]
    
    def get_action_posconditions(self, action):
        return self.action_posconditions[action]
    
    def get_initial_state(self):    
        return self.initial_state
    
    def get_final_state(self):
        return self.final_state

class SatPlanInstanceMapper:
    def __init__(self):
        self.counter = 0
        self.mapping = {}  #from string to int
        self.mapping_reverse = {} #from int to string
    
    def add_literal_to_mapping(self, new_literal):
        pure_atom = new_literal.replace("~","")
        if pure_atom not in self.mapping.keys():
            self.counter += 1
            self.mapping[pure_atom] = self.counter
            self.mapping_reverse[self.counter] = pure_atom
 
    def add_list_of_literals_to_mapping(self, new_literals):
        for literal in new_literals:
            self.add_literal_to_mapping(literal)

    def get_literal_from_mapping(self, literal):
        pure_atom = literal.replace("~","")
        return -self.mapping[pure_atom] if literal[0] == "~" else self.mapping[pure_atom]

    def get_list_of_literals_from_mapping(self, list_literals):
        return [self.get_literal_from_mapping(literal) for literal in list_literals]
    
    def get_literal_from_mapping_reverse(self, mapped_int):
        return f"~" + self.mapping_reverse[-mapped_int] if mapped_int < 0 else self.mapping_reverse[mapped_int]

    def get_list_of_literals_from_mapping_reverse(self, mapped_ints):
        return [self.get_literal_from_mapping_reverse(mapped_int) for mapped_int in mapped_ints]    
