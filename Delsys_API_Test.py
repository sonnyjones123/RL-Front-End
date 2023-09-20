import sys
import time

sys.path.insert(0, "C:/Users/sonny/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/Delsys/Example-Applications-main/Python")

from AeroPy.TrignoBase import TrignoBase

base = TrignoBase()
TrigBase = base.BaseInstance

key = "MIIBKjCB4wYHKoZIzj0CATCB1wIBATAsBgcqhkjOPQEBAiEA/////wAAAAEAAAAAAAAAAAAAAAD///////////////8wWwQg/////wAAAAEAAAAAAAAAAAAAAAD///////////////wEIFrGNdiqOpPns+u9VXaYhrxlHQawzFOw9jvOPD4n0mBLAxUAxJ02CIbnBJNqZnjhE50mt4GffpAEIQNrF9Hy4SxCR/i85uVjpEDydwN9gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABCs6LASqvLpxqpvzLA8QbLmUDDDlOqD54JhLUEadv+oAgG8JVVDtI0qMO2V2PQiXoKsY33+ea/Jtp12wDA3847g="
license = "<License>  <Id>756caf49-ab7f-407f-970e-89f5933fa494</Id>  <Type>Standard</Type>  <Quantity>10</Quantity>  <LicenseAttributes>    <Attribute name='Software'></Attribute>  </LicenseAttributes>  <ProductFeatures>    <Feature name='Sales'>True</Feature>    <Feature name='Billing'>False</Feature>  </ProductFeatures>  <Customer>    <Name>Sonny Jones</Name>    <Email>sonny.jones@utah.edu</Email>  </Customer>  <Expiration>Fri, 05 Sep 2031 04:00:00 GMT</Expiration>  <Signature>MEUCIDx5YfJ4042zldgXWz+IJi//Z+ZQQ0b0LZoYIjcRm3BvAiEAjXJD2kb1fLqcFLD7/fAOoWOjRHANREyQwjDpDlaLYOg=</Signature></License>"

# print("Validating TrignoBase")

# time.sleep(1)

# TrigBase.ValidateBase(key, license)

# time.sleep(1)

# print(f"Current Status: {TrigBase.GetPipelineState()}")

# TrigBase.ScanSensors()
# TrigBase.PairSensor()

from DelsysEMG import DelsysEMG

DelsysEMG = DelsysEMG()