# ################################################################################################
# import pandas as pd
# from src.models import assessment

# class AssessmentService:
#     def __init__(self, assessment: pd.DataFrame, submissions: pd.DataFrame):

#         self.assessment = assessment.copy()
#         self.submissions = submissions.copy()
#         self.merged_df = None  # Will hold combined assessment + submissions later


# ######### convert to datetime function ##############################################################################
#     def convert_to_datetime(
#         self,
#         column_name: str,
#         df: pd.DataFrame = None,
#         unit: str = 's',

#         tz: str = None
#     ) -> pd.DataFrame:

#         target_df = df if df is not None else self.merged_df
#         if target_df is None:
#             raise ValueError("No DataFrame provided and merged_df is None.")
#         if column_name not in target_df.columns:
#             raise ValueError(f"Column '{column_name}' not found in DataFrame.")
        
#         # Convert Unix timestamp to datetime
#         target_df[column_name] = pd.to_datetime(target_df[column_name], unit=unit, errors='coerce', utc=True)
        
#         # Convert to specific timezone if provided
#         if tz:
#             target_df[column_name] = target_df[column_name].dt.tz_convert(tz)
        
#         return target_df
    

# ######### every semester duedate function #################################################### 
    

#     def get_latest_due_date(
#             self,
#             df: pd.DataFrame = None,
#             group_cols: list = ["cmid", "course", "assign_id", "assign_name"],
#             date_col: str = "duedate"
#         ) -> pd.DataFrame:
    
#             target_df = df if df is not None else self.assessment
#             if target_df is None:
#                 raise ValueError("No DataFrame provided and merged_df is None.")
#             if date_col not in target_df.columns:
#                 raise ValueError(f"Column '{date_col}' not found in DataFrame.")
#             for col in group_cols:
#                 if col not in target_df.columns:
#                     raise ValueError(f"Group column '{col}' not found in DataFrame.")

#             # Ensure date column is datetime
#             target_df[date_col] = pd.to_datetime(target_df[date_col], errors='coerce')

#             # Sort by date descending so the first row per group is the latest
#             target_df_sorted = target_df.sort_values(by=date_col, ascending=False)

#             # Drop duplicates keeping the first (latest date) per group
#             latest_df = target_df_sorted.drop_duplicates(subset=group_cols, keep="first")

#             # Optional: reset index
#             latest_df = latest_df.reset_index(drop=True)

#             return latest_df
    

# ######### weekly log file function #################################################### 
    
    
    # def log_to_action_time(
    #     self,
    #     df_log: pd.DataFrame,
    # ) -> pd.DataFrame:
    #     # Always convert 'time' column in logs
    #     df_log = self.convert_to_datetime(
    #         column_name="time",
    #         df=df_log,
    #         unit="s",
    #         tz="Australia/Adelaide"
    #     )

    #     need_cols = ["userid", "time", "cmid", "action"]
    #     missing_cols = [col for col in need_cols if col not in df_log.columns]
    #     if missing_cols:
    #         raise ValueError(f"Missing columns in log DataFrame: {missing_cols}")

    #     return df_log[need_cols]

#     def filter_actions_by_period(
#         self,
#         df: pd.DataFrame,
#         start: str,
#         end: str,
#         date_format: str = "%d/%m/%Y",
#         tz: str = "Australia/Adelaide"
#     ) -> pd.DataFrame:

#         if "time" not in df.columns:
#             raise ValueError("DataFrame must have a 'time' column in datetime format.")

#         # Ensure df["time"] is datetime
#         if not pd.api.types.is_datetime64_any_dtype(df["time"]):
#             df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)

#         # Parse input dates
#         start_date = pd.to_datetime(start, format=date_format).tz_localize(tz)
#         end_date = pd.to_datetime(end, format=date_format).tz_localize(tz)

#         # Align df timezone to match
#         df["time"] = df["time"].dt.tz_convert(tz)

#         # Filter inclusive range
#         mask = (df["time"] >= start_date) & (df["time"] <= end_date)
#         return df.loc[mask].copy()



# ######### weekly submit time file function #################################################### 

#     def get_action_submit(
#         self,
#         df: pd.DataFrame,
#         start: str = None,
#         end: str = None
#     ):

