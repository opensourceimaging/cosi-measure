#rst
class chg():
    '''cyclic voltammogram object. created either from file or by a potentiostat.'''

    variableDict = {
        "voltage": [],
        "current": [],
        "datetime": '',
    }

    voltage = [] # make it a real float array!
    time = [] # make it a real float array!

    chgFile = 0 # a file where cv is stored

    def __init__(self,filename=''):

        # --- set parameters ---
        self.chg_current = 0 # what current to charge with
        self.dcg_current = 0  # what current to charge with
        self.low_voltage_level = 0
        self.high_voltage_level = 0
        self.n_cycles = 0

        # --- measure parameters ---
        self.data_pts = []
        self.time = [0]
        self.current = [0]
        self.voltage = [0]

        self.filename = 'dummy'
        self.delayBetweenPointsInSeconds = 0

        # --- from here on - import from file ---
        # if filename was given, user wants to import that cv
        if filename != '':
            self.time = []
            self.current = []
            self.voltage = []
        # populate the fields of the chg object from that csv file

            self.chgFile = open(filename)  # open the file
            self.filename = str(filename.split('/')[-1])
            chgf = self.chgFile  # for short
            datafile = chgf.readlines()
            linecounter = 0
            lineWhereDataStarts = 0

            for line in datafile:
                linecounter = linecounter+1
                if 'Date/Time' in line:
                    self.datetime = line.split(',')[1]
                    self.variableDict["datetime"] = self.datetime
                    print('Date/Time: %s'%self.datetime)
                if 'Serial Number' in line:
                    self.variableDict["serialnumber"] = int(line.split(',')[1])
                    print('Serial Number: %d'%self.variableDict["serialnumber"])
                if 'Model' in line:
                    self.variableDict["Model"] = int(line.split(',')[1])
                    print('Model: %d'%self.variableDict["Model"])
                if '# of Cycles' in line:
                        self.variableDict["# of Cycles"] = int(line.split(',')[1])
                        print('# of Cycles: %d' % self.variableDict["# of Cycles"])
                if 'nplc' in line:
                    self.variableDict["nplc"] = float(line.split(',')[1])
                    print('nplc: %f'%self.variableDict["nplc"])
                if 'Raw Data' in line:
                    lineWhereDataStarts = linecounter+4
                    print('RAW DATA BLOCK DETECTED, reading values from line %d' % lineWhereDataStarts)
                    for i in range(lineWhereDataStarts, len(datafile)):
                        if "Step" in datafile[i]:
                            continue
                        data_pt = float(datafile[i].split(',')[0])
                        self.data_pts.append(data_pt)
                        timeInSeconds = float(datafile[i].split(',')[1])
                        self.time.append(timeInSeconds)
                        currentInAmps = float(datafile[i].split(',')[2])
                        self.current.append(currentInAmps)
                        potentialInVolts = float(datafile[i].split(',')[3])
                        self.voltage.append(potentialInVolts)

    def saveAs(self,filename: str):
        # open file filename and write comma separated values in it
        # experiment parameters
        # data
        with open(filename, 'w') as file:
            file.write('EMRE Device Manager: Chronopotentiometry\n\n')

            file.write('System Parameters\n')
            file.write('Date/Time,%s\n\n\n'%self.datetime)

            file.write('Raw Data\n\nData Pt,Times (s), Current (A), Potential (V)\n')
            for i in range(len(self.voltage)):
                file.write('%d,%f,%f,%f\n'%(i,self.time[i],self.current[i],self.voltage[i]))
        file.close()


