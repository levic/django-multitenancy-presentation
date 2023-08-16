from django.db import migrations
from django.db import models
from django.db.migrations.operations.base import Operation


class EnableRowLevelSecurity(Operation):
    reversible = True

    model: models.Model
    tenant_id_field: str

    def __init__(self, model: models.Model, tenant_id_field: str):
        super().__init__()
        self.model = model
        self.tenant_id_field = tenant_id_field

    def state_forwards(self, app_label, state):
        # Sanity-check that the model & field actually exist
        try:
            model = state.apps.get_model(app_label, self.model)
        except LookupError:
            raise ValueError(f"{app_label}.{self.model} does not exist")

        # the RLS code here is only built to handle integer fields
        field = model._meta.get_field(self.tenant_id_field)
        if isinstance(field, models.ForeignKey):
            field = field.target_field

        if not isinstance(field, (models.AutoField, models.IntegerField)):
            raise ValueError(f"{type(self)} doesn't know how to handle field type {type(field)}")

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model)
        field = model._meta.get_field(self.tenant_id_field)
        table_name = model._meta.db_table
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")

            # we need the FORCE so that the table owner is subject to RLS
            # note that users with SUPERUSER will still bypass RLS
            schema_editor.execute(f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY")

            sql = f"""
                CREATE POLICY {table_name}__policy
                    ON {table_name} USING (
                        CASE
                            WHEN
                                CURRENT_SETTING(%(setting)s, TRUE) IS NULL
                                OR CURRENT_SETTING(%(setting)s, TRUE) = ''
                            THEN
                                TRUE
                            ELSE
                                {self.tenant_id_field} = CURRENT_SETTING(%(setting)s)::INT
                        END
                    );
            """
            params = {
                "setting": "django.tenant_id",
            }
            schema_editor.execute(sql, params)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model)
        field = model._meta.get_field(self.tenant_id_field)
        table_name = model._meta.db_table
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute(f"DROP POLICY {table_name}__policy ON {table_name}")
            schema_editor.execute(f"ALTER TABLE {table_name} NO FORCE ROW LEVEL SECURITY")
            schema_editor.execute(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY")

    def describe(self):
        # This is used to describe what the operation does in console output.
        return f"Enable Row-Level Security on {self.model}"


class Migration(migrations.Migration):
    dependencies = [
        ("singleschema", "0001_initial"),
    ]

    operations = [
        EnableRowLevelSecurity(model="account", tenant_id_field="id"),
        EnableRowLevelSecurity(model="user", tenant_id_field="account_id"),
        EnableRowLevelSecurity(model="project", tenant_id_field="account_id"),
        EnableRowLevelSecurity(model="task", tenant_id_field="account_id"),
        EnableRowLevelSecurity(model="subtask", tenant_id_field="account_id"),
    ]
