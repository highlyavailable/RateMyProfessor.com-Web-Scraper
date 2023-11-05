import pandas

rmp_df = pandas.read_csv(
    "../static_data/alaskapacificuniversity_professors.csv")
print(rmp_df.head(5))

# Average level of difficulty per department
rmp_dept_df = rmp_df.groupby(by=["department"],
                             as_index=True)["level_of_difficulty"].mean()
print(rmp_dept_df)

# Average chance a student will retake the course per department
rm_dept_ta_df = rmp_df.dropna(subset=["would_take_again_pct"])
rm_dept_ta_df["would_take_again_pct"] = rm_dept_ta_df["would_take_again_pct"].str.replace(
    '%', '')
rm_dept_ta_df["would_take_again_pct"] = rm_dept_ta_df[
    "would_take_again_pct"].apply(lambda x: float(x))
rm_dept_ta_df["would_take_again_pct"] = rm_dept_ta_df[
    "would_take_again_pct"] / 100.0
rmp_dept_df = rm_dept_ta_df.groupby(by=["department"],
                                    as_index=True)["would_take_again_pct"].mean().round(2)
print(rmp_dept_df)
