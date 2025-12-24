from django.db.backends.base.features import BaseDatabaseFeatures


class DatabaseFeatures(BaseDatabaseFeatures):
    # Does the backend support partial indexes (CREATE INDEX ... WHERE ...)?
    supports_partial_indexes = False
    supports_functions_in_partial_indexes = False

    # Does the backend support indexes on expressions?
    supports_expression_indexes = False

    supports_foreign_keys = False
    supports_comments = False

    can_rollback_ddl = False
    can_return_columns_from_insert = True

    # We set it as True so we can use GeneratedFields, but
    # we ignore it at sql creation time.
    supports_virtual_generated_columns = True

    def supports_transactions(self):
        return False
