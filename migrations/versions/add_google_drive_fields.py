"""Add Google Drive fields

Revision ID: 3a9ccf19cc14
Revises: b1241bb98fe4
Create Date: 2025-02-28 10:43:49.174531

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3a9ccf19cc14'
down_revision = 'b1241bb98fe4'
branch_labels = None
depends_on = None

def upgrade():
    # Make file_path nullable for existing documents
    op.alter_column('document', 'file_path',
                    existing_type=sa.String(length=512),
                    nullable=True)

    # Add Google Drive fields for documents
    op.add_column('document', sa.Column('drive_file_id', sa.String(length=100), nullable=True))
    op.add_column('document', sa.Column('drive_web_link', sa.String(length=512), nullable=True))
    
    # Add Google Drive fields for reviews
    op.add_column('document', sa.Column('review_file1_drive_id', sa.String(length=100), nullable=True))
    op.add_column('document', sa.Column('review_file1_web_link', sa.String(length=512), nullable=True))
    op.add_column('document', sa.Column('review_file2_drive_id', sa.String(length=100), nullable=True))
    op.add_column('document', sa.Column('review_file2_web_link', sa.String(length=512), nullable=True))

def downgrade():
    # Remove Google Drive fields for reviews
    op.drop_column('document', 'review_file2_web_link')
    op.drop_column('document', 'review_file2_drive_id')
    op.drop_column('document', 'review_file1_web_link')
    op.drop_column('document', 'review_file1_drive_id')
    
    # Remove Google Drive fields for documents
    op.drop_column('document', 'drive_web_link')
    op.drop_column('document', 'drive_file_id')
    
    # Make file_path non-nullable again
    op.alter_column('document', 'file_path',
                    existing_type=sa.String(length=512),
                    nullable=False)
