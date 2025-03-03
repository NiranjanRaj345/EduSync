"""Initial schema with faculty assignment

Revision ID: 3060e60cf56b
Revises: 
Create Date: 2025-02-28 17:34:31.585423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3060e60cf56b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assigned_faculty_id', sa.Integer(), nullable=False))
        batch_op.alter_column('file_path',
               existing_type=sa.VARCHAR(length=512),
               nullable=False)
        batch_op.create_foreign_key(None, 'user', ['assigned_faculty_id'], ['id'])
        batch_op.drop_column('review_file1_drive_id')
        batch_op.drop_column('gdrive_review1_id')
        batch_op.drop_column('gdrive_review1_link')
        batch_op.drop_column('gdrive_file_id')
        batch_op.drop_column('drive_file_id')
        batch_op.drop_column('review_file2_drive_id')
        batch_op.drop_column('review_file2_web_link')
        batch_op.drop_column('gdrive_review2_link')
        batch_op.drop_column('review_file1_web_link')
        batch_op.drop_column('drive_web_link')
        batch_op.drop_column('gdrive_view_link')
        batch_op.drop_column('gdrive_review2_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gdrive_review2_id', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('gdrive_view_link', sa.VARCHAR(length=512), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('drive_web_link', sa.VARCHAR(length=512), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('review_file1_web_link', sa.VARCHAR(length=512), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('gdrive_review2_link', sa.VARCHAR(length=512), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('review_file2_web_link', sa.VARCHAR(length=512), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('review_file2_drive_id', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('drive_file_id', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('gdrive_file_id', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('gdrive_review1_link', sa.VARCHAR(length=512), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('gdrive_review1_id', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('review_file1_drive_id', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('file_path',
               existing_type=sa.VARCHAR(length=512),
               nullable=True)
        batch_op.drop_column('assigned_faculty_id')

    # ### end Alembic commands ###
