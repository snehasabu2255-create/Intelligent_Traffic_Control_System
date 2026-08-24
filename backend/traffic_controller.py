import time
import threading
from backend.ml_model import predict_green_time
from backend.vision import cameras

class TrafficController:
    def __init__(self):
        self.running = False
        self.skip_current = False
        self.state = {
            "active_camera": "South", 
            "active_phase": "Init",
            "phase_description": "Initializing...",
            "time_remaining": 0,
            "green_times": {"South": 0, "North": 0, "West": 0, "East": 0},
            "densities": {"South": "UNKNOWN", "North": "UNKNOWN", "West": "UNKNOWN", "East": "UNKNOWN"},
            "signals": {
                "South": {"red": True, "yellow": False, "green_s": False, "green_r": False, "timer": 0},
                "North": {"red": True, "yellow": False, "green_s": False, "green_r": False, "timer": 0},
                "West": {"red": True, "yellow": False, "green_s": False, "green_r": False, "timer": 0},
                "East": {"red": True, "yellow": False, "green_s": False, "green_r": False, "timer": 0},
            }
        }
        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_cycle, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def get_state(self):
        with self.lock:
            return dict(self.state)

    def _update_state(self, updates):
        with self.lock:
            self.state.update(updates)

    def _update_signal(self, road, red, yellow, green_s, green_r, timer):
        with self.lock:
            self.state["signals"][road] = {
                "red": red,
                "yellow": yellow,
                "green_s": green_s,
                "green_r": green_r,
                "timer": int(timer)
            }

    def _sleep_and_countdown(self, seconds, road_timers=None):
        """
        Sleeps for a duration while updating the countdown timer.
        road_timers: dict of road_name -> bool (whether to decrement its signal timer)
        Returns True if skipped early.
        """
        while seconds > 0 and self.running and not self.skip_current:
            with self.lock:
                self.state["time_remaining"] = int(seconds)
                if road_timers:
                    for road, should_decrement in road_timers.items():
                        if should_decrement and self.state["signals"][road]["timer"] > 0:
                            self.state["signals"][road]["timer"] -= 1

            time.sleep(1)
            seconds -= 1
            
        return self.skip_current

    def _set_all_red(self):
        for road in ["South", "North", "West", "East"]:
            self._update_signal(road, True, False, False, False, 0)

    def _execute_road(self, main_road):
        """Executes the phase sequence for a single active road."""
        main_count = cameras[main_road].get_count()
        t_main, d_main = predict_green_time(main_count)
        
        with self.lock:
            self.state["green_times"][main_road] = t_main
            self.state["densities"][main_road] = d_main
            self.state["active_camera"] = main_road

        self._set_all_red()
        self.skip_current = False

        if t_main == 0:
            self._update_state({
                "active_phase": "Skipping",
                "phase_description": f"No vehicles on {main_road}. Skipping."
            })
            return

        opp_road = "North" if main_road == "South" else ("South" if main_road == "North" else ("West" if main_road == "East" else "East"))

        # Yellow transition before Green for active road
        self._update_state({
            "active_phase": f"{main_road} Ready",
            "phase_description": f"Preparing {main_road}."
        })
        self._update_signal(main_road, False, True, False, False, 3)
        if self._sleep_and_countdown(3, {main_road: True}): return
        
        if t_main <= 45:
            self._update_state({
                "active_phase": f"{main_road} Green",
                "phase_description": f"{main_road} Right + Straight."
            })
            self._update_signal(main_road, False, False, True, True, t_main)
            if self._sleep_and_countdown(t_main, {main_road: True}): return
        else:
            self._update_state({
                "active_phase": f"{main_road} Green (All)",
                "phase_description": f"{main_road} Right + Straight."
            })
            self._update_signal(main_road, False, False, True, True, 45)
            if self._sleep_and_countdown(45, {main_road: True}): return
            
            rem = t_main - 45
            self._update_state({
                "active_phase": f"{main_road} & {opp_road} Straight",
                "phase_description": f"{main_road} & {opp_road} Straight only."
            })
            self._update_signal(main_road, False, False, True, False, rem)
            self._update_signal(opp_road, False, False, True, False, rem)
            if self._sleep_and_countdown(rem, {main_road: True, opp_road: True}): return
            
        # 3-second Yellow transition
        self._update_state({
            "active_phase": f"Yellow Transition",
            "phase_description": f"Turning Red."
        })
        self._update_signal(main_road, False, True, False, False, 3)
        if t_main > 45:
            self._update_signal(opp_road, False, True, False, False, 3)
            
        if self._sleep_and_countdown(3, {main_road: True, opp_road: True} if t_main > 45 else {main_road: True}): return
        
        self._set_all_red()
        
        # 1 second buffer all red
        self._sleep_and_countdown(1)

    def _run_cycle(self):
        cycle_sequence = ["South", "North", "East", "West"]
        while self.running:
            for road in cycle_sequence:
                if not self.running: break
                self._execute_road(road)

# Singleton instance
controller = TrafficController()
