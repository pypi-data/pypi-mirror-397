"""Storage components for sessions and files."""

from .file_storages import (
    FileMetadata,
    MetadataStorageInterface,
    LocalMetadataStorage,
    ElasticsearchMetadataStorage,
    MetadataStorageManager,
    MetadataMigrationUtility,
    MigrationReport,
    FileStorageInterface,
    LocalFileStorage,
    GCP_AVAILABLE,
)

# Conditionally import GCPFileStorage
if GCP_AVAILABLE:
    from .file_storages import GCPFileStorage

__all__ = [
    # File metadata
    'FileMetadata',
    'MetadataStorageInterface',
    'LocalMetadataStorage',
    'ElasticsearchMetadataStorage',
    'MetadataStorageManager',
    'MetadataMigrationUtility',
    'MigrationReport',
    # File storage
    'FileStorageInterface',
    'LocalFileStorage',
    'GCP_AVAILABLE',
    # Modules
    'file_storages',
    'file_system_management',
    'storage_optimizer',
]

# Add GCPFileStorage to __all__ if available
if GCP_AVAILABLE:
    __all__.append('GCPFileStorage')
