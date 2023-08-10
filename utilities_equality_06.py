"""
Вспомогательный модуль для сравнения данных при заданном явном диаметре в пайпах и нодах, и подстановке дефолтного
значения параметра диаметра в нодах
"""

computation_solver_params = {
    "hcs_obj_type": "SolverParameters",
    "dt_max": 0.05,
    "output_format": {
        "hcs_obj_type": "json_format"
    },
    "path_text": "correlation_pipe_line.json",
    "max_iterations": 1000,
    "error": 0.001,
    "delta_iterations": 100
}

computation_compute_all = {
    "hcs_child": "solver",
    "hcs_obj_type": "compute_all",
    "solver_params": {
        "hcs_child": "solver_params"
    }
}


def check_parameters_equivalnce(model1, model_auto_diameter):
    err_msg = []
    sim_results_1 = model1['simulation_results'][-1]
    sim_results_2 = model_auto_diameter['simulation_results'][-1]
    # создаетм словарь для сравнения данных выходных файлов по ключам-параметрам
    check_params_dict = {
        'data': ("pressure", "temperature", "velocity_oil", "velocity_gas", "velocity_water", "holdup"),

        'linear_condition': ("frac_oil", "frac_gas", "frac_water", "density_oil", "density_gas", "density_water",
                             "viscosity_oil", "viscosity_gas", "viscosity_water", "mass_flow_oil", "mass_flow_gas",
                             "mass_flow_water", "volumetric_flow_oil", "volumetric_flow_gas", "volumetric_flow_water"),
        "standard_condition": ("frac_oil", "frac_gas", "frac_water", "density_oil", "density_gas", "density_water",
                               "mass_flow_oil", "mass_flow_gas", "mass_flow_water", "volumetric_flow_oil",
                               "volumetric_flow_gas", "volumetric_flow_water"),
        'separation_data': ("condensate_gas_factor", "water_gas_factor"),
    }

    # Итерируем по нодам и проверяем эквивалентность

    for node1, node2 in zip(sim_results_1["nodes"], sim_results_2["nodes"]):
        for data_type in check_params_dict:
            for param in check_params_dict[data_type]:

                if not sim_results_1["nodes"][node1][data_type][param] == sim_results_2["nodes"][node2][data_type][
                    param]:
                    err_msg.append(
                        f'{node1}_{data_type}_{param} are not the same {sim_results_1["nodes"][node1][data_type][param]} != {sim_results_2["nodes"][node2][data_type][param]}')

    # Итерируем по пайпам и проверяем эквивалентность
    for pipe1, pipe2 in zip(sim_results_1["pipes"], sim_results_2["pipes"]):
        for idx, (cell1, cell2) in enumerate(
                zip(sim_results_1["pipes"][pipe1]["cells"], sim_results_2["pipes"][pipe2]["cells"])):
            for data_type in check_params_dict:
                for param in check_params_dict[data_type]:

                    if not cell1[data_type][param] == cell2[data_type][param]:
                        err_msg.append(
                            f'{pipe1}_cells_{idx}_{data_type}_{param} are not the same {cell1[data_type][param]} != {cell2[data_type][param]}')

    return err_msg
