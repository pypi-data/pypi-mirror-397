def maybe_sample(df, max_rows=200_000, random_state=42):
    if len(df) > max_rows:
        return df.sample(max_rows, random_state=random_state), True
    return df, False
