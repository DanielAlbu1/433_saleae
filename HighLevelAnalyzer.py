# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions
from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):
    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        '433': {
            'format': '{{data.result}}'
        }
    }
    def __init__(self):
        '''
        Initialize HLA.
        Settings can be accessed using the same name used above.
        '''
        #A byte we will be building up bit by bit.
        self.byte = []
        self.byte_start_time = None
        #This will initialize the first byte of the capture so the times can be relative to the capture frame
        self.first_frame_start = None
		
    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.
        The type and data values in `frame` will depend on the input analyzer.
        '''
        bit=99999
        if self.first_frame_start is None:
            self.first_frame_start = frame.start_time
        wave_time = int(float(frame.end_time - frame.start_time) * 800000)#修正误差
		#以采样率8MS/s 一秒采集8000 000个点 需要一个wave_time代表0.01ms  wave_time所乘系数*8000=8000
        frame_label = ""
        if 8000<wave_time<11000:
            frame_label = "START FRAME"
            
        #If nothing is happening then ignore everything and wipe it out
        elif 31000<wave_time<32000:
            frame_label = "END"
            self.byte = []
            self.byte_start_time = None
        elif wave_time< 50: #Captures the end of a repeat
            return
        else:

            
            #This must be a normal bit, build up the byte.

            if self.byte_start_time is None:
                self.byte_start_time = frame.start_time
            if 300<wave_time<400:
                bit = 1
                self.byte.append(bit)	  		  
            if 900<wave_time<1000:    
                bit = 0
                self.byte.append(bit)          
            if len(self.byte) == 8:
                byte_value = 0
                for i in self.byte:
                    byte_value = byte_value * 2 + i
                framestart = self.byte_start_time
                self.byte = []
                self.byte_start_time = None
                return AnalyzerFrame('433', framestart, frame.end_time, {
                    'result': str(hex(byte_value))
                })
            
            else:
                
                return
        
        # Return the data frame itself
        return AnalyzerFrame('433', frame.start_time, frame.end_time, {
            'result': frame_label
        })
