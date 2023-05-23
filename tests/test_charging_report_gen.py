import pytest
from contextlib import nullcontext as does_not_raise
import responses
from io import StringIO
import subprocess
from pathlib import Path

from ev_charging_report.bin.charging_report_gen import (
    get_todays_caiso_fuelsource_data,
    get_latest_energy_mix_from_todays_caiso_data,
    calculate_clean_energy_percentage,
    interpret_clean_energy_percentage,
)


@pytest.mark.parametrize(
    "todays_supply_url, mocked_text, status, expected_response",
    [
        (
            "https://www.caiso.com/outlook/SP/fuelsource.csv",
            """Time,Solar,Wind,Geothermal,Biomass,Biogas,Small hydro,Coal,Nuclear,Natural Gas,Large Hydro,Batteries,Imports,Other
00:00,1,2373,819,283,228,357,3,2268,5764,5263,-271,7044,0""",
            200,
            """Time,Solar,Wind,Geothermal,Biomass,Biogas,Small hydro,Coal,Nuclear,Natural Gas,Large Hydro,Batteries,Imports,Other
00:00,1,2373,819,283,228,357,3,2268,5764,5263,-271,7044,0""",
        )
    ],
)
@responses.activate
def test_get_todays_caiso_fuelsource_data_unit(
    todays_supply_url, mocked_text, status, expected_response
):
    mocked_response = responses.add(
        responses.GET,
        todays_supply_url,
        body=mocked_text,
        status=status,
    )
    todays_fuelsource_data = get_todays_caiso_fuelsource_data(todays_supply_url)
    assert mocked_response.call_count == 1
    assert todays_fuelsource_data == expected_response


@pytest.mark.parametrize(
    "todays_supply_url, expected_column_names, expected_exception",
    [
        (
            "https://www.caiso.com/outlook/SP/fuelsource.csv",
            [
                "Natural Gas",
                "Nuclear",
                "Biomass",
                "Coal",
                "Geothermal",
                "Biogas",
                "Large Hydro",
                "Wind",
                "Solar",
                "Batteries",
                "Other",
                "Small hydro",
                "Imports",
            ],
            does_not_raise(),
        ),
        (
            "https://www.google.com",
            [
                "Natural Gas",
                "Nuclear",
                "Biomass",
                "Coal",
                "Geothermal",
                "Biogas",
                "Large Hydro",
                "Wind",
                "Solar",
                "Batteries",
                "Other",
                "Small hydro",
                "Imports",
            ],
            pytest.raises(AssertionError),
        ),
    ],
)
def test_get_todays_caiso_fuelsource_data_integration(
    todays_supply_url, expected_column_names, expected_exception
):
    with expected_exception:
        todays_fuelsource_data = get_todays_caiso_fuelsource_data(todays_supply_url)
        for expected_column_name in expected_column_names:
            assert expected_column_name in todays_fuelsource_data


@pytest.mark.parametrize(
    "energy_data_input,expected_output,expected_exception",
    [
        (
            StringIO(
                """Time,Solar,Wind,Geothermal,Biomass,Biogas,Small hydro,Coal,Nuclear,Natural Gas,Large Hydro,Batteries,Imports,Other
        00:00,-41,5800,863,297,227,338,1,2267,3641,4297,-108,6066,0
        04:15,-43,4909,859,302,225,333,2,2268,2473,4245,286,6036,0"""
            ),
            {
                "Solar": -43,
                "Wind": 4909,
                "Geothermal": 859,
                "Biomass": 302,
                "Biogas": 225,
                "Small hydro": 333,
                "Coal": 2,
                "Nuclear": 2268,
                "Natural Gas": 2473,
                "Large Hydro": 4245,
                "Batteries": 286,
                "Imports": 6036,
                "Other": 0,
            },
            does_not_raise(),
        ),
        (
            StringIO(
                """Time,Solar,Wind,Geothermal,Biomass,Biogas,Small hydro,Coal,Nuclear,Natural Gas,Large Hydro,Batteries,Imports,Other
        """
            ),
            None,
            pytest.raises(RuntimeError),
        ),
    ],
)
def test_get_latest_energy_mix_from_todays_caiso_data_unit(
    energy_data_input, expected_output, expected_exception
):
    with expected_exception:
        latest_supply_dict = get_latest_energy_mix_from_todays_caiso_data(
            energy_data_input
        )
        assert latest_supply_dict == expected_output


@pytest.mark.parametrize(
    "energy_dict,expected_output,expected_exception",
    [
        (
            {
                "Wind": 500,
                "Coal": 500,
                "Nuclear": 500,
            },
            66.7,
            does_not_raise(),
        ),
        (
            {
                "Solar": -500,
                "Coal": 500,
                "Nuclear": 0,
            },
            None,
            pytest.raises(ValueError),
        ),
    ],
)
def test_calculate_clean_energy_percentage_unit(
    energy_dict, expected_output, expected_exception
):
    with expected_exception:
        clean_energy_pct = calculate_clean_energy_percentage(energy_dict)
        assert clean_energy_pct == expected_output


@pytest.mark.parametrize(
    "clean_energy_percentage, expected_output, expected_exception",
    [
        ("Poldo the pig", None, pytest.raises(TypeError)),
        (
            80.0,
            "It's a perfect time to charge. The grid is very clean right now.",
            does_not_raise(),
        ),
        (
            80,
            "It's a perfect time to charge. The grid is very clean right now.",
            does_not_raise(),
        ),
        (60.0, "It's a decent time to charge.", does_not_raise()),
        (
            40.0,
            "It's not an ideal time to charge. The grid is using dirty energy right now.",
            does_not_raise(),
        ),
    ],
)
def test_interpret_clean_energy_percentage_unit(
    clean_energy_percentage, expected_output, expected_exception
):
    with expected_exception:
        grid_interpretation = interpret_clean_energy_percentage(clean_energy_percentage)
        assert grid_interpretation == expected_output


@pytest.mark.parametrize(
    "script_path, expected_returncode, expected_stderr, expected_stdout",
    [
        (
            Path(__file__).parent.parent / "bin/charging_report_gen.py",
            0,
            b"",
            b"The CA grid is currently comprised of ",
        )
    ],
)
def test_full_script(
    script_path, expected_returncode, expected_stderr, expected_stdout
):
    full_script_run = subprocess.run(["python", script_path], capture_output=True)
    assert full_script_run.returncode == expected_returncode
    assert full_script_run.stderr == expected_stderr
    assert expected_stdout in full_script_run.stdout
