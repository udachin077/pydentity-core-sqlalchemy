import sqlalchemy as sa
from pydenticore.interfaces import IPersonalDataProtector


class ProtectedPersonalDataField(sa.TypeDecorator):
    impl = sa.String
    cache_ok = True

    protector: IPersonalDataProtector | None = None

    def process_bind_param(self, value, dialect):
        if value and self.protector:
            value = self.protector.protect(value)
        return value

    def process_result_value(self, value, dialect):
        if value and self.protector:
            value = self.protector.unprotect(value)
        return value
