from typing import override

import sqlalchemy as sa
from pydenticore.interfaces import IPersonalDataProtector


class ProtectedPersonalDataField(sa.TypeDecorator):
    """A variably sized protected string type.

    If a protector is installed, the data will be encrypted when writing and decrypted when receiving.
    """
    impl = sa.String
    cache_ok = True

    protector: IPersonalDataProtector | None = None

    @override
    def process_bind_param(self, value, dialect):
        if value and self.protector:
            value = self.protector.protect(value)
        return value

    @override
    def process_result_value(self, value, dialect):
        if value and self.protector:
            value = self.protector.unprotect(value)
        return value
