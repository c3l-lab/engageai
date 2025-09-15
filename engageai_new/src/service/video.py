import pandas as pd
from src.models import video
import re

class VideoService:
    def __init__(self, VideoPanopto: pd.DataFrame= None):
        self.timestamp: pd.datetime
        self.session_name: str
        self.session_id: str
        self.minutes_delivered: float
        self.username: str
        self.user_id: str
        self.name: str
        self.viewing_type: str

######### OVERALL VIDEO OVERVIEW ##############################################################################
   
    ######### needed columns ##############################################################################
    def need_statvideo_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        needed_col=  [ 'Session','Video Duration Minutes']
        df= df[needed_col]
        df.drop_duplicates()
        return df
    
    def need_weekvideo_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        needed_columns = [
        'Video Name', 'Week']
        df = df[needed_columns]
        return df

    def define_whichweek(self, sem_start: str, sem_end: str, week_start: str, week_end: str) -> int:

        # Convert strings to datetime
        sem_start = pd.to_datetime(sem_start, dayfirst=True)
        week_start = pd.to_datetime(week_start, dayfirst=True)
        
        # Normalize semester start to the Monday of that week
        sem_monday = sem_start - pd.to_timedelta(sem_start.weekday(), unit="D")
        
        # Normalize target week_start to its Monday
        target_monday = week_start - pd.to_timedelta(week_start.weekday(), unit="D")
        
        # Calculate difference in weeks (1-based index)
        week_number = ((target_monday - sem_monday).days // 7) + 1
        
        return week_number
    

    def fix_week_overview(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()
        def process_week(val):
            if pd.isna(val):
                return val
            val_str = str(val).strip()
            # Handle 'x or y' pattern
            if "or" in val_str:
                numbers = re.findall(r'\d+', val_str)
                if numbers:
                    return int(min(map(int, numbers)))
                else:
                    return val_str
            # Handle pure numeric
            try:
                return int(val_str)
            except ValueError:
                return val_str  # keep string as-is

        # Apply processing
        df['Week'] = df['Week'].apply(process_week)

        # Sort numeric values first, strings stay at the end
        numeric_mask = df['Week'].apply(lambda x: isinstance(x, int))
        df_numeric = df[numeric_mask].sort_values(by='Week', ascending=True)
        df_non_numeric = df[~numeric_mask]
        df_sorted = pd.concat([df_numeric, df_non_numeric]).reset_index(drop=True)

        return df_sorted


    def map_weekvideo_videoduration(self,df_statvideo: pd.DataFrame, df_weekvideo: pd.DataFrame) -> pd.DataFrame:
        # Make a copy of df_weekvideo
        df_weekvideo_duration = df_weekvideo.copy()

        # Merge based on matching Session <-> Vidoe Name
        df_weekvideo_duration = df_weekvideo_duration.merge(
            df_statvideo[['Session', 'Video Duration Minutes']],
            left_on='Video Name',
            right_on='Session',
            how='left'
        )

        # Drop duplicate 'Session' column (since we only want Vidoe Name)
        df_weekvideo_duration.drop(columns=['Session'], inplace=True)

        return df_weekvideo_duration


    def groupby_week_overview(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Separate numeric and non-numeric weeks
        numeric_mask = df['Week'].apply(lambda x: isinstance(x, int))
        df_numeric = df[numeric_mask].sort_values(by='Week', ascending=True)
        df_non_numeric = df[~numeric_mask]

        # Define a helper to group by 'Week'
        def _group(group_df):
            return group_df.groupby('Week', as_index=False).agg(
                Video_Count=('Video Name', 'size'),
                Video_Name_List=('Video Name', list),
                Total_Duration_Minutes=('Video Duration Minutes', 'sum'),
                Duration_List=('Video Duration Minutes', list)
            )

        # Apply to both subsets
        df_numeric_grouped = _group(df_numeric)
        df_non_numeric_grouped = _group(df_non_numeric)

        # Concatenate numeric first, then non-numeric
        df_grouped = pd.concat([df_numeric_grouped, df_non_numeric_grouped]).reset_index(drop=True)

        return df_grouped

  
    # def groupby_week_overview(self, df: pd.DataFrame) -> pd.DataFrame:

    #     df = df.copy()
        
    #     # Separate numeric and non-numeric weeks
    #     numeric_mask = df['Week'].apply(lambda x: isinstance(x, int))
    #     df_numeric = df[numeric_mask].sort_values(by='Week', ascending=True)
    #     df_non_numeric = df[~numeric_mask]

    #     # Group numeric weeks
    #     df_numeric_grouped = df_numeric.groupby('Week', as_index=False).agg(
    #         Video_Count=('Video Name', 'size'),
    #         Video_Name_List=('Video Name', lambda x: list(x))
    #     )

    #     # Group non-numeric weeks
    #     df_non_numeric_grouped = df_non_numeric.groupby('Week', as_index=False).agg(
    #         Video_Count=('Video Name', 'size'),
    #         Video_Name_List=('Video Name', lambda x: list(x))
    #     )

    #     # Concatenate numeric first, then non-numeric
    #     df_grouped = pd.concat([df_numeric_grouped, df_non_numeric_grouped]).reset_index(drop=True)

    #     return df_grouped


######## VIDEO LOG ##############################################################################

    def need_log_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        needed_columns = [
        'Timestamp', 'Session Name', 'Session ID', 'Minutes Delivered', 'UserName', 'User ID']
        df = df[needed_columns]
        return df


    def convert_to_mins(self,df: pd.DataFrame) -> pd.DataFrame:
        df["Minutes Delivered"] = pd.to_numeric(df["Minutes Delivered"], errors="coerce").fillna(0.0)
        return df
    

    def week_schedule(self, df: pd.DataFrame, start: str, tz: str = "Australia/Adelaide") -> pd.DataFrame:
        # Convert start date to tz-aware datetime
        start_dt = pd.to_datetime(start, dayfirst=True).tz_localize(tz)

        # Normalize start_dt to Monday of that week
        week0_start = start_dt - pd.to_timedelta(start_dt.weekday(), unit="d")

        # Calculate week number relative to week0_start
        df["Week"] = ((df["Timestamp"] - week0_start).dt.days // 7).astype(int)

        # Cap week number at 12
        df["Week"] = df["Week"].clip(upper=12)
        
        # Sort dataframe by Week ascending
        df = df.sort_values(by="Week").reset_index(drop=True)

        return df

    def groupby_userid_week_watchvideo(self, df: pd.DataFrame) -> pd.DataFrame:

        # Define aggregation rules
        agg_dict = {}
        for col in df.columns:
            if col in ["Week", "User ID", "Session Name"]:
                continue  # These are groupby columns
            elif pd.api.types.is_numeric_dtype(df[col]):
                agg_dict[col] = "sum"  # Sum numeric columns like video minutes
            else:
                agg_dict[col] = "first"  # Keep first value for non-numeric columns

        # Group by the required columns
        grouped_df = df.groupby(["Week", "User ID", "Session Name"], as_index=False).agg(agg_dict)

        return grouped_df


    def summary_week_user_sessions(sef,df: pd.DataFrame) -> pd.DataFrame:

        # Group by Week, User ID, Session ID, Session Name and sum Minutes Delivered
        summary_df = (
            df.groupby(["Week", "User ID", "Session ID", "Session Name"], as_index=False)
            .agg({"Minutes Delivered": "sum"})
        )

        # Sort by Week and User ID for readability
        summary_df = summary_df.sort_values(by=["Week", "User ID"]).reset_index(drop=True)
        
        return summary_df
    
    ####### Compute per video and per user statistics #######

    def compute_per_video_stats(self, df: pd.DataFrame) -> pd.DataFrame:

        per_video = (
            df.groupby(["User ID", "Session ID", "Session Name"], as_index=False)
            .agg(
                total_minutes=("Minutes Delivered", "sum"),
                view_count=("Session ID", "count"),
            )
        )
        return per_video

    def compute_per_user_features(self, per_video: pd.DataFrame) -> pd.DataFrame:
 
        # Filter videos with any watch time
        videos_watched = (
            per_video[per_video["total_minutes"] > 0]
            .groupby("User ID")["Session ID"]
            .nunique()
            .rename("num_videos_watched")
        )

        # Total time watched per user
        total_time = (
            per_video.groupby("User ID")["total_minutes"]
            .sum()
            .rename("total_minutes")
        )

        # Repeated views per user (extra views beyond the first view)
        repeated_views = (
            per_video.assign(extra_views=lambda d: d["view_count"].clip(lower=1) - 1)
            .groupby("User ID")["extra_views"]
            .sum()
            .rename("repeated_views")
        )

        # Combine all features into one dataframe
        per_user = (
            pd.concat([videos_watched, total_time, repeated_views], axis=1)
            .fillna({"num_videos_watched": 0, "total_minutes": 0.0, "repeated_views": 0})
            .reset_index()
        )

        # Average minutes per video
        per_user["avg_minutes_per_video"] = per_user.apply(
            lambda r: r["total_minutes"] / r["num_videos_watched"]
            if r["num_videos_watched"] > 0
            else 0.0,
            axis=1,
        )

        return per_user

    # def summary_per_user_videolog(self, per_video: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        # -----------------------------
        # 1. Per-user summary
        # -----------------------------
        videos_watched = (
            per_video[per_video["total_minutes"] > 0]
            .groupby("User ID")["Session ID"]
            .nunique()
            .rename("num_unique_videos_watched")
        )

        total_time = (
            per_video.groupby("User ID")["total_minutes"]
            .sum()
            .rename("total_video_time_minutes")
        )

        repeated_views = (
            per_video.assign(extra_views=lambda d: d["view_count"].clip(lower=1) - 1)
            .groupby("User ID")["extra_views"]
            .sum()
            .rename("repeated_views_from_unique_video")
        )

        per_user = (
            pd.concat([videos_watched, total_time, repeated_views], axis=1)
            .fillna({"num_videos_watched": 0, "total_video_time_minutes": 0.0, "repeated_views": 0})
            .reset_index()
        )

        per_user["avg_minutes_per_video"] = per_user.apply(
            lambda r: r["total_video_time_minutes"] / r["num_videos_watched"]
            if r["num_videos_watched"] > 0
            else 0.0,
            axis=1,
        )

        # -----------------------------
        # 2. Per-user-per-video detail
        # -----------------------------
        per_user_video = (
            per_video.groupby(["User ID", "Session ID", "Session Name"], as_index=False)
            .agg(
                total_minutes=("total_minutes", "sum"),
                view_count=("view_count", "sum")
            )
            .sort_values(by=["User ID", "total_minutes"], ascending=[True, False])
            .reset_index(drop=True)
        )

        # -----------------------------
        # 3. Per-user-session summary (dictionary-like)
        # -----------------------------
        per_user_session_summary = (
            per_video.groupby(["User ID", "Session ID"], as_index=False)
            .agg(
                session_names=("Session Name", lambda x: list(x.unique())),  # list of session names
                total_minutes=("total_minutes", "sum"),
                session_count=("Session Name", "nunique")  # count of unique session names
            )
            .sort_values(by=["User ID", "total_minutes"], ascending=[True, False])
            .reset_index(drop=True)
        )

        return per_user, per_user_video, per_user_session_summary
    def summary_per_user_videolog(self, per_video: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        # -----------------------------
        # 1. Per-user summary
        # -----------------------------
        videos_watched = (
            per_video[per_video["total_minutes"] > 0]
            .groupby("User ID")["Session ID"]
            .nunique()
            .rename("unique_videos_watched")
        )

        total_time = (
            per_video.groupby("User ID")["total_minutes"]
            .sum()
            .rename("total_minutes")
        )

        repeated_views = (
            per_video.assign(extra_views=lambda d: d["view_count"].clip(lower=1) - 1)
            .groupby("User ID")["extra_views"]
            .sum()
            .rename("repeated_views_from_unique_video")
        )

        per_user = (
            pd.concat([videos_watched, total_time, repeated_views], axis=1)
            .fillna({"unique_videos_watched": 0, "total_minutes": 0.0, "repeated_views_from_unique_video": 0})
            .reset_index()
        )

        per_user["avg_minutes_per_video"] = per_user.apply(
            lambda r: r["total_minutes"] / r["unique_videos_watched"]
            if r["unique_videos_watched"] > 0
            else 0.0,
            axis=1,
        )

        # -----------------------------
        # 2. Per-user-per-video detail
        # -----------------------------
        per_user_video = (
            per_video.groupby(["User ID", "Session ID", "Session Name"], as_index=False)
            .agg(
                total_minutes=("total_minutes", "sum"),
                view_count=("view_count", "sum")
            )
            .sort_values(by=["User ID", "total_minutes"], ascending=[True, False])
            .reset_index(drop=True)
        )

        # -----------------------------
        # 3. Per-user-session summary (one row per user)
        # -----------------------------
        def session_dict(x):
            return dict(zip(x["Session ID"], x["Session Name"]))

        per_user_session_summary = (
            per_video.groupby("User ID")
            .agg(
                unique_session_ids=("Session ID", lambda x: list(x.unique())),
                # unique_session_names=("Session Name", lambda x: session_dict(per_video[per_video["User ID"] == x.name])),
                unique_session_names=("Session Name", lambda x: list(pd.unique(x))),
                unique_num_videos_watched=("Session ID", "nunique"),
                total_minutes_watched=("total_minutes", "sum")
            )
            .reset_index()
        )
    #     per_user_session_summary = (
    #     per_video.groupby("User ID").apply(
    #         lambda g: pd.Series({
    #             "unique_session_ids": list(g["Session ID"].unique()),
    #             "unique_session_names": session_dict(g),
    #             "unique_num_videos_watched": g["Session ID"].nunique(),
    #             "total_minutes_watched": g["total_minutes"].sum()
    #         })
    #     ).reset_index()
    # )

        return per_user, per_user_video, per_user_session_summary


########################## Reminder message funciton ##############################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################

    def remind_week_videowatch(self, week_info) -> str:

        # If DataFrame, take the first row
        if isinstance(week_info, pd.DataFrame):
            if week_info.shape[0] == 0:
                return "No data available for this week."
            # take the first row as a Series
            week_info = week_info.iloc[0]

        # Now week_info is a Series
        # Helper to extract scalar values from Series/dict
        def get_scalar(val):
            if hasattr(val, "item"):
                return val.item()
            elif isinstance(val, (dict, pd.Series)):
                return list(val.values())[0]
            return val

        # Extract scalars
        week = get_scalar(week_info["Week"])
        video_count = get_scalar(week_info["Video_Count"])

        # Convert video names and durations to plain lists
        video_name_list = week_info["Video_Name_List"]
        duration_list = week_info["Duration_List"]

        if isinstance(video_name_list, pd.Series):
            video_name_list = video_name_list.tolist()
        if isinstance(duration_list, pd.Series):
            duration_list = duration_list.tolist()

        # Ensure proper types
        video_name_list = [str(v) for v in video_name_list]
        duration_list = [float(d) for d in duration_list]

        # Total duration
        total_duration = sum(duration_list)

        # Build message per video
        video_messages = [f"{name} ({dur} min)" for name, dur in zip(video_name_list, duration_list)]
        videos_str = " and ".join(video_messages)

        # Final message
        message = (
            f"This is Week {week}, and there are {video_count} videos to watch: "
            f"{videos_str}. "
            f"Watching them will help you develop the course content and prepare for assignments. "
            f"Please watch them before starting this week’s course content and assignments."
        )

        print(message)
        return message



############# CALCULATE VIDEO ENGAGEMENT INDEX ##############################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


    def map_weekvideo_duration_log(self, df_weekvideo_duration, df_per_user_video):

        # --- Step 1: Copy per-user video DataFrame and select needed columns ---
        need_col = ['User ID', 'Session Name', 'total_minutes', 'view_count']
        df_user_with_duration = df_per_user_video.copy()[need_col]

        # --- Step 2: Rename total_minutes ---
        if 'total_minutes' in df_user_with_duration.columns:
            df_user_with_duration = df_user_with_duration.rename(
                columns={'total_minutes': 'student_watch_total_mins'}
            )

        # --- Step 3: Initialize new columns ---
        df_user_with_duration['video_duration'] = None
        df_user_with_duration['Week'] = None
        df_user_with_duration['video_importance'] = None  # new column

        # --- Step 4: Map Video Duration, Week, and video_importance ---
        if 'Video Name' in df_weekvideo_duration.columns:
            # Map Video Duration
            if 'Video Duration Minutes' in df_weekvideo_duration.columns:
                video_duration_map = pd.Series(
                    df_weekvideo_duration['Video Duration Minutes'].values,
                    index=df_weekvideo_duration['Video Name']
                ).to_dict()
                df_user_with_duration['video_duration'] = df_user_with_duration['Session Name'].map(video_duration_map)

            # Map Week
            if 'Week' in df_weekvideo_duration.columns:
                week_map = pd.Series(
                    df_weekvideo_duration['Week'].values,
                    index=df_weekvideo_duration['Video Name']
                ).to_dict()
                df_user_with_duration['Week'] = df_user_with_duration['Session Name'].map(week_map)

            # Map video_importance
            if 'video_importance' in df_weekvideo_duration.columns:
                video_importance_map = pd.Series(
                    df_weekvideo_duration['video_importance'].values,
                    index=df_weekvideo_duration['Video Name']
                ).to_dict()
                df_user_with_duration['video_importance'] = df_user_with_duration['Session Name'].map(video_importance_map)

        return df_user_with_duration



    def percentage_video_watch(self, df: pd.DataFrame) -> pd.DataFrame:

        df_result = df.copy()

        # Avoid division by zero
        df_result['percent_watch'] = df_result.apply(
            lambda row: row['student_watch_total_mins'] / row['video_duration']
            if row['video_duration'] and row['video_duration'] > 0 else 0,
            axis=1
        )

        # Optional: Cap at 1.0 (100%) if needed
        df_result['percent_watch'] = df_result['percent_watch'].clip(upper=1.0)

        return df_result
    

    def video_weight_importance(self,df):

        df = df.copy()
        
        # Compute total duration per week
        df['week_total_duration'] = df.groupby('Week')['Video Duration Minutes'].transform('sum')
        
        # Compute importance per video
        df['video_importance'] = df['Video Duration Minutes'] / df['week_total_duration']
        
        # Optional: drop intermediate column if you only want importance
        df.drop(columns=['week_total_duration'], inplace=True)
        
        return df

########## Manaully edit the video and duration ############################################################

    def search_nan_session(slef, df):

        # Filter rows where engagement_col is NaN
        nan_rows = df[df['video_engagement_indicator'].isna()]
        
        # Return list of session names
        return nan_rows['Session Name'].tolist()


    def edit_content_manually(self, df, video_name, week, video_duration):
  
        df_new = df.copy()
        
        # Ensure 'week' is stored as string to allow mixed types
        week_value = str(week) if isinstance(week, int) else week
        
        new_row = {
            'Video Name': video_name,
            'Week': week_value,
            'Video Duration Minutes': video_duration
        }
        
        # Append the new row
        df_new = pd.concat([df_new, pd.DataFrame([new_row])], ignore_index=True)
        
        return df_new








######################################################################

##### not sure is correct think on monday 
    def calculate_video_week_engagement(self, df):

        # Make a copy to avoid modifying original df
        df_new = df.copy()
        
        # Calculate engagement indicator
        df_new['video_engagement_indicator'] = df_new['video_importance'] * df_new['percent_watch']
        
        return df_new

    
    def calculate_user_engagement_indicator(self, df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()

        # Ensure numeric
        df_copy['video_importance'] = pd.to_numeric(df_copy['video_importance'], errors='coerce').fillna(0)
        df_copy['percent_watch'] = pd.to_numeric(df_copy['percent_watch'], errors='coerce').fillna(0)

        # Engagement per video
        df_copy['video_engagement_indicator'] = (
            df_copy['video_importance'] * df_copy['percent_watch']
        )

        # Aggregate per user: weighted sum / total importance
        result = (
            df_copy.groupby('User ID').apply(
                lambda g: g['video_engagement_indicator'].sum() / g['video_importance'].sum()
                if g['video_importance'].sum() > 0 else 0
            )
            .reset_index(name='user_engagement')
        )

        return result


    def trigger_userid_sent_reminder(self, df_week_summary: pd.DataFrame, df_with_engagement: pd.DataFrame, threshold: float = 0.3) -> tuple[pd.DataFrame, list]:

        df_copy = df_with_engagement.copy()
        reminder_video_message=self.remind_week_videowatch(df_week_summary)
        reminder_video_message

        # Build reminder message where condition is met
        def build_message(row):
            if row['user_engagement'] < threshold:
                return (
                    f"In terms of the record showing your video engagement score is "
                    f"{row['user_engagement']:.3f}, then we recommend and remind you "
                    f"to watch the video provided that helps you; "
                    f"{ reminder_video_message}"
                )
            else:
                return None

        df_copy['reminder_message'] = df_copy.apply(build_message, axis=1)

        # Filter triggered rows
        result = df_copy[df_copy['reminder_message'].notnull()].reset_index(drop=True)

        # Extract triggered user IDs
        triggered_userids = result['User ID'].tolist()

        return result, triggered_userids



########################## TEMP FUNCTION ##############################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


    def constraint_week_time(
        self,
        df: pd.DataFrame,
        tem_start: str,
        tem_end: str,
        date_format: str = "%d/%m/%Y",
        tz: str = "Australia/Adelaide"
    ) -> pd.DataFrame:


        # Ensure df[col_name] is datetime
        if not pd.api.types.is_datetime64_any_dtype(df["Timestamp"]):
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", utc=True)

        # Parse input dates
        start_date = pd.to_datetime(tem_start, format=date_format).tz_localize(tz)
        end_date = pd.to_datetime(tem_end, format=date_format).tz_localize(tz)

        # Align df timezone to match
        df["Timestamp"] = df["Timestamp"].dt.tz_convert(tz)

        # Filter inclusive range
        mask = (df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)
        return df.loc[mask].copy()
