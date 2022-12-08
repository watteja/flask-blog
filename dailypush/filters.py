from flask import (
    Blueprint,
)

bp = Blueprint("filters", __name__)

@bp.app_template_filter("format_datetime")
def format_datetime_filter(dt):
    """
    Format datetime for post headers.
    
    As of transitioning to Moment.js for date formatting, this filter is unused.
    I'm retaining it here as an example of a custom filter.

    Example usage in a template:
    {{ post.created | format_datetime }}
    """
    return dt.strftime("%A, %d %B %Y, %H:%M UTC")
