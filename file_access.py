from datetime import datetime

class DataLog:

    def __init__(self, filename='digiball.log', starting_epoch=0, ending_epoch=0, data_video_delay_seconds=0):
        try:
            self._shotdata = None
            self._starting_epoch = starting_epoch
            self._ending_epoch = ending_epoch
            self._video_delay = data_video_delay_seconds
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
                    chunks_dict['time'] = (epoch - self._starting_epoch)/1000 + self._video_delay
                    self._shotdata.append(chunks_dict)

    def _get_datetime(self, epoch):
        return datetime.fromtimestamp(epoch/1000)

    def get_all_shot_data(self):
        return self._shotdata

    def set_all_shot_data(self, shotdata):
        self._shotdata = shotdata

    def get_next_shot_data(self, time):
        for i in range(1,len(self._shotdata)):
            if self._shotdata[i]['time']>=time or i==(len(self._shotdata)-1):
                current_shot = self._shotdata[i-1]
                next_shot = self._shotdata[i]
                return i-1, current_shot, next_shot

    def set_shot_data(self, index, key, value):
        self._shotdata[index][key] = value
