#         if df is None:
#             raise ValueError("Input DataFrame is required.")

#         if "action" not in df.columns:
#             raise ValueError("DataFrame must contain an 'action' column.")

#         # Normalize action values
#         df["action_clean"] = df["action"].astype(str).str.strip().str.lower()

#         filtered = df[df["action_clean"] == "submit for grading"].copy()

#         if filtered.empty:
#             return {
#                 "message": f"this week {start} to {end} is no submission requirement needed"
#             }

#         return filtered



    
#     def get_latest_userid_subtime(self, df: pd.DataFrame = None) -> pd.DataFrame:
 
#             latest_df = df.sort_values('time', ascending=False).groupby(['userid', 'cmid'], as_index=False).first()

#             return latest_df


#     def groupby_userid_submissiontime(self, df: pd.DataFrame = None):
#         target_df = df if df is not None else self.submissions
#         if target_df is None or target_df.empty:
#             print("⚠️ There is no submission requirement for the last week.")
#             return None, None

#         required_cols = ["cmid", "id", "time", "userid"]
#         for col in required_cols:
#             if col not in target_df.columns:
#                 raise ValueError(f"Required column '{col}' not found in submissions DataFrame.")

#         # Keep only relevant columns
#         df = target_df[required_cols].copy()

#         df["userid"] = pd.to_numeric(df["userid"], errors="coerce").astype("Int64")
#         df = df.dropna(subset=["userid"])
#         df["userid"] = df["userid"].astype(int)

#         # Drop exact duplicate rows
#         df = df.drop_duplicates(subset=["cmid", "id", "time", "userid"])

#         # Sort by userid, then cmid and time
#         df_sorted = df.sort_values(["userid", "cmid", "time"]).reset_index(drop=True)

#         # Optionally, group by userid but preserve sorting
#         grouped = {userid: group for userid, group in df_sorted.groupby("userid")}

#         return df_sorted, grouped


#     def submit_size_userid(self, df: pd.DataFrame = None):
#         target_df = df if df is not None else self.submissions
#         if target_df is None or target_df.empty:
#             print("⚠️ There is no submission requirement for the last week.")
#             return None

#         required_cols = ["userid"]
#         for col in required_cols:
#             if col not in target_df.columns:
#                 raise ValueError(f"Required column '{col}' not found in submissions DataFrame.")

#         # Keep only userid
#         df = target_df[["userid"]].copy()

#         # Ensure userid is integer
#         df["userid"] = pd.to_numeric(df["userid"], errors="coerce").astype("Int64")
#         df = df.dropna(subset=["userid"])
#         df["userid"] = df["userid"].astype(int)

#         # Count submissions per user
#         submit_counts = df.groupby("userid").size().reset_index(name="submission_count")

#         return submit_counts


#     def attach_due_date_from_df(self, df_duedate: pd.DataFrame, userid_submissions: pd.DataFrame):
     
#         if df_duedate.empty or userid_submissions.empty:
#             print("⚠️ One of the DataFrames is empty.")
#             return pd.DataFrame()  # return empty DF if any input is empty

#         # Select and rename columns from df_duedate
#         df_duedate_renamed = df_duedate[['cmid', 'assign_name', 'duedate']].copy()
#         df_duedate_renamed = df_duedate_renamed.rename(columns=lambda col: f"{col}_assign" if col != 'cmid' else col)

#         # Merge on 'cmid'
#         merged_df = pd.merge(
#             userid_submissions,
#             df_duedate_renamed,
#             on='cmid',
#             how='left'  # keep all userid_submissions rows
#         )
#     # Sort by duedate_assign ascending
#         merged_df = merged_df.sort_values('duedate_assign', ascending=True).reset_index(drop=True)

#         self.merged_df = merged_df
#         return self


# ######### calculate sunmission score function #################################################### 
    

#     def calculate_time_score(self, T_max=14, T_late=-2, submission_col='time', due_col='duedate_assign'):

#         if self.merged_df is None:
#             raise ValueError("Call attach_due_date() before calculate_time_score()")

#         df = self.merged_df.copy()
#         df[submission_col] = pd.to_datetime(df[submission_col])
#         df[due_col] = pd.to_datetime(df[due_col])

