#rst
class cv():
    '''cyclic voltammogram object. created either from file or by a potentiostat.'''

    variableDict = {
        "voltage": [],
        "current": [],
        "datetime": '',
    }

    voltage = [] # make it a real float array
    current = [] # make it a real float array
    scan_rate = 0 # millivolts per second

    cvFile = 0 # a file where cv is stored

    def __init__(self,filename=''):

        # --- set parameters ---
        self.low_voltage_point = 0
        self.high_voltage_point = 0
        self.n_cycles = 0

        # --- measure parameters ---
        self.voltage = []
        self.current = []
        self.time = []
        self.filename = 'dummy'

        self.delayBetweenPointsInSeconds = 0

        # --- from here on - import from file ---
        # if filename was given, user wants to import that cv
        if filename != '':
        # populate the fields of the cv object from that csv file
            print('CV module: opening %s'%filename)
            self.cvFile = open(filename)  # open the file
            self.filename = str(filename.split('/')[-1])
            cvf = self.cvFile  # for short
            datafile = cvf.readlines()
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
                if 'Vertex 1' in line:
                    self.variableDict["Vertex 1"] = float(line.split(',')[1])
                    print('Vertex 1: %d' % self.variableDict["Vertex 1"])
                if 'Vertex 2' in line:
                    self.variableDict["Vertex 2"] = float(line.split(',')[1])
                    print('Vertex 2: %d' % self.variableDict["Vertex 2"])
                if 'Vertex 3' in line:
                    self.variableDict["Vertex 3"] = float(line.split(',')[1])
                    print('Vertex 3: %d' % self.variableDict["Vertex 3"])
                if '# of Cycles' in line:
                        self.variableDict["# of Cycles"] = int(line.split(',')[1])
                        print('# of Cycles: %d' % self.variableDict["# of Cycles"])
                if 'Source Rate' in line:
                    self.variableDict["Source Rate"] = float(line.split(',')[1])
                    print('Source Rate: %f'%self.variableDict["Source Rate"])
                if 'nplc' in line:
                    self.variableDict["nplc"] = float(line.split(',')[1])
                    print('nplc: %f'%self.variableDict["nplc"])
                if 'Raw Data' in line:
                    lineWhereDataStarts = linecounter+3
                    print('RAW DATA BLOCK DETECTED, reading values from line %d' % lineWhereDataStarts)
                    for i in range(lineWhereDataStarts, len(datafile)):
                        voltageInVolts = float(datafile[i].split(',')[0])
                        self.voltage.append(voltageInVolts)
                        currentInAmps = float(datafile[i].split(',')[1])
                        self.current.append(currentInAmps)
                        timeInSeconds = float(datafile[i].split(',')[2])
                        self.time.append(timeInSeconds)

    def saveAs(self,filename: str):
        # open file filename and write comma separated values in it
        # experiment parameters
        # data
        with open(filename, 'w') as file:
            file.write('EMRE Device Manager: Cyclic Voltammetry\n\n')

            file.write('System Parameters\n')
            file.write('Date/Time,%s\n\n\n'%self.datetime)

            file.write('Source Parameters\n')
            file.write('Vertex 1,%f\n' % self.low_voltage_point)
            file.write('Vertex 2,%f\n' % self.high_voltage_point)
            file.write('# of Cycles,%d\n' % self.n_cycles)

            file.write('Raw Data\nVoltage,Current,Seconds\n\n')
            for i in range(len(self.voltage)):
                file.write('%f,%f,%f\n'%(self.voltage[i],self.current[i],self.time[i]))
        file.close()


