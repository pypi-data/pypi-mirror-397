import requests

def send_email_no_attachment(p, endpoint_url=None, access_token=None):
    """
    Send email without attachment via a simple POST API.

    Parameters:
        p (dict): {
            "to": str | list[str],
            "subject": str,
            "body": str,
            "headers": dict (optional),
            "timeout": int (optional)
        }
        endpoint_url (str): API endpoint for sending mail.
        access_token (str): Bearer token for authentication.

    Returns:
        (status_code, response_text) on success
        (None, error_message) on failure
    """

    # Validate required config
    if not endpoint_url:
        raise ValueError("endpoint_url is required")

    if not access_token:
        raise ValueError("access_token is required")

    # Required email fields
    missing = [k for k in ("to", "subject", "body") if not p.get(k)]
    if missing:
        return None, f"Missing required fields: {', '.join(missing)}"

    # Normalize payload
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
        print(f"Email send: {'✅ Success' if resp.status_code in success_codes else f'❌ Failed ({resp.status_code})'}")

        return resp.status_code, resp.text

    except requests.RequestException as e:
        msg = f"Request failed: {e}"
        print(f"{msg}")
        return None, msg