#         time_diff = df[due_col] - df[submission_col]
#         df['time_before_deadline_days'] = time_diff.dt.total_seconds() / 86400
#         df['time_before_deadline_hours'] = time_diff.dt.total_seconds() / 3600

#         def normalize(t):
#             if t >= T_max:
#                 return 1.0
#             elif t >= 0:
#                 return t / T_max
#             else:
#                 return max(0.0, 1 + t / abs(T_late))

#         df['score'] = df['time_before_deadline_days'].apply(normalize)
#         self.merged_df = df
#         return self
    
# ######### summary sunmission score function #################################################### 
    
    
#     def summarize_early_late_counts(self, scored_df: pd.DataFrame):
  
#         df = scored_df.copy()
        
#         # Classify submissions
#         df["time_category"] = df["time_before_deadline_hours"].apply(lambda x: "early" if x > 0 else "late")
        
#         # 1️⃣ Semester overall summary
#         semester_summary = df["time_category"].value_counts().rename_axis("time_category").reset_index(name="submission_count")
#         # Ensure columns for both early/late exist
#         semester_summary = semester_summary.pivot_table(index=None, columns="time_category", values="submission_count", fill_value=0).rename(columns={"early": "early_count", "late": "late_count"}).reset_index(drop=True)

#         # 2️⃣ Per student summary
#         per_student_summary = df.groupby(["userid", "time_category"]).size().unstack(fill_value=0).rename(columns={"early": "early_count", "late": "late_count"}).reset_index()
        
#         # 3️⃣ Per assignment summary
#         per_assignment_summary = df.groupby(["cmid", "time_category"]).size().unstack(fill_value=0).rename(columns={"early": "early_count", "late": "late_count"}).reset_index()
        
#         # Ensure early_count and late_count exist in all summaries
#         for summary in [semester_summary, per_student_summary, per_assignment_summary]:
#             for col in ["early_count", "late_count"]:
#                 if col not in summary.columns:
#                     summary[col] = 0
        
#         return semester_summary, per_student_summary, per_assignment_summary


#     def summarize_scores(self):
#         if self.merged_df is None:
#             raise ValueError("Call attach_due_date() and calculate_time_score() first")

#         # 1️⃣ Overall summary per assignment (grouped by cmid)
#         overall_summary_per_assign = (
#             self.merged_df.groupby(['cmid', 'assign_name_assign'], as_index=False)['score']
#             .agg(
#                 avg_score='mean',
#                 median_score='median',
#                 max_score='max',
#                 min_score='min'
#             )
#         )

#         # 2️⃣ Per student summary (across all assignments)
#         per_student_summary = self.merged_df.groupby('userid')['score'].agg(
#             avg_score='mean',
#             max_score='max',
#             min_score='min'
#         ).reset_index()

#         # 3️⃣ Semester overall summary (all scores together, no grouping)
#         semester_overall_summary = pd.DataFrame({
#             'avg_score': [self.merged_df['score'].mean()],
#             'median_score': [self.merged_df['score'].median()],
#             'max_score': [self.merged_df['score'].max()],
#             'min_score': [self.merged_df['score'].min()]
#         })

#         return overall_summary_per_assign, per_student_summary, semester_overall_summary


# #########  generate output trigger userid #################################################### 
    

#     def generate_submission_index_trigger_users(self, score_threshold: float = 0.4, df: pd.DataFrame = None) -> pd.DataFrame:

#         target_df = df if df is not None else self.merged_df
#         if target_df is None or target_df.empty:
#             print("⚠️ There is no data to check for low scores.")
#             return pd.DataFrame(columns=["userid", "cmid", "score"])

#         # Filter rows where score is below threshold
#         low_score_df = target_df[target_df["score"] < score_threshold][["userid", "cmid", "score"]].copy()

#         # Optional: reset index
#         low_score_df = low_score_df.reset_index(drop=True)
#         return low_score_df
    

#     # def get_dataframe(self):
#     #     """Return the merged DataFrame with scores"""
#     #     return self.merged_df
 


#  ################################################################################################### PLOT FUNCTION ###########################################################################################

 




# jdkbkvfvbdlv


import pandas as pd
from src.models import assessment
from src.common.readcsv_writehtml import convert_to_datetime


