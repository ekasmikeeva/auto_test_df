"""
Модуль для парсинга и отрисовки графиков
"""
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List

from auto_tests.utils.jsones import json_load

class Equality06Mixin:
    """
    Модуль для сравнения выходных данных в рамках одной однофазной модели и одного солвера
    с различными двухфазными моделями
    """
    calc_result_dict: dict

    def check_parameters_equivalnce(self, solver_type, fluid, geometry, one_phase_friction_model,
                                    two_phase_friction_model):
        err_msg = []

        # Возвращает тапл с первым  непустым ключом и значением словаря
        calc_result1 = None
        iter_calc_result_dict = iter(
            self.calc_result_dict[solver_type][fluid][geometry][one_phase_friction_model].items())

        while not isinstance(calc_result1, dict):
            try:
                key1, calc_result1 = next(iter_calc_result_dict)
            except StopIteration:
                break

        # если текущий кейс совпадает с первым кейсом с данными, то сравнивать его самого с собой не надо
        if key1 == two_phase_friction_model:
            return err_msg

        calc_result2 = self.calc_result_dict[solver_type][fluid][geometry][one_phase_friction_model][
            two_phase_friction_model]

        sim_results_1 = calc_result1['simulation_results'][-1]
        sim_results_2 = calc_result2['simulation_results'][-1]

        # Итерируем по нодам и проверяем эквивалентность

        for node1, node2 in zip(sim_results_1["nodes"], sim_results_2["nodes"]):
            for data_type in self.check_params_dict:
                for param in self.check_params_dict[data_type]:

                    if not sim_results_1["nodes"][node1][data_type][param] == \
                           sim_results_2["nodes"][node2][data_type][
                               param]:
                        err_msg.append(
                            f'In {solver_type}-{fluid}-{geometry}-{one_phase_friction_model}-'
                            f'{two_phase_friction_model} and {key1} '
                            f'{node1}-{data_type}-{param} are not the same '
                            f'{sim_results_1["nodes"][node1][data_type][param]} != '
                            f'{sim_results_2["nodes"][node2][data_type][param]}')

        # Итерируем по пайпам и проверяем эквивалентность
        for pipe1, pipe2 in zip(sim_results_1["pipes"], sim_results_2["pipes"]):
            for idx, (cell1, cell2) in enumerate(
                    zip(sim_results_1["pipes"][pipe1]["cells"], sim_results_2["pipes"][pipe2]["cells"])):
                for data_type in self.check_params_dict:
                    for param in self.check_params_dict[data_type]:

                        if not cell1[data_type][param] == cell2[data_type][param]:
                            err_msg.append(
                                f'In {solver_type}-{fluid}-{geometry}-{one_phase_friction_model}-'
                                f'{two_phase_friction_model} and {key1} '
                                f'{pipe1}-cells-{idx}-{data_type}-{param} '
                                f'are not the same {cell1[data_type][param]} != {cell2[data_type][param]}')

        return err_msg
