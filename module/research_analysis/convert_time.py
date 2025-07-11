import pandas as pd

def convert_time(df, time_col="time"):

    df = df.copy()

    # Convert UNIX timestamp to datetime
    dt_series = pd.to_datetime(df[time_col], unit='s')

    # Add readable full datetime
    df['Readable_Time'] = dt_series

    # Add time components
    df['Year'] = dt_series.dt.year
    df['Month'] = dt_series.dt.month
    df['Day'] = dt_series.dt.day
    df['Hour'] = dt_series.dt.hour
    df['Minute'] = dt_series.dt.minute
    df['Second'] = dt_series.dt.second

    return df

