# Copyright 2025 ropimen
#
# This file is licensed under the Server Side Public License (SSPL), Version 1.0.
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
# https://www.mongodb.com/legal/licensing/server-side-public-license
#
# This file is part of ElectricSystemClasses.
#
# ElectricSystemClasses is a Python package providing a collection of classes for simulating electric systems.

from electricsystemclasses.simulation import SimulationGlobals

def powerToTotalEnergy( power_array ):
    return sum(p*SimulationGlobals.step_size_in_h for p in power_array)

def powerToEnergy( power_array ):
    return [x*SimulationGlobals.step_size_in_h for x in power_array]

def allocate_charge_power_ev(ev_list, P_inj, P_unallocated = 0, power_dict= None):

    ev_list = list(ev_list)

    if power_dict is None:
        power_dict = {}

    for ev in ev_list[:]:
        if ev.soc_history_kwh[-1] == ev.capacity:
            power_dict[ev.id] = 0
            ev_list.remove(ev)

    if len(ev_list) == 0:
        power_dict["not allocated"] = P_inj
        return power_dict

    P_eqs = {}
    
    if P_inj > sum( [x.max_charge_power for x in ev_list] ):
        P_unallocated += P_inj - sum( [x.max_charge_power for x in ev_list] )
        P_inj = sum( [x.max_disch_power for x in ev_list] )
    
    for ev in ev_list:
        # compute time window in hours
        T_window = ev.t_depart - SimulationGlobals.current_step_time_in_h
        T_windows = {ev: ev.t_depart - SimulationGlobals.current_step_time_in_h for ev in ev_list}
        T_sum = sum(T_windows.values())
        w = {ev: 1-(T_windows[ev] / T_sum) if len(ev_list) > 1 else 1 for ev in ev_list}
        P_eq_tot = 0
        E_avail = 0

        if ev.soc_history_kwh[-1] < ev.capacity:
            E_avail = ev.capacity - ev.soc_history_kwh[-1]
            # feasible constant rate over the window
            P_eq_ev = (E_avail / T_window)*w[ev]
            P_eq_tot += P_eq_ev

            P_eqs[ev] = P_eq_ev
        else:
            P_eqs[ev] = 0

    total_p_eq = sum(P_eqs.values())

    P_min = {}
    total_p_min = 0

    for ev in ev_list:
        P_min[ev] = min( ev.max_charge_power, P_inj * P_eqs[ev]/total_p_eq if total_p_eq != 0 else 0)

    total_p_min = sum(P_min.values())
    # allocate proportionally
    for ev in ev_list:

        P_i = P_inj * (P_min[ev] / total_p_min) if total_p_min != 0 else 0

        if P_i > ev.max_charge_power:
            power_dict[ev.id] = ev.max_charge_power
            ev_list.remove(ev)
            P_inj = P_inj - ev.max_charge_power
            allocate_charge_power_ev(ev_list, P_inj, P_unallocated, power_dict)
            break
        else:
            power_dict[ev.id] = P_i

    power_dict["not allocated"] = P_unallocated

    return power_dict

def allocate_discharge_power_ev(ev_list, P_req, lim="min", P_unallocated = 0, power_dict=None):
    
    ev_list = list(ev_list)

    if power_dict is None:
        power_dict = {}

    #check if for a predefined condition i have vehicles that cannot discharge due to having socs lower than lim
    for ev in ev_list[:]:

        if lim == "min":
            if ev.soc_history_kwh[-1] <= ev.soc_min_kwh:
                ev_list.remove(ev)
                power_dict[ev.id] = 0
        
        elif lim == "lim":
            if ev.soc_history_kwh[-1] <= ev.soc_lim_kwh:
                ev_list.remove(ev)
                power_dict[ev.id] = 0
        
        else:
            if ev.soc_history_kwh[-1] <= lim:
                ev_list.remove(ev)
                power_dict[ev.id] = 0

    if len(ev_list) == 0:
        power_dict["not allocated"] = P_req
        return power_dict

    P_eqs = {}
    
    if P_req > sum( [x.max_disch_power for x in ev_list] ):
        P_unallocated += P_req - sum( [x.max_disch_power for x in ev_list] )
        P_req = sum( [x.max_disch_power for x in ev_list] )
    
    for ev in ev_list:
        # compute time window in hours
        T_window = ev.t_depart - SimulationGlobals.current_step_time_in_h
        T_windows = {ev: ev.t_depart - SimulationGlobals.current_step_time_in_h for ev in ev_list}
        T_sum = sum(T_windows.values())
        w = {ev: 1-(T_windows[ev] / T_sum) if len(ev_list) > 1 else 1 for ev in ev_list}

        P_eq_tot = 0
        E_avail = 0
        if lim == "min":
            if ev.soc_history_kwh[-1] > ev.soc_min_kwh:
                E_avail = ev.soc_history_kwh[-1] - ev.soc_min_kwh
        elif lim == "lim":
            if ev.soc_history_kwh[-1] > ev.soc_lim_kwh:
                E_avail = ev.soc_history_kwh[-1] - ev.soc_lim_kwh
        else:
            if ev.soc_history_kwh[-1] > lim:
                E_avail = ev.soc_history_kwh[-1] - lim
            # feasible constant rate over the window
        P_eq_ev = (E_avail / T_window)*w[ev]
        P_eq_tot += P_eq_ev

        P_eqs[ev] = P_eq_ev

    total_p_eq = sum(P_eqs.values())

    P_min = {}
    total_p_min = 0
    for ev in ev_list:
        P_min[ev] = min(ev.max_disch_power, P_req * P_eqs[ev]/total_p_eq if total_p_eq != 0 else 0)
   
    total_p_min = sum(P_min.values())

    # allocate proportionally
    for ev in ev_list:
        P_i = P_req * (P_min[ev] / total_p_min) if total_p_min != 0 else 0

        if P_i > ev.max_disch_power:
            power_dict[ev.id] = ev.max_disch_power
            ev_list.remove(ev)
            P_req = P_req - ev.max_disch_power
            allocate_discharge_power_ev(ev_list, P_req, lim, P_unallocated, power_dict)
            break
        else:
            power_dict[ev.id] = P_i
        
    power_dict["not allocated"] = P_unallocated

    return power_dict
