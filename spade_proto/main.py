import time
from spade import quit_spade

from spade_proto.raport_generator import RaportGenerator

if __name__ == "__main__":
    rap_gen = RaportGenerator("raport_generator@localhost", "RADiance89")
    future = rap_gen.start(auto_register=True)
    future.result()  # Wait until the start method is finished

    # wait until user interrupts with ctrl+C
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    print("Quiting spade...")
    # quickly finish all the agents and behaviors running in process
    quit_spade()
