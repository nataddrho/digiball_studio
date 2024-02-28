from datetime import datetime


class DataLog:

    def __init__(self, filename='digiball.log'):
        try:
            self._shotdata = None
            self._file = open(filename, mode='r')
            self._parser()
            self._file.close()
            self._starting_epoch = 0

        except FileNotFoundError:
            print('File %s not found.'%filename)

    def _parser(self):
        #Load and parse data into local memory as an array of dictionaries
        self._shotdata = []
        self._tags = []
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
                elif label=='tag':
                    chunks_dict[label] = data.strip('\r').strip('\n').strip(' ')
                elif label=='tagend':
                    pass
                else:
                    value = int(data)
                    chunks_dict[label] = value
            epoch = chunks_dict['epoch']
            chunks_dict['time'] = epoch / 1000
            if 'tag' in chunks_dict or 'tagend' in chunks_dict:
                tag_dict = {}
                tag_dict['epoch'] = chunks_dict['epoch']
                tag_dict['tag'] = chunks_dict['tag']
                self._tags.append(tag_dict)
            else:
                self._shotdata.append(chunks_dict)




    def _get_datetime(self, epoch):
        return datetime.fromtimestamp(epoch/1000)

    def align_to_starting_epoch(self, epoch):
        self._starting_epoch = epoch
        for shot in self._shotdata:
            if 'time' in shot:
                shot['time'] = (shot['epoch']-epoch)/1000

    def get_starting_epoch(self):
        return self._starting_epoch

    def get_all_shot_data(self):
        return self._shotdata

    def get_all_tags(self):
        return self._tags

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
        
    def get_shot_data(self, index, key):
        try:
            return self._shotdata[index][key]
        except:
            return None
















