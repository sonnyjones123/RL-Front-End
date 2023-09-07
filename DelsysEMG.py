import sys
import platform

# Adding path for current computer
# Please add your computer name and path ot the Python API folder for delsys.
if (platform.node() == "Sonny_ThinkPad"):
    sys.path.insert(0, "C:/Users/sonny/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/Delsys/Example-Applications-main/Python")

from AeroPy.TrignoBase import TrignoBase

class DelsysEMG:
    """
    This is a wrapper class for the Deslsys EMG System. This is inteneded to work with
    the Delsys TrignoBase EMG system and API. You will need to install all the dependencies
    and Delsys API software from their Github. The link to the Delsys Github Repository is
    below. 

    https://github.com/delsys-inc/Example-Applications/tree/main

    This class will interface with their API and will collect and store information obtained
    from the base. This class can also be used to conenct sensors, start and stop data collection,
    etc.  

    Author: Sonny Jones & Grange Simpson

    Usage:

    1. Create an instance of this class.
        DelsysEMG = DelsysEMG()
    """
    def __init__(self):
        # Key and License are obtained from Delsys. You may want to reach out to them for 
        # a new key and license if the following no longer work. 
        self.key = "MIIBKjCB4wYHKoZIzj0CATCB1wIBATAsBgcqhkjOPQEBAiEA/////wAAAAEAAAAAAAAAAAAAAAD///////////////8wWwQg/////wAAAAEAAAAAAAAAAAAAAAD///////////////wEIFrGNdiqOpPns+u9VXaYhrxlHQawzFOw9jvOPD4n0mBLAxUAxJ02CIbnBJNqZnjhE50mt4GffpAEIQNrF9Hy4SxCR/i85uVjpEDydwN9gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABCs6LASqvLpxqpvzLA8QbLmUDDDlOqD54JhLUEadv+oAgG8JVVDtI0qMO2V2PQiXoKsY33+ea/Jtp12wDA3847g="
        self.license = "<License>  <Id>756caf49-ab7f-407f-970e-89f5933fa494</Id>  <Type>Standard</Type>  <Quantity>10</Quantity>  <LicenseAttributes>    <Attribute name='Software'></Attribute>  </LicenseAttributes>  <ProductFeatures>    <Feature name='Sales'>True</Feature>    <Feature name='Billing'>False</Feature>  </ProductFeatures>  <Customer>    <Name>Sonny Jones</Name>    <Email>sonny.jones@utah.edu</Email>  </Customer>  <Expiration>Fri, 05 Sep 2031 04:00:00 GMT</Expiration>  <Signature>MEUCIDx5YfJ4042zldgXWz+IJi//Z+ZQQ0b0LZoYIjcRm3BvAiEAjXJD2kb1fLqcFLD7/fAOoWOjRHANREyQwjDpDlaLYOg=</Signature></License>"
        
    def connect(self):
        """ 
        Initializes the connection to the Delsys EMG system.

        Usage:
            DelsysEMG.connect()
        """
        # Creating base class instance from Delsys API
        base = TrignoBase()
        self.TrigBase = base.BaseInstance

        # Validating connection to Delsys Base 
        print("Validating TrignoBase connection...")
        self.TrigBase.ValidateBase(self.key, self.license)

        try: 
            self.status = self.TrigBase.GetPipelineState()
            print("TrignoBase Connection Valid")
        except:
            print("TrignoBase Not Connected")

    def checkStatus(self):
        """
        Checks the pipline status of the Delsys EMG system.
            
        Usage:
            DelsysEMG.check_status()
        """
        # Checking the status of the Delsys EMG system
        self.status = self.TrigBase.GetPipelineState()

        # Printing Current Status
        print(f"Current Status: {self.status}")

    def currentStatus(self):
        """
        Checks current status of Delsys EMG system.
        """
        return self.status