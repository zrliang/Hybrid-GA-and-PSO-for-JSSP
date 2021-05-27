import re
class Job():
    def __init__(self, configure,eqp_recipe): #processTime=eqp
        self.configure = configure

        for i in self.configure.index:   #LOT_ID、OPE_NO... to object
            setattr(self, i, self.configure[i])
        self.processTime = eqp_recipe[eqp_recipe["RECIPE"] == self.configure["RECIPE"]] #一張表 #filter to recipe #Y8000
        self.canRunMachine={}
        self.generate_canrunM()
        self.arrive_time= float(self.configure["ARRIV_T"])

        self.machineID = ''  #var
        self.startTime = 0 #var
        self.endTime = 0 #var
        self.probability = []

    def generate_canrunM(self):
        allM=self.configure["CANRUN_TOOL"]

        def cut_text(text,lenth):
            textArr = re.findall('.{'+str(lenth)+'}', text)
            textArr.append(text[(len(textArr)*lenth):])
            return textArr

        cut_canrunmachine=cut_text(allM,6)[:-1] #長度6 多餘-1
        one_prob=1/len(cut_canrunmachine)
        keys=[]
        for i in range(1,len(cut_canrunmachine)+1):
            keys.append(one_prob*i)
        self.canRunMachine = dict(zip(keys, cut_canrunmachine))

        return self.canRunMachine
        
    #
    def set_probability(self, probabilities): #probabilities=[選機,排序]
        self.probability=probabilities #set prob
        m_probability = probabilities[0]
        last  = 0
        for key in self.canRunMachine.keys():
            if m_probability > last and m_probability < key:
                self.machineID = self.canRunMachine[key]
                break
            else:
                last = key   
        return self.machineID,self.probability

    def set_start_time(self, time):
        self.startTime = self.arrive_time
        if time >= self.startTime:
            self.startTime = round(time,0)
        processTime = int(self.processTime[ self.processTime["EQP_ID"] == self.machineID ]["PROCESS_TIME"]) *  int(self.configure["QTY"])/25  #!
        self.endTime = round(self.startTime + processTime,0)

    def get_end_time(self):
        return self.endTime
    
    
