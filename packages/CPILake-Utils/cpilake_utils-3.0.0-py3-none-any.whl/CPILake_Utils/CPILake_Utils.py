import re
import requests
from typing import Optional, List, Dict, Tuple, Union
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

def hash_function(s):
    """Hash function for alphanumeric strings"""
    if s is None:
        return None
    s = str(s).upper()
    s = re.sub(r'[^A-Z0-9]', '', s)
    base36_map = {ch: idx for idx, ch in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
    result = 0
    for i, ch in enumerate(reversed(s)):
        result += base36_map.get(ch, 0) * (36 ** i)
    result += len(s) * (36 ** (len(s) + 1))
    return result


def send_email_no_attachment(p, endpoint_url=None, access_token=None):
    """
    Send email via POST API without attachment.

    Parameters:
        p (dict): {
            "to": str | list[str],
            "subject": str,
            "body": str,
            "headers": dict (optional),
            "timeout": int (optional)
        }
        endpoint_url (str): API endpoint for sending mail
        access_token (str): Bearer token

    Returns:
        (status_code, response_text) or (None, error_message)
    """
    if not endpoint_url:
        raise ValueError("endpoint_url is required")
    if not access_token:
        raise ValueError("access_token is required")

    missing = [k for k in ("to", "subject", "body") if not p.get(k)]
    if missing:
        return None, f"Missing required fields: {', '.join(missing)}"

    payload = {
        "to": ";".join(p["to"]) if isinstance(p["to"], list) else p["to"],
        "subject": p["subject"],
        "body": p["body"],
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        **p.get("headers", {})
    }

    try:
        resp = requests.post(
            endpoint_url,
            json=payload,
            headers=headers,
            timeout=p.get("timeout", 15)
        )
        success_codes = (200, 201, 202)
        return resp.status_code, resp.text
    except requests.RequestException as e:
        return None, str(e)


def send_email_no_attachment_01(
    body        : Optional[str]             = None,
    endpoint_url: Optional[str]             = None,
    access_token: Optional[str]             = None,
    subject     : Optional[str]             = None,
    recipients  : Optional[List[str]]       = None,
    headers     : Optional[Dict[str, str]]  = None,
    timeout     : int                       = 15,
    tz_name     : str                       = "America/Los_Angeles"
) -> Tuple[Optional[int], str]:
    """
    Send email via POST API without attachments. All parameters are optional.
    If required information is missing, returns a descriptive message instead of sending.
    """
    # If endpoint or token not provided, skip sending
    if not endpoint_url or not access_token:
        return None, "Skipping send: endpoint_url or access_token not provided."

    # Determine recipients
    final_recipients = recipients
    if not final_recipients:
        return None, "Skipping send: no recipients provided."

    # Determine body content
    final_body = body
    if not final_body:
        return None, "Skipping send: no body content provided."

    payload = {
        "to": ";".join(final_recipients) if isinstance(final_recipients, list) else final_recipients,
        "subject": subject or "",
        "body": final_body
    }

    request_headers = {
        "Authorization": f"Bearer {access_token}",
        **(headers or {})
    }

    try:
        resp = requests.post(
            endpoint_url,
            json=payload,
            headers=request_headers,
            timeout=timeout
        )
        if resp.status_code in (200, 201, 202):
            return resp.status_code, resp.text
        else:
            return resp.status_code, f"Failed: {resp.text}"
    except requests.RequestException as e:
        return None, str(e)



def QA_CheckUtil(
    source_df: DataFrame,
    qa_df: DataFrame
) -> DataFrame:

    spark = source_df.sparkSession
    qa_rows: List[tuple] = []

    def calc_diff(src: Optional[Union[int, float]], qa: Optional[Union[int, float]]) -> Optional[float]:
        if src is None or qa is None:
            return None
        return float(src) - float(qa)

    # Row count
    src_count = float(source_df.count())
    qa_count = float(qa_df.count())
    qa_rows.append((
        "ROW_COUNT",
        "row_count",
        None,
        src_count,
        qa_count,
        calc_diff(src_count, qa_count),
        src_count == qa_count
    ))

    # Null check
    common_cols = set(source_df.columns).intersection(set(qa_df.columns))
    for col in common_cols:
        src_nulls = float(source_df.filter(F.col(col).isNull()).count())
        qa_nulls = float(qa_df.filter(F.col(col).isNull()).count())
        qa_rows.append((
            "NULL_CHECK",
            "null_count",
            col,
            src_nulls,
            qa_nulls,
            calc_diff(src_nulls, qa_nulls),
            src_nulls == qa_nulls
        ))

    # Aggregation check (SUM for amount)
    if "amount" in source_df.columns and "amount" in qa_df.columns:
        src_sum = float(source_df.select(F.sum("amount")).collect()[0][0] or 0.0)
        qa_sum = float(qa_df.select(F.sum("amount")).collect()[0][0] or 0.0)
        qa_rows.append((
            "AGG_CHECK",
            "sum",
            "amount",
            src_sum,
            qa_sum,
            calc_diff(src_sum, qa_sum),
            src_sum == qa_sum
        ))

    # Duplicate check on id column
    if "id" in source_df.columns and "id" in qa_df.columns:
        src_dupes = float(source_df.count() - source_df.select("id").distinct().count())
        qa_dupes = float(qa_df.count() - qa_df.select("id").distinct().count())
        qa_rows.append((
            "DUPLICATE_CHECK",
            "duplicate_id",
            "id",
            src_dupes,
            qa_dupes,
            calc_diff(src_dupes, qa_dupes),
            src_dupes == qa_dupes
        ))

    # Create final QA DataFrame
    qa_df_result = spark.createDataFrame(
        qa_rows,
        [
            "check_type",
            "check_name",
            "column_name",
            "source_value",
            "qa_value",
            "diff",
            "match"
        ]
    )
    return qa_df_result