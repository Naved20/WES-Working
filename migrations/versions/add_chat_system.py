"""Add chat system tables

Revision ID: chat_system_001
Revises: 
Create Date: 2024-01-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'chat_system_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create chat_conversations table
    op.create_table(
        'chat_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_type', sa.String(length=20), nullable=False, server_default='direct'),
        sa.Column('participant1_id', sa.Integer(), nullable=False),
        sa.Column('participant2_id', sa.Integer(), nullable=False),
        sa.Column('group_name', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['participant1_id'], ['signup_details.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant2_id'], ['signup_details.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('participant1_id', 'participant2_id', name='uq_chat_participants')
    )
    
    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['chat_conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['signup_details.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('idx_chat_messages_conversation', 'chat_messages', ['conversation_id'])
    op.create_index('idx_chat_messages_sender', 'chat_messages', ['sender_id'])
    op.create_index('idx_chat_messages_created', 'chat_messages', ['created_at'])
    op.create_index('idx_chat_conversations_p1', 'chat_conversations', ['participant1_id'])
    op.create_index('idx_chat_conversations_p2', 'chat_conversations', ['participant2_id'])


def downgrade():
    op.drop_index('idx_chat_conversations_p2')
    op.drop_index('idx_chat_conversations_p1')
    op.drop_index('idx_chat_messages_created')
    op.drop_index('idx_chat_messages_sender')
    op.drop_index('idx_chat_messages_conversation')
    op.drop_table('chat_messages')
    op.drop_table('chat_conversations')