class AssessmentService:
    def __init__(self, assessment: pd.DataFrame, submissions: pd.DataFrame):
        self.assessment = assessment.copy() if assessment is not None else pd.DataFrame()
        self.submissions = submissions.copy() if submissions is not None else pd.DataFrame()
        self.merged_df = None  # Will hold combined assessment + submissions later

    ######### convert to datetime function ##############################################################################
    # def convert_to_datetime(self, column_name: str, df: pd.DataFrame = None, unit: str = 's', tz: str = None) -> pd.DataFrame:
    #     target_df = df if df is not None else self.merged_df
    #     if target_df is None or target_df.empty:
    #         return pd.DataFrame()  # return empty DF if no data
    #     if column_name not in target_df.columns:
    #         raise ValueError(f"Column '{column_name}' not found in DataFrame.")
    #     target_df[column_name] = pd.to_datetime(target_df[column_name], unit=unit, errors='coerce', utc=True)
    #     if tz:
    #         target_df[column_name] = target_df[column_name].dt.tz_convert(tz)
    #     return target_df
    
# ######### every semester duedate function #################################################### 
    


    def get_latest_due_date(
            self,
            df: pd.DataFrame = None,
            group_cols: list = ["cmid", "course", "assign_id", "assign_name"],
            date_col: str = "duedate"
        ) -> pd.DataFrame:
    
            target_df = df if df is not None else self.assessment
            if target_df is None:
                raise ValueError("No DataFrame provided and merged_df is None.")
            if date_col not in target_df.columns:
                raise ValueError(f"Column '{date_col}' not found in DataFrame.")
            for col in group_cols:
                if col not in target_df.columns:
                    raise ValueError(f"Group column '{col}' not found in DataFrame.")

            # Ensure date column is datetime
            target_df[date_col] = pd.to_datetime(target_df[date_col], errors='coerce')

            # Sort by date descending so the first row per group is the latest
            target_df_sorted = target_df.sort_values(by=date_col, ascending=False)

            # Drop duplicates keeping the first (latest date) per group
            latest_df = target_df_sorted.drop_duplicates(subset=group_cols, keep="first")

            # Optional: reset index
            latest_df = latest_df.reset_index(drop=True)

            return latest_df

