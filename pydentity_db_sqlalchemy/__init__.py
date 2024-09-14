from pydenticore import DefaultPersonalDataProtector
from pydenticore.interfaces import IPersonalDataProtector
from pydenticore.utils import get_device_uuid

from pydentity_db_sqlalchemy.fields import ProtectedPersonalDataField

__all__ = ("use_personal_data_protector",)


def use_personal_data_protector(protector: IPersonalDataProtector | None = None) -> None:
    """
    Sets the ``IPersonalDataProtector`` for ``ProtectedPersonalDataField`` fields.
    When using the function, a protector will be installed,
    the data will be encrypted when writing and decrypted when receiving.
    If the value of protector is None, the default protector will be set.

    :param protector:
    :return:
    """
    ProtectedPersonalDataField.protector = protector or DefaultPersonalDataProtector(
        "ProtectedPersonalDataField",
        get_device_uuid()
    )
