def get_allowed_actions(role, actions):
    role = role.lower()
    return [a for a in actions if role in [r.lower() for r in a["role_access"]]]
