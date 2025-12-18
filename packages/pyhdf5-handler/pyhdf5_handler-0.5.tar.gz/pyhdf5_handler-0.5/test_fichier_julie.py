import pyhdf5_handler
import numpy as np

#states
pyhdf5_handler.hdf5file_view("202309010300_states.hdf5")

res=pyhdf5_handler.read_hdf5file_as_dict("202309010300_states.hdf5")
res.keys()
res["202309010300"].keys()
res["202309010300"]["keys"][0].decode()
res["202309010300"]["keys"][:].astype("str")

states=res["202309010300"]["values"]

states=pyhdf5_handler.get_hdf5file_item("202309010300_states.hdf5",location="./202309010300",item="values")

search=pyhdf5_handler.search_in_hdf5file("202309010300_states.hdf5","values")
res=search[0]
res.keys()
res["path"]
res["key"]
res["datatype"]
res["value"]

#prévis ensemble:
pyhdf5_handler.hdf5file_view("20230901030000_qens.hdf5")

res=pyhdf5_handler.read_hdf5file_as_dict("20230901030000_qens.hdf5")

res.keys()
res["20230901030000"].keys()
Q=res["20230901030000"]["member0"]

Q=pyhdf5_handler.get_hdf5file_item("20230901030000_qens.hdf5",location="./20230901030000",item="member8")

search=pyhdf5_handler.search_in_hdf5file("20230901030000_qens.hdf5","member8")
res=search[0]
res.keys()
res["path"]
res["key"]
res["datatype"]
res["value"]
