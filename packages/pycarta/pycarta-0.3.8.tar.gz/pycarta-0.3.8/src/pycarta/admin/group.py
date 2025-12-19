from ..auth.agent import CartaAgent
from ..exceptions import InvalidParameterException
from .types import Group, User


def create_group(group: Group, *, exists_ok: bool=False, agent: None | CartaAgent=None) -> None:
    if not agent:
        from pycarta import get_agent
    try:
        agent = agent or get_agent()
        agent.post(f"user/group/{str(group)}")
    except InvalidParameterException as error:
        if exists_ok:
            return
        raise error

def add_user_to_group(
    add_user: User,
    group: Group,
    create_if_not_exists=False,
    *,
    agent: None | CartaAgent=None
) -> None:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    try:
        response = agent.post(f"user/group/{str(group)}/{add_user.name}")
    except InvalidParameterException as error:  # pragma: no cover
        if create_if_not_exists:
            create_group(group)
            # If this fails, something else was wrong with the request
            add_user_to_group(add_user, group, create_if_not_exists=False)
            return
        raise error

def list_members(group: str | Group, *, agent: None | CartaAgent=None) -> list[User]:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.get(f"user/group/{str(group)}")
    users = response.json()
    return [User(**user) for user in users]


def is_user_in_group(
    user: User,
    candidate_group: str | Group,
    *,
    agent: None | CartaAgent=None
) -> bool:
    """Check if a user belongs to a group.

    Args:
        user: The user to check membership for
        candidate_group: The group to check (can be a Group object or string like "org:name")
        agent: Optional CartaAgent for authentication

    Returns:
        True if the user is a member of the group, False otherwise
    """
    # Fast path: check user.groups if populated
    if user.groups is not None:
        group_names = [str(g) for g in user.groups]
        return str(candidate_group) in group_names

    # Fallback: query API
    members = list_members(candidate_group, agent=agent)
    return user in members
