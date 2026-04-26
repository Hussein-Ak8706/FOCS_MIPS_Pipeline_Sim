from parse import parseAll



class pipelined4StageFwd:
    
    def __init__(self, regAvail, instr_arr):
        
        self.cycle = 1
        self.pipelineStages = {
            "IF":None,
            "ID":None,
            "EX":None,
            "MEM/WB":None,
        }
        self.instr_arr = instr_arr
        self.regAvail = regAvail
        self.schedule = [{} for _ in range(len(instr_arr))] 
        self.raw = [[] for _ in range(len(instr_arr))]
        self.fwd = []
        # Gets the index of an instr in the order they came in for a provided instr
    def get_idx(self, instr): 
        for i in range(len(self.instr_arr)):
            if self.instr_arr[i] == instr:
                return i
            
    # Updates the available register dict after a speific instruction executes
    def finishInstr(self, instr): 
        if instr['dst'] is not None:
            self.regAvail[instr['dst']] = -1

    def print_schedule(self):
        # Get total cycles
        max_cycle = 0
        for instr in self.schedule:
            if instr:
                max_cycle = max(max_cycle, max(instr.keys()))

        # Header row
        print("Cycle ", end="")
        for c in range(1, max_cycle + 1):
            print(f"{c:^6}", end="")
        print()

        # Rows for each instruction
        for i, instr in enumerate(self.schedule):
            print(f"I{i+1}    ", end="")
            for c in range(1, max_cycle + 1):
                stage = instr.get(c, "")
                print(f"{stage:^6}", end="")
            print()

    def checkStall(self, instr):
        srcs = instr["src"]
        for i in srcs:
            if self.regAvail[i] > self.cycle:
                return True
        return False
    
    
    def createShedule(self):
        
        # Keeps track of which instr to fetch
        instrIndex = 0 

        # Keeps track of cycle
        self.cycle = 1 
        while True:

            # Makes sure a valid next instr is fetched if present
            if instrIndex < len(self.instr_arr): 
                IFInstr = self.instr_arr[instrIndex]
                
            else:
                IFInstr = None

            if self.pipelineStages["ID"] is not None and self.checkStall(self.pipelineStages["ID"]):
                

                # Forwarding the pipeline every cycle
                
                self.pipelineStages["MEM/WB"] = self.pipelineStages["EX"]
                self.pipelineStages["EX"] = None
                # self.pipelineStages["IF"] = IFInstr

                for stage, instr in self.pipelineStages.items(): # Updates Schedule array
                    if instr != None:
                        in_ind = self.get_idx(instr) # Gets the index of a given instr 
                        if stage == "ID" or stage == "IF":
                            self.schedule[in_ind][self.cycle] = "STALL"
                        else:
                            self.schedule[in_ind][self.cycle] = stage # Adds the current situation to that instr's dict
                
            else:
                

                # Forwarding the pipeline every cycle
                self.pipelineStages["MEM/WB"] = self.pipelineStages["EX"]
                self.pipelineStages["EX"] = self.pipelineStages["ID"]
                self.pipelineStages["ID"] = self.pipelineStages["IF"]
                self.pipelineStages["IF"] = IFInstr
                
                for stage, instr in self.pipelineStages.items(): # Updates Schedule array
                    if instr != None:
                        in_ind = self.get_idx(instr) # Gets the index of a given instr 
                        self.schedule[in_ind][self.cycle] = stage # Adds the current situation to that instr's dict
                instrIndex += 1

                if self.pipelineStages["EX"] is not None:
                    if self.pipelineStages["EX"]["op"] == "LW":
                        self.regAvail[self.pipelineStages["EX"]["dst"]] = max(self.cycle + 2, self.regAvail[self.pipelineStages["EX"]["dst"]])
                    else:
                        self.regAvail[self.pipelineStages["EX"]["dst"]] = max(self.cycle + 1, self.regAvail[self.pipelineStages["EX"]["dst"]])
            
                curr_ex = self.pipelineStages.get("EX")
                if curr_ex is not None:
                    ex_idx = self.get_idx(curr_ex)
                    for src_reg in curr_ex.get("src", []):
                        p_mem = self.pipelineStages.get("MEM/WB")
                        if p_mem and p_mem.get("dst") == src_reg:
                            self.fwd.append([(self.get_idx(p_mem), self.cycle-1), (ex_idx, self.cycle)])
                            continue 

            # Debugging
            print(IFInstr)
            print(self.cycle)
            print(self.schedule)
            print(self.regAvail)
            print(self.pipelineStages)
            print(self.fwd)
            
            
            # Makes sure the available reg gets updated once an instruction finishes
            # if pipelineStages["WB"] is not None: 
            #     finishInstr(pipelineStages["WB"])
            # Update Counters
            
            self.cycle += 1
                
            # Breaks only all pipeline stages are empty
            if instrIndex >= len(self.instr_arr) and all(stage is None for stage in self.pipelineStages.values()):
                break

        self.get_raws()
    
    def get_raws(self):
        n = 4
        for index, i in enumerate(self.instr_arr[:-1]):
            dest = i['dst']
            end = index + n + 1 if index+n < len(self.instr_arr) else index - (index-len(self.instr_arr)) + 1
            for indexj, j in enumerate(self.instr_arr[index+1: end]):
                if dest in j['src']:
                    self.raw[indexj+index+1].append(index)


