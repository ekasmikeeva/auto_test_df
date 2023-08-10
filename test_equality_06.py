"""
Тестовый модуль, запускающий набор тестов.
Проверка эквивалентности вывода результатов корреляционного ГСС солвера: сравнение данных при заданном явном диаметре в
пайпах и нодах, и подстановке дефолтного значения параметра диаметра в нодах
"""
import shutil

import pytest
from pathlib import Path

from auto_tests.utils.jsones import json_load

from utils_equality_06 import check_parameters_equivalnce, computation_solver_params, computation_compute_all

dir_test_suite = Path(__file__).resolve().parent
input_dir = dir_test_suite / "input"
output_dir = dir_test_suite / "output"

solver_types = (
    'correlation',
    'computation',
)

geometries = (
    'simple_gsn',
    'gsn_nulu_13_minus_9',
)

fluids = (
    "bo_conv_1",
    "comp_C6",
    "composite_c_10_plus",
    "gc_blackoil_fluidWell1",
    "nt_blackoil_fluidWell1",
)


@pytest.mark.launch_incremental
@pytest.mark.parametrize("fluid", fluids)
@pytest.mark.parametrize("geometry", geometries)
@pytest.mark.parametrize("solver_type", solver_types)
class TestNodesAutoDiameter:
    """
    Запускает простую ГСС и ее аналог без явного указания диамерна в нодах.
    Сравнивает результаты. Они должны быть идентичны.
    """

    @classmethod
    def setup_class(cls):
        """
        Очистка output директории
        """
        shutil.rmtree(output_dir, ignore_errors=True)

    def test_launch(self, launch_kernel, solver_type, fluid, geometry):
        """
        Запуск симулятора.
        """
        model = json_load(input_dir / "correlation" / geometry / fluid / "pysim1.json")

        if solver_type == 'computation':
            model['solver']['solver_params'] = computation_solver_params
            model['solver']['compute_all'] = computation_compute_all

        launch_kernel(output_dir / solver_type / geometry / fluid, source_json=model)

    def test_launch_auto_diameter(self, launch_kernel, solver_type, fluid, geometry):
        """
        Запуск симулятора без параметра диаметр в нодах.
        """
        model = json_load(input_dir / "correlation" / geometry / fluid / "pysim1.json")

        for idx, element in enumerate(model['solver']['nodes']):
            model['solver']['nodes'][idx].pop('diameter')

        if solver_type == 'computation':
            model['solver']['solver_params'] = computation_solver_params
            model['solver']['compute_all'] = computation_compute_all

        launch_kernel(output_dir / solver_type / geometry / f'{fluid}_nodes_auto_diameter', source_json=model)

    def test_assert_equality(self, solver_type, fluid, geometry):
        """
        Сравнивает выходные данные тест-кейса на простой ГСС с диаметром в нодах и без параметра диаметр в нодах.
        """
        model1 = json_load(output_dir / solver_type / geometry / fluid / "correlation_pipe_line.json")
        model_auto_diameter = json_load(
            output_dir / solver_type / geometry / f'{fluid}_nodes_auto_diameter' / "correlation_pipe_line.json")
        err_msg = check_parameters_equivalnce(model1, model_auto_diameter)
        assert not err_msg, f'Errors in {len(err_msg)} occurrences\n' + '\n'.join(err_msg)
