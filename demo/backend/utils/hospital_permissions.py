"""医院场景权限与数据范围辅助函数。"""

from models import BPatient, User


HEALTH_MANAGER_ROLES = {'health_manager', 'doctor_assistant'}
DOCTOR_ROLES = {'doctor'}
DIRECTOR_ROLES = {'department_director'}
ADMIN_ROLES = {'admin', 'system_admin'}


def role_of(user):
    return (getattr(user, 'role', None) or '').strip()


def is_admin(user):
    return role_of(user) in ADMIN_ROLES


def is_health_operator(user):
    return role_of(user) in HEALTH_MANAGER_ROLES


def is_doctor(user):
    return role_of(user) in DOCTOR_ROLES


def is_department_director(user):
    return role_of(user) in DIRECTOR_ROLES


def can_operate_patient(user):
    return is_admin(user) or is_health_operator(user)


def apply_patient_scope(query, user):
    """按当前用户角色过滤患者查询范围。"""
    if not user:
        return query.filter(False)

    if is_admin(user):
        return query

    if is_doctor(user):
        return query.filter(BPatient.primary_doctor_id == user.id)

    if is_department_director(user):
        department_id = getattr(user, 'department_id', None)
        if not department_id:
            return query.filter(False)
        return query.filter(BPatient.department_id == department_id)

    # 兼容旧账号：未配置新角色时，默认按健康管理师的数据范围处理。
    return query.filter(BPatient.manager_id == user.id)


def can_view_patient(user, patient):
    if not user or not patient:
        return False
    if is_admin(user):
        return True
    if is_doctor(user):
        return patient.primary_doctor_id == user.id
    if is_department_director(user):
        return bool(user.department_id) and patient.department_id == user.department_id
    return patient.manager_id == user.id


def require_patient_visible(user, patient):
    if not can_view_patient(user, patient):
        return False
    return True


def doctor_query():
    return User.query.filter(User.role == 'doctor', User.is_active.is_(True))
