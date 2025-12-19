from pycarta.admin.types import UserType, PermissionsRole

from . import CARTA_FS_SERVICE_PATH
from .types.configuration import ProjectConfiguration, Configuration, ProjectFiles
from .. import CartaAgent


def get_configuration(project: str, agent: CartaAgent = None):
    """Get project's Carta FS configuration"""
    if not agent:
        from pycarta import get_agent
        agent = get_agent()

    response = (
        agent.get(CARTA_FS_SERVICE_PATH + f'/config/{project}')
    )

    resp_json = response.json()

    return ProjectConfiguration(**resp_json)


def initialize_project(project: str, storage_backend: str = "", agent: CartaAgent = None):
    """Initialize a project in Carta FS"""
    if not agent:
        from pycarta import get_agent
        agent = get_agent()

    config_response = agent.post(CARTA_FS_SERVICE_PATH + f'/config/{project}', json={
        "storageBackend": storage_backend
    })

    return ProjectConfiguration(**config_response.json())


def change_storage_backend(project: str, storage_backend: str = "", agent: CartaAgent = None):
    """
    Change a project's storage

    This only effects future uploaded files, not existing files.
    """
    if not agent:
        from pycarta import get_agent
        agent = get_agent()

    config_response = agent.put(CARTA_FS_SERVICE_PATH + f'/config/{project}', json={
        "storageBackend": storage_backend
    })

    return ProjectConfiguration(**config_response.json())


def get_project_files(project: str, agent: CartaAgent = None):
    """
    Get the list of files associated with this project in Carta FS
    """
    if not agent:
        from pycarta import get_agent
        agent = get_agent()

    config_response = agent.get(CARTA_FS_SERVICE_PATH + f'/config/{project}/files')

    return ProjectFiles(**config_response.json())


def set_file_permission(
        project: str, entity: str, user_type: UserType, permission_role: PermissionsRole, agent: CartaAgent = None):
    """
    Add or modify a permission entity's default permission for a file in Carta FS

    This only effects future uploaded files, not existing files.
    """
    if not agent:
        from pycarta import get_agent
        agent = get_agent()

    config_response = agent.post(CARTA_FS_SERVICE_PATH + f'/config/{project}/permissions/{entity}', json={
        "userType": user_type.value,
        "permissionLevel": permission_role.value
    })

    return ProjectConfiguration(**config_response.json())


def remove_file_permission(project: str, entity: str, agent: CartaAgent = None):
    """
    Remove a permission entity's default permission for a file in Carta FS

    This only effects future uploaded files, not existing files.
    """
    if not agent:
        from pycarta import get_agent
        agent = get_agent()

    config_response = agent.delete(CARTA_FS_SERVICE_PATH + f'/config/{project}/permissions/{entity}')

    return ProjectConfiguration(**config_response.json())

