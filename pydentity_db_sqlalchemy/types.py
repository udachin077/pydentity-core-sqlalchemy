from typing import Optional

import sqlalchemy as sa
from pydentity.abc import IPersonalDataProtector


class ProtectedPersonalData(sa.TypeDecorator):
    impl = sa.String
    cache_ok = True

    protector: Optional[IPersonalDataProtector] = None

    def process_bind_param(self, value, dialect):
        if value and self.protector:
            value = self.protector.protect(value)
        return value

    def process_result_value(self, value, dialect):
        if value and self.protector:
            value = self.protector.unprotect(value)
        return value
