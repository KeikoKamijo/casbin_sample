from .users import (
    get_password_hash,
    verify_password,
    get_user,
    get_user_by_username,
    get_user_by_email,
    get_users,
    create_user,
    update_user,
    delete_user,
    get_users_by_corporation
)

from .corporations import (
    get_corporation,
    get_corporation_by_name,
    get_corporation_by_code,
    get_corporations,
    create_corporation,
    update_corporation,
    delete_corporation
)

from .shops import (
    get_shop,
    get_shops,
    create_shop,
    update_shop,
    delete_shop,
    get_shops_by_corporation,
    add_shop_to_corporation,
    remove_shop_from_corporation
)

from .inquiries import (
    get_inquiry,
    get_inquiries,
    get_inquiries_by_user,
    get_inquiries_assigned_to_user,
    get_inquiries_by_corporation,
    create_inquiry,
    update_inquiry,
    assign_inquiry,
    update_inquiry_status,
    delete_inquiry
)

from .roles import (
    get_role,
    get_roles,
    create_role,
    update_role,
    delete_role,
    get_role_permissions,
    add_role_permission,
    remove_role_permission,
    get_user_roles,
    assign_user_role,
    unassign_user_role
)

__all__ = [
    # Users
    "get_password_hash", "verify_password", "get_user", "get_user_by_username", "get_user_by_email",
    "get_users", "create_user", "update_user", "delete_user", "get_users_by_corporation",
    # Corporations
    "get_corporation", "get_corporation_by_name", "get_corporation_by_code",
    "get_corporations", "create_corporation", "update_corporation", "delete_corporation",
    # Shops
    "get_shop", "get_shops", "create_shop", "update_shop",
    "delete_shop", "get_shops_by_corporation", "add_shop_to_corporation",
    "remove_shop_from_corporation",
    # Inquiries
    "get_inquiry", "get_inquiries", "get_inquiries_by_user", "get_inquiries_assigned_to_user",
    "get_inquiries_by_corporation", "create_inquiry",
    "update_inquiry", "assign_inquiry", "update_inquiry_status", "delete_inquiry",
    # Roles
    "get_role", "get_roles", "create_role", "update_role", "delete_role",
    "get_role_permissions", "add_role_permission", "remove_role_permission",
    "get_user_roles", "assign_user_role", "unassign_user_role"
]