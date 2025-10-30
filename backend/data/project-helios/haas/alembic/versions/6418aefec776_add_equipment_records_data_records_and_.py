"""Add equipment_records, data_records, and crawler_data tables

Revision ID: 6418aefec776
Revises: 461fa80683d2
Create Date: 2025-10-23 01:52:54.755028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6418aefec776'
down_revision: Union[str, Sequence[str], None] = '461fa80683d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create equipment_records table
    op.create_table('equipment_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('categoria', sa.String(length=255), nullable=False),
        sa.Column('fabricante', sa.String(length=255), nullable=False),
        sa.Column('modelo', sa.String(length=255), nullable=False),
        sa.Column('familia', sa.String(length=255), nullable=True),
        sa.Column('normas_ensaios', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ocp', sa.String(length=255), nullable=True),
        sa.Column('certificado_numero', sa.String(length=255), nullable=True),
        sa.Column('registro_inmetro', sa.String(length=255), nullable=True),
        sa.Column('laboratorio_ensaio', sa.String(length=255), nullable=True),
        sa.Column('data_emissao', sa.Date(), nullable=True),
        sa.Column('data_validade', sa.Date(), nullable=True),
        sa.Column('atributos_tecnicos', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('arquivos_datasheet', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('raw_payload', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('fonte', sa.String(length=50), nullable=False),
        sa.Column('ultima_atualizacao', sa.DateTime(), nullable=False),
        sa.Column('responsavel', sa.String(length=255), nullable=True),
        sa.Column('extra_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_equipment_records_categoria'), 'equipment_records', ['categoria'], unique=False)
    op.create_index(op.f('ix_equipment_records_certificado_numero'), 'equipment_records', ['certificado_numero'], unique=False)
    op.create_index(op.f('ix_equipment_records_fabricante'), 'equipment_records', ['fabricante'], unique=False)
    op.create_index(op.f('ix_equipment_records_modelo'), 'equipment_records', ['modelo'], unique=False)
    op.create_index(op.f('ix_equipment_records_registro_inmetro'), 'equipment_records', ['registro_inmetro'], unique=False)

    # Create data_records table
    op.create_table('data_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('record_id', sa.String(length=255), nullable=False),
        sa.Column('data_type', sa.String(length=50), nullable=False),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=False),
        sa.Column('processing_attempts', sa.Integer(), nullable=False),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_records_data_type'), 'data_records', ['data_type'], unique=False)
    op.create_index(op.f('ix_data_records_record_id'), 'data_records', ['record_id'], unique=True)
    op.create_index(op.f('ix_data_records_timestamp'), 'data_records', ['timestamp'], unique=False)

    # Create crawler_data table
    op.create_table('crawler_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('dataset_name', sa.String(length=255), nullable=False),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('collection_date', sa.DateTime(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=False),
        sa.Column('processing_status', sa.String(length=20), nullable=False),
        sa.Column('processing_attempts', sa.Integer(), nullable=False),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('record_count', sa.Integer(), nullable=True),
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crawler_data_collection_date'), 'crawler_data', ['collection_date'], unique=False)
    op.create_index(op.f('ix_crawler_data_dataset_name'), 'crawler_data', ['dataset_name'], unique=False)
    op.create_index(op.f('ix_crawler_data_source'), 'crawler_data', ['source'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('crawler_data')
    op.drop_table('data_records')
    op.drop_table('equipment_records')