class pipelined5StageFwd:
    
    def __init__(self, regAvail, instr_arr):
        
        self.cycle = 1
        self.pipelineStages = {
            "IF":None,
            "ID":None,
            "EX":None,
            "MEM":None,
            "WB":None
        }
        self.instr_arr = instr_arr
        self.regAvail = regAvail
        self.schedule = [{} for _ in range(len(instr_arr))] 
        self.raw = [[] for _ in range(len(instr_arr))]
        self.fwd = []
    
    # Gets the index of an instr in the order they came in for a provided instr
    def get_idx(self, instr): 
        for i in range(len(self.instr_arr)):
            if self.instr_arr[i] == instr:
                return i
            
    # Updates the available register dict after a speific instruction executes
    def finishInstr(self, instr): 
        if instr['dst'] is not None:
            self.regAvail[instr['dst']] = -1

    def print_schedule(self):
        # Get total cycles
        max_cycle = 0
        for instr in self.schedule:
            if instr:
                max_cycle = max(max_cycle, max(instr.keys()))

        # Header row
        print("Cycle ", end="")
        for c in range(1, max_cycle + 1):
            print(f"{c:^6}", end="")
        print()

        # Rows for each instruction
        for i, instr in enumerate(self.schedule):
            print(f"I{i+1}    ", end="")
            for c in range(1, max_cycle + 1):
                stage = instr.get(c, "")
                print(f"{stage:^6}", end="")
            print()

    def checkStall(self, instr):
        srcs = instr["src"]
        for i in srcs:
            if self.regAvail[i] > self.cycle:
                return True
        return False
    
    
    def createShedule(self):
        
        # Keeps track of which instr to fetch
        instrIndex = 0 

        # Keeps track of cycle
        self.cycle = 1 
        while True:

            # Makes sure a valid next instr is fetched if present
            if instrIndex < len(self.instr_arr): 
                IFInstr = self.instr_arr[instrIndex]
                
            else:
                IFInstr = None

            if self.pipelineStages["ID"] is not None and self.checkStall(self.pipelineStages["ID"]):
                

                # Forwarding the pipeline every cycle
                self.pipelineStages["WB"] = self.pipelineStages["MEM"]
                self.pipelineStages["MEM"] = self.pipelineStages["EX"]
                self.pipelineStages["EX"] = None
                # self.pipelineStages["IF"] = IFInstr

                for stage, instr in self.pipelineStages.items(): # Updates Schedule array
                    if instr != None:
                        in_ind = self.get_idx(instr) # Gets the index of a given instr 
                        if stage == "ID" or stage == "IF":
                            self.schedule[in_ind][self.cycle] = "STALL"
                        else:
                            self.schedule[in_ind][self.cycle] = stage # Adds the current situation to that instr's dict
                
            else:
                

                # Forwarding the pipeline every cycle
                self.pipelineStages["WB"] = self.pipelineStages["MEM"]
                self.pipelineStages["MEM"] = self.pipelineStages["EX"]
                self.pipelineStages["EX"] = self.pipelineStages["ID"]
                self.pipelineStages["ID"] = self.pipelineStages["IF"]
                self.pipelineStages["IF"] = IFInstr
                
                for stage, instr in self.pipelineStages.items(): # Updates Schedule array
                    if instr != None:
                        in_ind = self.get_idx(instr) # Gets the index of a given instr 
                        self.schedule[in_ind][self.cycle] = stage # Adds the current situation to that instr's dict
                instrIndex += 1

                if self.pipelineStages["EX"] is not None:
                    if self.pipelineStages["EX"]["op"] == "LW":
                        self.regAvail[self.pipelineStages["EX"]["dst"]] = max(self.cycle + 2, self.regAvail[self.pipelineStages["EX"]["dst"]])
                    else:
                        self.regAvail[self.pipelineStages["EX"]["dst"]] = max(self.cycle + 1, self.regAvail[self.pipelineStages["EX"]["dst"]])

                curr_ex = self.pipelineStages.get("EX")
                if curr_ex is not None:
                    ex_idx = self.get_idx(curr_ex)
                    for src_reg in curr_ex.get("src", []):
                        p_mem = self.pipelineStages.get("MEM")
                        if p_mem and p_mem.get("dst") == src_reg:
                            self.fwd.append([(self.get_idx(p_mem), self.cycle-1), (ex_idx, self.cycle)])
                            continue 
                        
                        p_wb = self.pipelineStages.get("WB")
                        if p_wb and p_wb.get("dst") == src_reg:
                            self.fwd.append([(self.get_idx(p_wb), self.cycle-1), (ex_idx, self.cycle)])

            
            # Debugging
            print(IFInstr)
            print(self.cycle)
            print(self.schedule)
            print(self.regAvail)
            print(self.pipelineStages)
            print(self.fwd)
            
            self.cycle += 1
            
            # Breaks only all pipeline stages are empty
            if instrIndex >= len(self.instr_arr) and all(stage is None for stage in self.pipelineStages.values()):
                break

        self.get_raws()

    def get_raws(self):
        n = 5
        for index, i in enumerate(self.instr_arr[:-1]):
            dest = i['dst']
            end = index + n + 1 if index+n < len(self.instr_arr) else index - (index-len(self.instr_arr)) + 1
            for indexj, j in enumerate(self.instr_arr[index+1: end]):
                if dest in j['src']:
                    self.raw[indexj+index+1].append(index)

