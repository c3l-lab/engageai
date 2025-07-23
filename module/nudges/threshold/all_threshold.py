
################################################ Submission Index Score ##########################################################################################

def return_userid_sub_threshold(df, sub_threshold: 0.02):

    df_filtered = df[df['submission_score'] > sub_threshold]
    return df_filtered['userid'].tolist()


################################################ Time On Task Index Score ##########################################################################################

