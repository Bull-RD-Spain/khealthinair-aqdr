# Copyright © 2021-2026 Bull SAS
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of work done in the K-HEALTHinAIR EU funded project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Module with Air Quality API functions
"""

import logging
from datetime import datetime
from io import BytesIO, StringIO

import pandas as pd
import pytz
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from influxdb_client import InfluxDBClient
from modules.config import Config
from modules.enums import PARAMETERS_UNITS_DICT


def query_influx_data(
    influx_client: InfluxDBClient,
    pilot: str,
    scenario: str,
    sub_scenario: str,
    area: str,
    file_format: str,
    start_datetime: str = "2023-03-01",
    end_datetime: str | None = None,
):
    """
    Retrieves raw data from InfluxDB and processes it by calling custom
    process_dataframe function.

    Inputs:
        - pilot: specified pilot in GET request
        - scenario: specified scenario type in GET request
        - sub_scenario: specified scenario ID in GET request
        - area: specified area ID of the scenario in GET request
        - file_format: desired format for the output file (.csv/.xlsx)
        - start_datetime: specified starting datetime
        - end_datetime: specified end datetime

    Output:
        - FileResponse: processed measurements file ready to download
    """

    (
        start_date_utc_str,
        end_date_utc_str,
        start_date_cet_str,
        end_date_cet_str,
    ) = validate_datetimes(start_datetime, end_datetime)

    
    
    filters = f'r.id_pilot == "{pilot}" and r.scenario == "{scenario}"'
    
    if sub_scenario:
        filters += f' and r.sub_scenario == "{sub_scenario}"'
    
    if area:
        filters += f' and r.area == "{area}"'
     
    query = f"""from(bucket: "{Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_BUCKET"]}")
        |> range(start: {start_date_utc_str}, stop: {end_date_utc_str})
        |> filter(fn: (r) => r._measurement == "{Config.aqdr_ts_db["INFLUXDB_MEASUREMENT"]}")
        |> filter(fn: (r) => {filters})
        |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> drop(columns: ["_start", "_stop", "_measurement", "table", "result", "id_pilot", "scenario"])
    """
   


    # Influx query is performed in UTC dates (RFC3339 format)
    """query = f""""""from(bucket: "{Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_BUCKET"]}")
        |> range(start: {start_date_utc_str}, stop: {end_date_utc_str})
        |> filter(fn: (r) => r._measurement == "{Config.aqdr_ts_db["INFLUXDB_MEASUREMENT"]}")
        |> filter(fn: (r) => r.id_pilot == "{pilot}" and r.scenario == "{scenario}")
        |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> drop(columns: ["_start", "_stop", "_measurement", "table", "result", "id_pilot", "scenario"])
    """
    logging.debug("InfluxDB query:\n%s", query)

    try:
        data = influx_client.query_api().query_data_frame(
            org=Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_ORG"], query=query
        )
        logging.debug("Clean Influx Response...")
        measurements_df = clean_influx_response(data)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in query retrieval from InfluxDB:",
        ) from error

    # Filter by specified arguments
    processed_df = process_dataframe(
        measurements_df, pilot, scenario, sub_scenario, area
    )

    filename = (
        pilot
        + scenario
        + (sub_scenario if sub_scenario else "")
        + (area if area else "")
        + "_"
        + start_date_cet_str.split("T")[0]
        + "_"
        + end_date_cet_str.split("T")[0]  # simplify filename wo/ hours
    )

    logging.info(
        "Measurements file [%s.%s] almost ready to download...",
        filename,
        file_format.value,
    )

    if file_format.value == "csv":
        stream = StringIO()
        processed_df.to_csv(stream, index="_time")

        return StreamingResponse(
            iter([stream.getvalue()]),
            headers={
                "Content-Disposition": f"attachment;filename={filename}.csv"
            },
        )

    elif file_format.value == "xlsx":
        output_file = BytesIO()
        try:
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                processed_df.to_excel(
                    writer, sheet_name="AQ Data", index="_time"
                )
                units_df = pd.DataFrame.from_dict(PARAMETERS_UNITS_DICT)
                units_df.to_excel(writer, sheet_name="Units", index=False)

            return StreamingResponse(
                iter([output_file.getvalue()]),
                headers={
                    "Content-Disposition": f"attachment;filename={filename}.xlsx"
                },
            )
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error.args[0],
            ) from error


def clean_influx_response(influx_data) -> pd.DataFrame:
    """
    Takes raw response from InfluxDB query and ensures it is
    returned as a single pd.DF even if there was more than one initial DF
    (e.g., due to updates in InfluxDB table).
    Args:
        - influx_data: raw response from query (pd.DF or list of pd.DFs)
    """

    # Records in list of DFs due to InfluxDB table updates
    # (e.g., new params added)
    if isinstance(influx_data, list):
        df = influx_data[0]

        # Concatenate DFs and merge them by keys union
        for i in range(1, len(influx_data)):
            df = pd.merge(df, influx_data[i], how="outer")

        return df

    # Records in only 1 DF
    # (i.e., Influx table identical to when it was created)
    elif isinstance(influx_data, pd.DataFrame):
        return influx_data
    else:
        raise ValueError("Input should be pd.DF or list of pd.DFs.")


def process_dataframe(
    influx_df: pd.DataFrame,
    pilot: str,
    scenario: str,
    sub_scenario: str = None,
    area: str = None,
):
    """
    Filters initial measurements extracted from InfluxDB according
    to specific pilot, scenario, scenario ID (opt) and area ID (opt).

    Inputs:
        - influx_df: raw pd.DF directly extracted from InfluxDB in specified
          datetime range
        - pilot: pilot of interest (depends on endpoint)
        - scenario: scenario type of interest
        - sub_scenario: specific scenario ID (default: None = all IDs within
          previous hierarchy level)
        - area: specific area ID (default: None = all IDs within previous
          hierarchy level)

    Output:
        - df: filtered pd.DF with information of interest
    """

    # Prevent empty DF
    if influx_df.empty:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            # detail="No measurements found in specified datetimes.",
        )

    df = influx_df.sort_values(by="_time")

    # Reordering
    
    base_cols = ["_time"]

    # Add those colls that exists in the DataFrame
    opcional_cols = ["sub_scenario", "area"]
    reordering_cols = base_cols + [col for col in opcional_cols if col in df.columns]

    # Create the two DAtaframes if there are valid columns
    df1 = df[reordering_cols]
    df2 = df.drop(columns=reordering_cols, errors="ignore")
    df = pd.concat([df1, df2], axis=1)
    
    # reordering_cols = ["_time", "sub_scenario", "area"]
    # df1, df2 = df[reordering_cols], df.drop(columns=reordering_cols, axis=1)
    # df = pd.concat([df1, df2], axis=1)

    # Level 1 filtering: Subscenario level (opt)
    if sub_scenario and (scenario + sub_scenario in df["sub_scenario"].values):
        df = df[df["sub_scenario"] == (scenario + sub_scenario)]
        df = df.drop(columns=["sub_scenario"])

    elif sub_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario ID {scenario + sub_scenario} "
            + f"does not exist in {pilot}.",
        )

    # Level 2 filtering: Area level (opt)
    if area and (scenario + sub_scenario + area) in df["area"].values:
        df = df[df["area"] == (scenario + sub_scenario + area)]
        df = df.drop(columns=["area"])

    elif area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Area ID {area} "
            + f"does not exist in {pilot + scenario + sub_scenario}.",
        )

    # Prevent empty DF again after filters
    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            # detail="No measurements found in the specified datetimes.",
        )

    # Some other cleaning
    if pilot == "NO":
        df = df.drop(columns=["result", "table"])  # Differentiate OAQ[_kunak]
    else:
        df = df.drop(columns=["AQ", "result", "table"])
    df["_time"] = pd.to_datetime(df["_time"]).round("min")
    # AQFD-TS-DB data is returned in UTC timezone, convert to CET timezone
    df = df.set_index("_time").tz_convert("Europe/Madrid").tz_localize(None)
    df.sort_index(inplace=True)

    return df


def validate_datetimes(start_datetime: str = None, end_datetime: str = None):
    """
    Performs datetime validation of specified datetimes.
    Inputs:
        - start_datetime, end_datetime: provided datetimes as GET params
        as str (ISO8601 format)

    Outputs:
        - initTime, finalTime: transformed datetimes as str (RFC 3339 format)
    """

    # All pilots are CET timezone
    cet = pytz.timezone("Europe/Madrid")

    # start_datetime validation (default: 2023-03-01)
    if start_datetime is None:
        start_datetime = datetime.fromisoformat("2023-03-01T00:00:00")
    else:
        try:
            start_datetime = datetime.fromisoformat(
                str(start_datetime) + "T00:00:00"
            )
        except Exception as error:
            raise HTTPException(
                status_code=400,
                detail="start_datetime invalid date format: [YYYY-mm-dd].",
            ) from error

    # end_datetime validation (default: time of the request)
    if end_datetime is None:
        end_datetime = datetime.now(tz=cet)
    else:
        try:
            end_datetime = datetime.fromisoformat(
                str(end_datetime) + "T00:00:00"
            )
        except Exception as error:
            raise HTTPException(
                status_code=400,
                detail="end_datetime invalid date format: [YYYY-mm-dd].",
            ) from error

    # Ensure dates are not localized
    start_datetime = start_datetime.replace(tzinfo=None)
    end_datetime = end_datetime.replace(tzinfo=None)
    # Localize requested dates as in CET timezone
    start_date_cet = cet.localize(start_datetime)
    end_date_cet = cet.localize(end_datetime)
    # Save CET times in str
    start_date_cet_str = start_date_cet.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date_cet_str = end_date_cet.strftime("%Y-%m-%dT%H:%M:%SZ")

    # datetime range validation
    if start_date_cet >= end_date_cet:
        raise HTTPException(
            status_code=400,
            detail="start_datetime must be previous than end_datetime.",
        )

    # Convert CET dates: to UTC tz for Flux query
    start_date_utc = start_date_cet.astimezone(pytz.UTC)
    end_date_utc = end_date_cet.astimezone(pytz.UTC)
    # Save UTC times in str (in RFC 3339 format for Flux query)
    start_date_utc_str = start_date_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date_utc_str = end_date_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    return (
        start_date_utc_str,
        end_date_utc_str,
        start_date_cet_str,
        end_date_cet_str,
    )
