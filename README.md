# V2V project

Repository for designing a single transceiver with a software defined radio (SDR) that handles radar, LiDAR, GPS, and V2V communications.

We are using Adalm-Pluto SDR. 

Google docs [link](https://docs.google.com/document/d/1pcrVIo0RQJuGwDCi-xMBNvkVarRPVy1aNbBDQT-anN0/edit?pli=1&tab=t.0#heading=h.rqtnr59anzwo)

## Links & goals
For simulating github repos:
- [gps](https://github.com/osqzss/gps-sdr-sim) 
- [radar](https://github.com/kit-cel/gr-radar) 
- [can](https://github.com/hardbyte/python-can) 
- [lidar](https://github.com/szenergy/awesome-lidar) 

ETSI C-ITS protocol suite 
- [vanetza](https://github.com/riebl/vanetza)  
- [gr-ieee802-11](https://github.com/bastibl/gr-ieee802-11 )


Project direction:
	Gather data from radar, LiDAR, GPS and CAN from the car. 
	Create a mock based on data format. 
	Design transceiver SDR that receives the signals correctly & efficiently. 

	Later plug in the car’s real information.


```
v2v_sdr_project/
│
├── simulation/                         # Simulated sensor data generators
│   ├── radar/                          # Radar simulation using gr-radar
│   │   └── gr-radar-flowgraphs/       # GNURadio .grc or Python files
│   ├── gps/                            # GPS I/Q generator (gps-sdr-sim)
│   │   ├── eph/                        # Ephemeris data
│   │   └── scripts/                    # Run scripts for I/Q stream
│   ├── lidar/                          # LiDAR point cloud generator
│   │   ├── datasets/                   # CSV, PCD or KITTI-formatted mock data
│   │   └── scripts/                    # Mock publishers / parsers
│   └── can/                            # CAN bus simulation
│       ├── vcan_setup.sh               # Script to setup virtual CAN
│       └── simulator.py                # python-can mock CAN messages
│
├── transceiver/                        # SDR logic
│   ├── plutosdr/                       # PlutoSDR-specific code
│   │   ├── radar_tx_rx.py              # Example: radar TX/RX with SDR
│   │   ├── gps_tx.py                   # GPS spoof / broadcast
│   │   └── v2v_tx_rx.py                # IEEE 802.11p PHY communication
│   └── flowgraphs/                     # GNU Radio .grc or .py files
│
├── v2x_stack/                          # ETSI ITS protocol layers
│   ├── vanetza/                        # VANETza: BSM, CAM, DENM stack
│   ├── gr-ieee802-11/                  # IEEE 802.11p PHY layer
│   └── openv2x_interface/              # Hooks between PHY and stack
│
├── integration/                        # Sensor fusion & messaging logic
│   ├── message_builder/               # Format CAN+Radar+LiDAR+GPS into ITS msgs
│   │   └── builder.py
│   ├── message_router/                # Route messages between modules
│   └── mock_car_interface/            # Placeholder for vehicle data I/O
│
├── data/                               # Logging & captured sensor data
│   ├── logs/                          # Saved logs for replay/debugging
│   └── captures/                      # Raw IQ or point cloud capture
│
├── matlab/                             # Optional MATLAB integration
│   ├── radar_processing/              # Signal processing blocks
│   └── validation/                    # Scripts for result validation
│
├── docker/                             # Docker build setup
│   └── Dockerfile                     # Simulation environment container
│
├── README.md
└── setup.sh                            # Master install/setup script
```