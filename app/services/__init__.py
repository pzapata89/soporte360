from .user_service import (
    get_user_by_email,
    get_user_by_id,
    get_users,
    create_user,
    create_users_bulk,
    update_user,
    activate_user,
    deactivate_user,
    get_active_technicians
)
from .category_service import (
    get_category_by_id,
    get_category_by_name,
    get_categories,
    create_category,
    update_category
)
from .ticket_service import (
    get_ticket_by_id,
    get_ticket_by_code,
    get_tickets,
    count_open_tickets_for_technician,
    find_best_technician,
    create_ticket,
    update_ticket,
    update_ticket_status,
    assign_ticket,
    create_comment,
    get_comments_by_ticket,
    create_history_entry,
    get_history_by_ticket
)
from .report_service import (
    get_general_report,
    get_category_report,
    get_technician_report
)
