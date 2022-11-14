from flask import (
    Blueprint,
)

bp = Blueprint("filters", __name__)

@bp.app_template_filter("format_datetime")
def format_datetime_filter(dt):
    """Format datetime for post headers."""
    return dt.strftime("%A, %d %B %Y, %H:%M UTC")
