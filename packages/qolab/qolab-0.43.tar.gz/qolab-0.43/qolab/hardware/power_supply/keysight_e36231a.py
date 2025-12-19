from qolab.hardware.basic import BasicInstrument
from ._basic import PowerSupplySCPI


class KeysightE36231A(PowerSupplySCPI):
    """Keysight E36231A power supply"""

    def __init__(self, resource, *args, **kwds):
        super().__init__(resource, *args, **kwds)
        self.resource.read_termination = "\n"
        self.config["Device model"] = "Keysight E36231A"
        self.numberOfChannels = 1
        self.deviceProperties.update({"OpMode"})
        self.channelProperties = {
            "IsOn",
            "Regulation",
            "Vout",
            "Vlimit",
            "Iout",
            "Ilimit",
            "dV",
            "dI",
        }

    def setOpMode(self, val):
        """Sets power supply operation mode, returns OFF|PAR|SER.

        OFF stands for independent channels.
        """
        ALLOWED_CMD = ['OFF', 'PAR', 'SER']
        try:
            if val in ALLOWED_CMD:
                cmnd = f"OUTP:PAIR {val}"
                self.write(cmnd)
            else:
                print(f"[WARNING] Command PSU operation mode {val} is not allowed")
        except pyvisa.errors.VisaIOError as e:
                print(f"[ERROR] GPIB communication error: {e}")

    def setChanOn(self, chNum=1):
        """Power up channel output"""
        self.write(f"OUTP ON,(@{chNum})")

    def setChanOff(self, chNum=1):
        """Power down channel output"""
        self.write(f"OUTP OFF,(@{chNum})")

    @BasicInstrument.tsdb_append
    def getChanIsOn(self, chNum=1):
        """Queries channel output state"""
        qstr = f"OUTP? (@{chNum})"
        rstr = self.query(qstr)
        return bool(float(rstr))

    @BasicInstrument.tsdb_append
    def getChanRegulation(self, chNum=1):
        """Queries channel output regulation

        0 - The output is off and unregulated
        1 - The output is CC (constant current) operating mode
        2 - The output is CV (constant voltage) operating mode
        3 - The output has hardware failure
        """
        qstr = f"STAT:QUES:INST:ISUM{chNum}:COND?"
        rstr = self.query(qstr)
        return int(rstr)

    @BasicInstrument.tsdb_append
    def getChanVout(self, chNum=1):
        qstr = f"MEAS:VOLT? (@{chNum})"
        rstr = self.query(qstr)
        return float(rstr)

    @BasicInstrument.tsdb_append
    def getChanVlimit(self, chNum=1):
        qstr = f"SOUR:VOLT? (@{chNum})"
        rstr = self.query(qstr)
        return float(rstr)

    @BasicInstrument.tsdb_append
    def getChanIout(self, chNum=1):
        qstr = f"MEAS:CURR? (@{chNum})"
        rstr = self.query(qstr)
        return float(rstr)

    def get_out_current(self):
        '''
        Wrapper for `getChanIout()` to comply with PSW25045 
        source's method `get_out_current`.
        '''
        return self.getChanIout()
    
    def get_out_voltage(self):
        '''
        Wrapper for `getChanVout()` to comply with PSW25045 
        source's method `get_out_voltage`.
        '''
        return self.getChanVout()

if __name__ == "__main__":
    import pyvisa

    print("testing")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    instr = rm.open_resource("USB0::0x2A8D::0x2F02::MY61003701::INSTR")
    ps = KeysightE36231A(instr)
    print("------ Header start -------------")
    print(str.join("\n", ps.getHeader()))
    print("------ Header ends  -------------")