class pipelined4StageStall:
    
    def __init__(self, regAvail, instr_arr):
        
        self.cycle = 1
        self.pipelineStages = {
            "IF":None,
            "ID":None,
            "EX":None,
            "MEM/WB":None
        }
        self.instr_arr = instr_arr
        self.regAvail = regAvail
        self.schedule = [{} for _ in range(len(instr_arr))] 
        self.raw = [[] for _ in range(len(instr_arr))]
        # Gets the index of an instr in the order they came in for a provided instr
    def get_idx(self, instr): 
        for i in range(len(self.instr_arr)):
            if self.instr_arr[i] == instr:
                return i
            
    # Updates the available register dict after a speific instruction executes
    def finishInstr(self, instr): 
        if instr['dst'] is not None:
            self.regAvail[instr['dst']] = -1

    def print_schedule(self):
        # Get total cycles
        max_cycle = 0
        for instr in self.schedule:
            if instr:
                max_cycle = max(max_cycle, max(instr.keys()))

        # Header row
        print("Cycle ", end="")
        for c in range(1, max_cycle + 1):
            print(f"{c:^6}", end="")
        print()

        # Rows for each instruction
        for i, instr in enumerate(self.schedule):
            print(f"I{i+1}    ", end="")
            for c in range(1, max_cycle + 1):
                stage = instr.get(c, "")
                print(f"{stage:^6}", end="")
            print()

    def checkStall(self, instr):
        srcs = instr["src"]
        for i in srcs:
            if self.regAvail[i] > self.cycle:
                return True
        return False
    
    
    def createShedule(self):
        
        # Keeps track of which instr to fetch
        instrIndex = 0 

        # Keeps track of cycle
        self.cycle = 1 
        while True:

            # Makes sure a valid next instr is fetched if present
            if instrIndex < len(self.instr_arr): 
                IFInstr = self.instr_arr[instrIndex]
                
            else:
                IFInstr = None

            if self.pipelineStages["IF"] is not None and self.checkStall(self.pipelineStages["IF"]):
                

                # Forwarding the pipeline every cycle
                self.pipelineStages["MEM/WB"] = self.pipelineStages["EX"]
                self.pipelineStages["EX"] = self.pipelineStages["ID"]
                self.pipelineStages["ID"] = None # Set to None to make sure that pipelinestage is empty

                for stage, instr in self.pipelineStages.items(): # Updates Schedule array
                    if instr != None:
                        in_ind = self.get_idx(instr) # Gets the index of a given instr 
                        if stage == "IF":
                            self.schedule[in_ind][self.cycle] = "STALL"
                        else:
                            self.schedule[in_ind][self.cycle] = stage # Adds the current situation to that instr's dict
                
            else:
                

                # Forwarding the pipeline every cycle
                self.pipelineStages["MEM/WB"] = self.pipelineStages["EX"]
                self.pipelineStages["EX"] = self.pipelineStages["ID"]
                self.pipelineStages["ID"] = self.pipelineStages["IF"]
                self.pipelineStages["IF"] = IFInstr
                
                for stage, instr in self.pipelineStages.items(): # Updates Schedule array
                    if instr != None:
                        in_ind = self.get_idx(instr) # Gets the index of a given instr 
                        self.schedule[in_ind][self.cycle] = stage # Adds the current situation to that instr's dict
                instrIndex += 1

                if self.pipelineStages["ID"] is not None:
                    self.regAvail[self.pipelineStages["ID"]["dst"]] = self.cycle + len(self.pipelineStages) - 1

            # Debugging
            print(IFInstr)
            print(self.cycle)
            print(self.schedule)
            print(self.regAvail)
            print(self.pipelineStages)
            
            # Makes sure the available reg gets updated once an instruction finishes
            # if pipelineStages["WB"] is not None: 
            #     finishInstr(pipelineStages["WB"])
            # Update Counters
            
            self.cycle += 1
                
            # Breaks only all pipeline stages are empty
            if instrIndex >= len(self.instr_arr) and all(stage is None for stage in self.pipelineStages.values()):
                break
        
        self.get_raws()

    def get_raws(self):
        n = 4
        for index, i in enumerate(self.instr_arr[:-1]):
            dest = i['dst']
            end = index + n + 1 if index+n < len(self.instr_arr) else index - (index-len(self.instr_arr)) + 1
            for indexj, j in enumerate(self.instr_arr[index+1: end]):
                if dest in j['src']:
                    self.raw[indexj+index+1].append(index)           



