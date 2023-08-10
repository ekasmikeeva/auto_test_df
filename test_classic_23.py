"""
Тестовый модуль, запускающий набор тестов.
Проверяет скорости с разными моделями трения.
"""
import pytest
import shutil
from pathlib import Path

from auto_tests.utils.jsones import json_load

# Директория тест-сьюта
dir_test_suite = Path(__file__).resolve().parent
output_dir = dir_test_suite / "output"

# Параметризация.
# все возможные модели трения
two_phase_friction_models = (
    "Model1",
    "Model2",
    "Model3",
    "Model4"
)

one_phase_friction_models = (
    "OnePhaseModel1",
    "OnePhaseModel2",
    "OnePhaseModel3"
)

# флюиды
fluid_models = (
    "water",
    "methane",
)

# геометрии
geometries = (
    "vertical3km",
)

# Солверы. Если нужны только корреляционные, то производить запуск pytest с параметром `-m correlation`
# корреляционные солверы
test_cases_correlations = (
    pytest.param('CorrelationPipeLineSolver', marks=pytest.mark.correlation),
    pytest.param('CorrelationWellSolver', marks=pytest.mark.correlation),
)

# компутационные солверы
test_cases_computations = (
    'ComputationPipeLineCircuit',
    'UpwindSolver',
)


@pytest.mark.incremental
@pytest.mark.parametrize('solver_type', test_cases_correlations + test_cases_computations)
@pytest.mark.parametrize('geometry', geometries)
@pytest.mark.parametrize('fluid', fluid_models)
@pytest.mark.parametrize('two_phase_friction_model', two_phase_friction_models)
@pytest.mark.parametrize('one_phase_friction_model', one_phase_friction_models)
class TestAssertEquality(Equality06Mixin):
    """
    Наследует все методы сравнения и проверки эквивалентности из Equality06Mixin.
    Сравнивает результаты выходных данных в рамках одной однофазной модели и одного солвера
    с различными двухфазными моделями. Они должны быть идентичны.
    """

    @classmethod
    def setup_class(cls):
        """
        Созается словарь входных данных по ключам-параметрам calc_result_dict.
        Создается словарь для сравнения данных выходных файлов по ключам-параметрам check_params_dict.
        """
        cls.calc_result_dict = {slvr_type: {fld: {gmtr: {one_ph_fr_model: {two_ph_fr_model: None
                                                                           for two_ph_fr_model in
                                                                           two_phase_friction_models}
                                                         for one_ph_fr_model in one_phase_friction_models}
                                                  for gmtr in geometries}
                                            for fld in fluid_models}
                                for slvr_type in ([cor_slv_type.values[0] for cor_slv_type in test_cases_correlations]
                                                  + list(test_cases_computations))}

        cls.check_params_dict = {
            'data': ("pressure", "temperature", "velocity_oil", "velocity_gas", "velocity_water", "holdup"),

            'linear_condition': ("frac_oil", "frac_gas", "frac_water", "density_oil", "density_gas", "density_water",
                                 "viscosity_oil", "viscosity_gas", "viscosity_water", "mass_flow_oil", "mass_flow_gas",
                                 "mass_flow_water", "volumetric_flow_oil", "volumetric_flow_gas",
                                 "volumetric_flow_water"),
            "standard_condition": ("frac_oil", "frac_gas", "frac_water", "density_oil", "density_gas", "density_water",
                                   "mass_flow_oil", "mass_flow_gas", "mass_flow_water", "volumetric_flow_oil",
                                   "volumetric_flow_gas", "volumetric_flow_water"),
            'separation_data': ("condensate_gas_factor", "water_gas_factor"),
        }

    def test_parse_calc_result(self, solver_type, fluid, geometry, one_phase_friction_model, two_phase_friction_model):
        """
        Получает путь до выходного файла, проверяет его существование. Результаты сохраняет в словарь.
        """

        # Получаем строку с именем корреляционного солвера
        if not isinstance(solver_type, str):
            solver_type = solver_type.values[0]

        # Формируем путь до выходного файла
        path = Path(output_dir / one_phase_friction_model / two_phase_friction_model / fluid / geometry /
                    solver_type / "output.json")
        if not path.exists():
            raise FileNotFoundError('Файл с выходными данными отсутствует')
        calculation_result = json_load(path)
        self.calc_result_dict[solver_type][fluid][geometry][one_phase_friction_model][
            two_phase_friction_model] = calculation_result

    def test_assert_equality(self, solver_type, fluid, geometry, one_phase_friction_model, two_phase_friction_model):

        """
        Сравнивает выходные данные тест-кейса в рамках одной однофазной модели и одного солвера с различными
        двухфазными моделями. Они должны быть идентичны. Формируется сообщение об ошибке.
        """

        err_msg = self.check_parameters_equivalnce(solver_type, fluid, geometry, one_phase_friction_model,
                                                   two_phase_friction_model)
        assert not err_msg, f'{len(err_msg)} errors in  solver-type-fluid-geometry-' \
                            f'one_phase_friction_model-two_phase_friction_model\n' + '\n'.join(err_msg)

