import sys
from ansys_corba import CORBA
import Example

orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
ior = sys.argv[1]
obj = orb.string_to_object(ior)
eo = obj._narrow(Example.Echo)

if eo is None:
  print("Can't narrow reference.")
  sys.exit(1)