"""Add resume-related tables

Revision ID: a97ec23ce5e9
Revises: 4001dd77727b
Create Date: 2025-06-20 16:28:34.439725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a97ec23ce5e9'
down_revision = '4001dd77727b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('resumes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('file_url', sa.String(length=255), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('extracted_text', sa.Text(), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('resume_job_matches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('resume_id', sa.Integer(), nullable=False),
    sa.Column('job_id', sa.Integer(), nullable=False),
    sa.Column('match_score', sa.Float(), nullable=True),
    sa.Column('match_summary', sa.Text(), nullable=True),
    sa.Column('matched_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
    sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('resume_scores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('resume_id', sa.Integer(), nullable=False),
    sa.Column('ai_model', sa.String(length=100), nullable=True),
    sa.Column('score_overall', sa.Float(), nullable=True),
    sa.Column('score_format', sa.Float(), nullable=True),
    sa.Column('score_skills', sa.Float(), nullable=True),
    sa.Column('score_experience', sa.Float(), nullable=True),
    sa.Column('strengths', sa.Text(), nullable=True),
    sa.Column('weaknesses', sa.Text(), nullable=True),
    sa.Column('suggestions', sa.Text(), nullable=True),
    sa.Column('evaluated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('resume_scores')
    op.drop_table('resume_job_matches')
    op.drop_table('resumes')
    # ### end Alembic commands ###
