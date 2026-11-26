# ALL UNITS IN PETAJOULES (PJ)

TOTAL = 730
HOUSEHOLDS = 300   #  including commercial and public services
INDUSTRY = 150+30  # including agriculture and 30PJ of data centers expected by 2030
LIGHT_TRANSPORT = 100

# HEAVY TRANSPORT. TRUCKS is assumed to be 50 PJ of diesel trucks.
TRUCKS = 50
TRUCK_TRIPS_ELEC_SHARE = 0.356 # Calculated in the ds_api.ipynb script
TRUCK_TRIPS_METH_SHARE = 0.644 # Calculated same way as electrified share

TRUCKS_ELEC_DEMAND = TRUCKS * TRUCK_TRIPS_ELEC_SHARE * 0.4 # An electric truck uses approx. 40% of the energy (electricity) of a diesel truck
TRUCKS_METH_DEMAND = TRUCKS * TRUCK_TRIPS_METH_SHARE * 1.1 # A methanol truck uses approx. 110% of the energy (methanol) of a diesel truck


SHIPPING = 50      # not including 500 PJ of international shipping under Danish flag
AVIATION = 50

AVAILABLE_BIOMASS = 150  # "Use a value of 150 PJ for the available biomass (and sustainable trash) in DK"