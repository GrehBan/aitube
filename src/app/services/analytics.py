# File: src/app/services/analytics.py
# Description: Analytics using Polars (Requirement C5)

import polars as pl
from typing import List

def analyze_view_metrics(view_data: List[dict]):
    """
    Process raw view event logs using Polars.
    Expects list of dicts: {'video_id': str, 'watch_time': float, 'timestamp': datetime}
    """
    df = pl.DataFrame(view_data)
    
    # Calculate average watch time per video
    stats = df.group_by("video_id").agg([
        pl.col("watch_time").mean().alias("avg_watch_time"),
        pl.count("timestamp").alias("view_count")
    ])
    
    return stats.to_dicts()