class pipelined5StageStall:
    
    def __init__(self, regAvail, instr_arr):
        
        self.cycle = 1
        self.pipelineStages = {
            "IF":None,
            "ID":None,
            "EX":None,
            "MEM":None,
            "WB":None
        }
        self.instr_arr = instr_arr
        self.regAvail = regAvail
        self.schedule = [{} for _ in range(len(instr_arr))] 
        self.raw = [[] for _ in range(len(instr_arr))]
        # Gets the index of an instr in the order they came in for a provided instr
    def get_idx(self, instr): 
        for i in range(len(self.instr_arr)):
            if self.instr_arr[i] == instr:
                return i
            
    # Updates the available register dict after a speific instruction executes
    def finishInstr(self, instr): 
        if instr['dst'] is not None:
            self.regAvail[instr['dst']] = -1

    def print_schedule(self):
        # Get total cycles
        max_cycle = 0
        for instr in self.schedule:
            if instr:
                max_cycle = max(max_cycle, max(instr.keys()))

        # Header row
        print("Cycle ", end="")
        for c in range(1, max_cycle + 1):
            print(f"{c:^6}", end="")
        print()

        # Rows for each instruction
        for i, instr in enumerate(self.schedule):
            print(f"I{i+1}    ", end="")
            for c in range(1, max_cycle + 1):
                stage = instr.get(c, "")
                print(f"{stage:^6}", end="")
            print()

    def checkStall(self, instr):
        srcs = instr["src"]
        for i in srcs:
            if self.regAvail[i] > self.cycle:
                return True
        return False
    
    
    def createShedule(self):
        
        # Keeps track of which instr to fetch
        instrIndex = 0 

        # Keeps track of cycle
        self.cycle = 1 
        while True:

            # Makes sure a valid next instr is fetched if present
            if instrIndex < len(self.instr_arr): 
                IFInstr = self.instr_arr[instrIndex]
                
            else:
                IFInstr = None

            if self.pipelineStages["IF"] is not None and self.checkStall(self.pipelineStages["IF"]):
                

                # Forwarding the pipeline every cycle
                self.pipelineStages["WB"] = self.pipelineStages["MEM"]
                self.pipelineStages["MEM"] = self.pipelineStages["EX"]
                self.pipelineStages["EX"] = self.pipelineStages["ID"]
                self.pipelineStages["ID"] = None # Set to None to make sure that pipelinestage is empty

                for stage, instr in self.pipelineStages.items(): # Updates Schedule array
                    if instr != None:
                        in_ind = self.get_idx(instr) # Gets the index of a given instr 
                        if stage == "IF":
                            self.schedule[in_ind][self.cycle] = "STALL"
                        else:
                            self.schedule[in_ind][self.cycle] = stage # Adds the current situation to that instr's dict
                
            else:
                

                # Forwarding the pipeline every cycle
                self.pipelineStages["WB"] = self.pipelineStages["MEM"]
                self.pipelineStages["MEM"] = self.pipelineStages["EX"]
                self.pipelineStages["EX"] = self.pipelineStages["ID"]
                self.pipelineStages["ID"] = self.pipelineStages["IF"]
                self.pipelineStages["IF"] = IFInstr
                
                for stage, instr in self.pipelineStages.items(): # Updates Schedule array
                    if instr != None:
                        in_ind = self.get_idx(instr) # Gets the index of a given instr 
                        self.schedule[in_ind][self.cycle] = stage # Adds the current situation to that instr's dict
                instrIndex += 1

                if self.pipelineStages["ID"] is not None:
                    self.regAvail[self.pipelineStages["ID"]["dst"]] = self.cycle + len(self.pipelineStages) - 1

            # Debugging
            print(IFInstr)
            print(self.cycle)
            print(self.schedule)
            print(self.regAvail)
            print(self.pipelineStages)
            
            # Makes sure the available reg gets updated once an instruction finishes
            # if pipelineStages["WB"] is not None: 
            #     finishInstr(pipelineStages["WB"])
            # Update Counters
            
            self.cycle += 1
                
            # Breaks only all pipeline stages are empty
            if instrIndex >= len(self.instr_arr) and all(stage is None for stage in self.pipelineStages.values()):
                break
        self.get_raws()

    def get_raws(self):
        n = 5
        for index, i in enumerate(self.instr_arr[:-1]):
            dest = i['dst']
            end = index + n + 1 if index+n < len(self.instr_arr) else index - (index-len(self.instr_arr)) + 1
            for indexj, j in enumerate(self.instr_arr[index+1: end]):
                if dest in j['src']:
                    self.raw[indexj+index+1].append(index)

