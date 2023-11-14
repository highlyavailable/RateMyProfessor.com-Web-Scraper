import pandas
pandas.options.mode.chained_assignment = None

def rmp_stats(file_path,school_name):
    rmp_df = pandas.read_csv(
    file_path)

    print(f"\n\n>>> Statistics for {school_name}")
    # Average level of difficulty per department
    print("\nAverage Rating per department")
    rmp_rating_dept_df = rmp_df.groupby(by=["department"],
                                as_index=True)[
                                    "rating"
                                    ].mean().round(2).apply(lambda x: str(x) + "/5")
    print(rmp_rating_dept_df.to_string( header=False))

    # Average level of difficulty per department
    print("\nAverage level of difficulty per department")
    rmp_dept_df = rmp_df.groupby(by=["department"],
                                as_index=True)[
                                    "level_of_difficulty"
                                    ].mean().round(2).apply(lambda x: str(x) + "/5")
    print(rmp_dept_df.to_string( header=False))

    # Average chance a student will retake the course per department
    rm_dept_ta_df = rmp_df.dropna(subset=["would_take_again_pct"])
    rm_dept_ta_df["would_take_again_pct"] = rm_dept_ta_df["would_take_again_pct"].apply(lambda x: x.replace( '%', ''))
    rm_dept_ta_df["would_take_again_pct"] = rm_dept_ta_df[
    "would_take_again_pct"].apply(lambda x: float(x))
    rm_dept_ta_df["would_take_again_pct"] = rm_dept_ta_df[
    "would_take_again_pct"] / 100.0
    rmp_dept_df = rm_dept_ta_df.groupby(by=["department"],
                                    as_index=True)[
                                    "would_take_again_pct"
                                    ].mean().round(2).apply(
                                    lambda x: x*100.0).apply(
                                    lambda x: str(x) + "%")
    print(
    f"\n% of students who would retake a professor's course, by department: \n{rmp_dept_df.to_string( header=False)}")


