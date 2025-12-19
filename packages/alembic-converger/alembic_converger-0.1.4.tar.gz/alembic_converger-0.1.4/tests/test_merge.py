"""
Tests for merge module.
"""


from alembic_converger.merge import has_schema_operations


class TestSchemaOperationDetection:
    """Test detection of schema operations in migration files."""

    def test_clean_merge_no_operations(self):
        """Test that clean merge with only 'pass' is detected correctly."""
        content = """
\"\"\"Merge heads.\"\"\"
revision = 'abc123'
down_revision = ('def456', 'ghi789')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
"""
        assert has_schema_operations(content) is False

    def test_detects_create_table(self):
        """Test detection of create_table operation."""
        content = """
def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True)
    )

def downgrade():
    op.drop_table('users')
"""
        assert has_schema_operations(content) is True

    def test_detects_add_column(self):
        """Test detection of add_column operation."""
        content = """
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255)))

def downgrade():
    pass
"""
        assert has_schema_operations(content) is True

    def test_detects_alter_column(self):
        """Test detection of alter_column operation."""
        content = """
def upgrade():
    op.alter_column('users', 'name', nullable=False)

def downgrade():
    pass
"""
        assert has_schema_operations(content) is True

    def test_detects_execute(self):
        """Test detection of execute operation."""
        content = """
def upgrade():
    op.execute('ALTER TABLE users ADD CONSTRAINT...')

def downgrade():
    pass
"""
        assert has_schema_operations(content) is True

    def test_ignores_comments(self):
        """Test that comments mentioning operations are ignored."""
        content = """
def upgrade():
    # op.create_table - this is just a comment
    pass

def downgrade():
    pass
"""
        assert has_schema_operations(content) is False

    def test_upgrade_with_docstring(self):
        """Test that docstrings don't trigger false positives."""
        content = """
def upgrade():
    \"\"\"Merge heads without schema changes.\"\"\"
    pass

def downgrade():
    \"\"\"Downgrade merge.\"\"\"
    pass
"""
        assert has_schema_operations(content) is False
