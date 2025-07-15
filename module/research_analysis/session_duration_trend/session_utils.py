import pandas as pd
from datetime import datetime, timedelta

class SessionProcessor:
    def __init__(self, session_timeout_minutes=30, course_filter=None):
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.course_filter = str(course_filter) if course_filter else None

    @staticmethod
    def unix_to_dt(x):
        return datetime.utcfromtimestamp(int(x))

    def _sessionize_chunk(self, chunk):
        # Drop rows with missing critical values
        chunk = chunk.dropna(subset=['userid', 'course', 'time'])

        # Filter for specific course if needed
        if self.course_filter:
            chunk = chunk[chunk['course'].astype(str) == self.course_filter]

        # Convert types
        chunk['userid'] = chunk['userid'].astype(str)
        chunk['course'] = chunk['course'].astype(str)
        chunk['time'] = chunk['time'].astype(int)

        # Convert time to datetime
        chunk['dt'] = chunk['time'].apply(self.unix_to_dt)

        # Sort and compute gaps
        chunk = chunk.sort_values(['userid', 'course', 'dt'])
        chunk['prev_dt'] = chunk.groupby(['userid', 'course'])['dt'].shift(1)
        chunk['gap'] = chunk['dt'] - chunk['prev_dt']
        chunk['new_session'] = (chunk['gap'] > self.session_timeout) | chunk['gap'].isna()
        chunk['session_id'] = chunk.groupby(['userid', 'course'])['new_session'].cumsum()

        # Aggregate session stats
        session_groups = chunk.groupby(['userid', 'course', 'session_id'])
        session_df = session_groups['dt'].agg(['min', 'max', 'count']).reset_index()

        # Convert min and max to datetime
        session_df['min'] = pd.to_datetime(session_df['min'])
        session_df['max'] = pd.to_datetime(session_df['max'])

        # Now safe to compute session_duration
        session_df['session_duration'] = (session_df['max'] - session_df['min']).dt.total_seconds() / 60

        return session_df
    
    def process_csv_files(self, csv_files):
        """
        Process a list of local CSV log files and return sessionized DataFrame.
        """
        session_list = []
        for file in csv_files:
            print(f"Processing: {file}")
            term_code = file.split('/')[-1].split('_')[0]
            chunk_iter = pd.read_csv(file, chunksize=500_000)
            for chunk in chunk_iter:
                session_df = self._sessionize_chunk(chunk)
                session_df['term_code'] = term_code
                session_list.append(session_df)

        return pd.concat(session_list, ignore_index=True)

    def process_dataframe(self, df, term_code="unknown"):
        """
        Process a pre-loaded DataFrame directly (e.g., from S3) and return sessionized results.
        """
        session_df = self._sessionize_chunk(df)
        session_df['term_code'] = term_code
        return session_df


  

    @staticmethod
    def aggregate_avg_session_duration(session_df):
        return session_df.groupby(['userid', 'term_code'])['session_duration'].mean().reset_index()