# ######### weekly log file function #################################################### 

    def log_to_action_time(
        self,
        df_log: pd.DataFrame,
    ) -> pd.DataFrame:
        # Always convert 'time' column in logs
        df_log = convert_to_datetime(
            column_name="time",
            df=df_log,
            unit="s",
            tz="Australia/Adelaide"
        )

        need_cols = ["userid", "time", "cmid", "action"]
        missing_cols = [col for col in need_cols if col not in df_log.columns]
        if missing_cols:
            raise ValueError(f"Missing columns in log DataFrame: {missing_cols}")

        return df_log[need_cols]


    def filter_actions_by_period(
        self,
        df: pd.DataFrame,
        col_name: str ,
        start: str,
        end: str,
        date_format: str = "%d/%m/%Y",
        tz: str = "Australia/Adelaide"
    ) -> pd.DataFrame:

        if col_name not in df.columns:
            raise ValueError("DataFrame must have a 'time' column in datetime format.")

        # Ensure df[col_name] is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[col_name]):
            df[col_name] = pd.to_datetime(df[col_name], errors="coerce", utc=True)

        # Parse input dates
        start_date = pd.to_datetime(start, format=date_format).tz_localize(tz)
        end_date = pd.to_datetime(end, format=date_format).tz_localize(tz)

        # Align df timezone to match
        df[col_name] = df[col_name].dt.tz_convert(tz)

        # Filter inclusive range
        mask = (df[col_name] >= start_date) & (df[col_name] <= end_date)
        return df.loc[mask].copy()


    ######### weekly submit time file function #################################################### 

    def get_action_submit(
        self,
        df: pd.DataFrame,
        start: str = None,
        end: str = None
    ) -> pd.DataFrame:

        if df is None:
            raise ValueError("Input DataFrame is required.")

        if "action" not in df.columns:
            raise ValueError("DataFrame must contain an 'action' column.")

        # Normalize action values
        df["action_clean"] = df["action"].astype(str).str.strip().str.lower()

        # Filter for 'submit for grading'
        filtered = df[df["action_clean"] == "submit for grading"].copy()
        filtered = filtered.drop(columns=["action_clean"])

        # If empty, return empty DataFrame with the expected columns
        if filtered.empty:
            filtered = pd.DataFrame(columns=df.columns)

        return filtered


    ######### latest submission per user #################################################### 
    def get_latest_userid_subtime(self, df: pd.DataFrame = None) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame(columns=['userid', 'cmid', 'time'])
        latest_df = df.sort_values('time', ascending=False).groupby(['userid', 'cmid'], as_index=False).first()
        return latest_df

    ######### groupby user submission #################################################### 
    def groupby_userid_submissiontime(self, df: pd.DataFrame = None):
        target_df = df if df is not None else self.submissions
        if target_df is None or target_df.empty:
            return pd.DataFrame(columns=["cmid", "id", "time", "userid"]), {}
        required_cols = ["cmid", "time", "userid"]
        for col in required_cols:
            if col not in target_df.columns:
                raise ValueError(f"Required column '{col}' not found in submissions DataFrame.")
        df = target_df[required_cols].copy()
        df["userid"] = pd.to_numeric(df["userid"], errors="coerce").astype("Int64")
        df = df.dropna(subset=["userid"])
        df["userid"] = df["userid"].astype(int)
        df = df.drop_duplicates(subset=["cmid","time", "userid"])
        df_sorted = df.sort_values(["userid", "cmid", "time"]).reset_index(drop=True)
        grouped = {userid: group for userid, group in df_sorted.groupby("userid")}
        return df_sorted, grouped

    ######### submission count per user #################################################### 
    def submit_size_userid(self, df: pd.DataFrame = None):
        target_df = df if df is not None else self.submissions
        if target_df is None or target_df.empty:
            return pd.DataFrame(columns=["userid", "submission_count"])
        if "userid" not in target_df.columns:
            raise ValueError("Required column 'userid' not found in submissions DataFrame.")
        df = target_df[["userid"]].copy()
        df["userid"] = pd.to_numeric(df["userid"], errors="coerce").astype("Int64")
        df = df.dropna(subset=["userid"])
        df["userid"] = df["userid"].astype(int)
        submit_counts = df.groupby("userid").size().reset_index(name="submission_count")
        return submit_counts

    ######### attach due date #################################################### 
    def attach_due_date_from_df(self, df_duedate: pd.DataFrame, userid_submissions: pd.DataFrame):
        if df_duedate.empty or userid_submissions.empty:
            self.merged_df = pd.DataFrame()  # always keep merged_df consistent
            return self
        df_duedate_renamed = df_duedate[['cmid', 'assign_name', 'duedate']].copy()
        df_duedate_renamed = df_duedate_renamed.rename(columns=lambda col: f"{col}_assign" if col != 'cmid' else col)
        merged_df = pd.merge(userid_submissions, df_duedate_renamed, on='cmid', how='left')
        merged_df = merged_df.sort_values('duedate_assign', ascending=True).reset_index(drop=True)
        self.merged_df = merged_df
        return self

    ######### calculate submission score #################################################### 
    def calculate_time_score(self, T_max=14, T_late=-2, submission_col='time', due_col='duedate_assign'):
        if self.merged_df is None or self.merged_df.empty:
            return self
        df = self.merged_df.copy()
        # df[submission_col] = pd.to_datetime(df[submission_col], errors='coerce')
        # df[due_col] = pd.to_datetime(df[due_col], errors='coerce')
        # time_diff = df[due_col] - df[submission_col]

        # Ensure both columns are datetime
        df[submission_col] = pd.to_datetime(df[submission_col], errors='coerce')
        df[due_col] = pd.to_datetime(df[due_col], errors='coerce')

        # Make both tz-aware in Australia/Adelaide
        if df[submission_col].dt.tz is None:
            df[submission_col] = df[submission_col].dt.tz_localize('Australia/Adelaide', ambiguous='NaT')
        else:
            df[submission_col] = df[submission_col].dt.tz_convert('Australia/Adelaide')

        if df[due_col].dt.tz is None:
            df[due_col] = df[due_col].dt.tz_localize('Australia/Adelaide', ambiguous='NaT')
        else:
            df[due_col] = df[due_col].dt.tz_convert('Australia/Adelaide')

        # Then subtract safely
        time_diff = df[due_col] - df[submission_col]

        df['time_before_deadline_days'] = time_diff.dt.total_seconds() / 86400
        df['time_before_deadline_hours'] = time_diff.dt.total_seconds() / 3600
        def normalize(t):
            if t >= T_max: return 1.0
            elif t >= 0: return t / T_max
            else: return max(0.0, 1 + t / abs(T_late))
        df['score'] = df['time_before_deadline_days'].apply(normalize)
        self.merged_df = df
        return self

    
