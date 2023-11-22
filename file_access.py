from datetime import datetime

class DataLog:

    def __init__(self, filename='digiball.log', starting_epoch=0, ending_epoch=0):
        try:
            self._shotdata = None
            self._starting_epoch = starting_epoch
            self._ending_epoch = ending_epoch
            self._file = open(filename, mode='r')
            self._parser()
            self._file.close()


        except FileNotFoundError:
            print('File %s not found.'%filename)

    def _parser(self):
        #Load and parse data into local memory as an array of dictionaries
        self._shotdata = []
        while 1:
            line = self._file.readline()
            if not line:
                break
            elif 'epoch' not in line:
                break
            chunks = line.split(',')
            chunks_dict = {}
            for chunk in chunks:
                label, data = chunk.split(':')
                if '{' in data:
                    values = data.strip('\r').strip('\n').strip('{').strip('}').strip(' ').split(' ')
                    values = list(map(int, values))
                    chunks_dict[label] = values
                elif '.' in data:
                    value = float(data)
                    chunks_dict[label] = value
                else:
                    value = int(data)
                    chunks_dict[label] = value
            epoch = chunks_dict['epoch']
            if epoch>=self._starting_epoch:
                if self._ending_epoch==0 or epoch<=self._ending_epoch:
                    chunks_dict['time'] = (epoch - self._starting_epoch)/1000
                    self._shotdata.append(chunks_dict)

    def _get_datetime(self, epoch):
        return datetime.fromtimestamp(epoch/1000)

    def get_next_shot_data(self, time):
        for i in range(1,len(self._shotdata)):
            if self._shotdata[i]['time']>=time or i==(len(self._shotdata)-1):
                return self._shotdata[i-1]

    def get_session_blocks(self):

        #Not working, needs more intelligence.

        sessions = []
        for i in range(0,len(self._shotdata)-1):
            e1 = self._shotdata[i]['epoch']
            e2 = self._shotdata[i + 1]['epoch']
            delta = e2-e1
            if delta>300000:
                sessions.append(self._get_datetime(e1))
        return sessions

    def print_session_blocks(self):
        sessions = self.get_session_blocks()
        for i in range(0,len(sessions)):
            s1 = sessions[i]
            t1 = s1.timestamp()
            print(s1, int(t1*1000))













