import streamlit as st
import pandas as pd


def show_success(message: str):
    st.success(message)


def show_error(message: str):
    st.error(message)


def show_info(message: str):
    st.info(message)


# def records_to_dataframe(records):
#     """
#     Convert list of dictionaries / objects into a DataFrame.
#     """

#     if records is None:
#         return pd.DataFrame()

#     if isinstance(records, pd.DataFrame):
#         return records

#     if not isinstance(records, list):
#         records = list(records)

#     if not records:
#         return pd.DataFrame()

#     result = []

#     for record in records:

#         if isinstance(record, dict):
#             result.append(record)

#         elif hasattr(record, "__dict__"):
#             data = {}

#             for key, value in record.__dict__.items():
#                 if not key.startswith("_"):
#                     data[key] = value

#             result.append(data)

#         else:
#             result.append(record)

#     return pd.DataFrame(result)


def records_to_dataframe(records):
    """
    Convert database records into a pandas DataFrame.

    Supports:
    - list of dictionaries
    - list of tuples
    - model objects
    - pandas DataFrame
    """

    if records is None:
        return pd.DataFrame()

    if isinstance(records, pd.DataFrame):
        return records

    if not isinstance(records, list):
        try:
            records = list(records)
        except TypeError:
            return pd.DataFrame()

    if not records:
        return pd.DataFrame()

    result = []

    for record in records:

        # Dictionary returned by MySQL
        if isinstance(record, dict):

            result.append(
                dict(record)
            )

        # Tuple/list returned by MySQL
        elif isinstance(record, (tuple, list)):

            result.append(
                list(record)
            )

        # Assignment / Employee / Project object
        elif hasattr(record, "__dict__"):

            data = {}

            for key, value in record.__dict__.items():

                if not key.startswith("_"):

                    data[key] = value

            result.append(data)

        else:

            result.append(record)

    try:

        return pd.DataFrame(result)

    except Exception as exc:

        raise ValueError(
            f"Unable to convert records to DataFrame: {exc}"
        )


def safe_execute(function, success_message=None):
    """
    Execute service operation safely.
    """

    try:
        result = function()

        if success_message:
            st.success(success_message)

        return result

    except Exception as exc:
        st.error(f"Operation failed: {exc}")
        return None


def refresh_page():
    st.rerun()