######### summary sunmission score function #################################################### 
    
    
    def summarize_early_late_counts(self, scored_df: pd.DataFrame):

        df = scored_df.copy()
        
        # Classify submissions
        df["time_category"] = df["time_before_deadline_hours"].apply(lambda x: "early" if x > 0 else "late")
        
        # 1️⃣ Semester overall summary
        semester_summary = df["time_category"].value_counts().rename_axis("time_category").reset_index(name="submission_count")
        # Ensure columns for both early/late exist
        semester_summary = semester_summary.pivot_table(index=None, columns="time_category", values="submission_count", fill_value=0).rename(columns={"early": "early_count", "late": "late_count"}).reset_index(drop=True)

        # 2️⃣ Per student summary
        per_student_summary = df.groupby(["userid", "time_category"]).size().unstack(fill_value=0).rename(columns={"early": "early_count", "late": "late_count"}).reset_index()
        
        # 3️⃣ Per assignment summary
        per_assignment_summary = df.groupby(["cmid", "time_category"]).size().unstack(fill_value=0).rename(columns={"early": "early_count", "late": "late_count"}).reset_index()
        
        # Ensure early_count and late_count exist in all summaries
        for summary in [semester_summary, per_student_summary, per_assignment_summary]:
            for col in ["early_count", "late_count"]:
                if col not in summary.columns:
                    summary[col] = 0
        
        return semester_summary, per_student_summary, per_assignment_summary


    def summarize_scores(self):
        if self.merged_df is None:
            raise ValueError("Call attach_due_date() and calculate_time_score() first")

        # 1️⃣ Overall summary per assignment (grouped by cmid)
        overall_summary_per_assign = (
            self.merged_df.groupby(['cmid', 'assign_name_assign'], as_index=False)['score']
            .agg(
                avg_score='mean',
                median_score='median',
                max_score='max',
                min_score='min'
            )
        )

        # 2️⃣ Per student summary (across all assignments)
        per_student_summary = self.merged_df.groupby('userid')['score'].agg(
            avg_score='mean',
            max_score='max',
            min_score='min'
        ).reset_index()

        # 3️⃣ Semester overall summary (all scores together, no grouping)
        semester_overall_summary = pd.DataFrame({
            'avg_score': [self.merged_df['score'].mean()],
            'median_score': [self.merged_df['score'].median()],
            'max_score': [self.merged_df['score'].max()],
            'min_score': [self.merged_df['score'].min()]
        })

        return overall_summary_per_assign, per_student_summary, semester_overall_summary


#########  generate output trigger userid #################################################### 
    

    def generate_submission_index_trigger_users(self, score_threshold: float = 0.2, df: pd.DataFrame = None):
        target_df = df if df is not None else self.merged_df
        if target_df is None or target_df.empty:
            print("⚠️ There is no data to check for low scores.")
            return pd.DataFrame(columns=["userid", "cmid", "score"]), []

        # Ensure 'score' is numeric and round it
        target_df["score"] = pd.to_numeric(target_df["score"], errors="coerce").round(6)

        # Filter rows below threshold
        low_score_df = target_df[target_df["score"] < float(score_threshold)][["userid", "cmid", "score"]].copy()
        low_score_df = low_score_df.reset_index(drop=True)

        if low_score_df.empty:
            print("✅ There is no one below the score threshold. No reminder needed.")
            return low_score_df, []

        trigger_userids = low_score_df['userid'].unique().tolist()
        print(f"⚠️ Users {trigger_userids} should be reminded since their submission score is lower than {score_threshold}.")
        return low_score_df, trigger_userids

  
    # def get_dataframe(self):
    #     """Return the merged DataFrame with scores"""
    #     return self.merged_df



################################################################################################### PLOT FUNCTION ###########################################################################################





