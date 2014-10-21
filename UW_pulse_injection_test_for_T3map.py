###############################################################################
# GPIB Class and Initializations

import visa
from struct import pack
import time


class GpibInst(visa.GpibInstrument):
	__GPIB_ADDRESS__ = 19
	__AMP__ = 0.2
	__OFFSET__ = __AMP__
	__BURST_COUNT__ = 255
	__DATA__ = [0, 0, 100, 0, 101, -2047, 200, 0]

	def __init__(self,reset=True):
		visa.GpibInstrument.__init__(self, self.__GPIB_ADDRESS__, timeout=30)
	

	# pass in an array of vectors (x-value, then y-value)
	def init_pulse(self):
		self.write("*CLS") # clears registers
		self.write("*SRE 16") # enables "message available bit"

		self.write("AMPL " + str(self.__AMP__) + "VP") # sets amplitude
		self.write("OFFS %f" % self.__AMP__) # sets offset

		data = self.__DATA__ # sets data to default

		self.write("LDWF? 1,%i" % (len(data) / 2)) # tells machine that 'len(data) / 2' vector vertices will be sent

		if self.read() != "1": # quit if there's an error loading the waveform
			print "Error loading waveform"
			quit()
		else :
			print "Success loading waveform"

		sum = 0 # initializes checksum
		input = pack('h', data[0]) # input is the string of vertices after being packed
		for count in range(1, len(data)):
			sum += data[count]
			input += pack('h', data[count])
		# adds packed checksum to end of data string
		input += pack('h', sum)
		# loads data string to machine
		self.write(input)

		self.write("FUNC5\n") # sets to arbitrary waveform to produce output
		self.write("BCNT %i" % self.__BURST_COUNT__) # sets burst count
		self.write("TRSC 0") # sets trigger source to single (triggers as many as burst count)
		self.write("MTYP 5") # sets the type of modulation to burst modulation
		self.write("MENA 1") # enables modulation
		self.write("TRG*") # triggers burst

generator = GpibInst() # makes a GPIB object through visa (connects with DS345)
generator.init_pulse() # runs code to generate a pulse
