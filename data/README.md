# data/

This project uses **no external data set**.  All traffic demand is generated synthetically by
`src/simulator.py` from the volumes of Tables 9 and 10 of the reference paper (stored in `src/config.py`)
and a random seed (exponential arrival headways, vehicle mix 80/10/5/3/2 %).  A given (volumes, seed) pair always
produces the same arrivals, so every experiment is exactly repeatable.
