def load_to_snowflake(
    session,
    dataframe,
    table_name,
):
    snowpark_df = session.create_dataframe(dataframe)

    snowpark_df.write.mode(
        "overwrite"
    ).save_as_table(table_name)

    print(
        f"Loaded {dataframe.shape[0]} rows "
        f"into {table_name}"
    )