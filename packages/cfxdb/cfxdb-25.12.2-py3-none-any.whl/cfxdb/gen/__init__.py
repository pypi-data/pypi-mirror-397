# Register zlmdb's vendored flatbuffers in sys.modules so that the flatc-generated
# code in this package (which does `import flatbuffers`) resolves to zlmdb's
# vendored copy instead of requiring a separate flatbuffers package.
#
# Note: We import zlmdb directly here (not via cfxdb) to avoid circular imports.
# The setup_flatbuffers_import function may be monkey-patched by cfxdb.__init__
# for zlmdb < 25.12.2, or natively available in zlmdb >= 25.12.2.
import sys
import zlmdb

# Check if zlmdb has setup_flatbuffers_import (zlmdb >= 25.12.2 or monkey-patched)
if hasattr(zlmdb, "setup_flatbuffers_import"):
    zlmdb.setup_flatbuffers_import()
else:
    # Fallback for zlmdb 25.12.1: register vendored flatbuffers directly
    _vendor = zlmdb._flatbuffers_vendor
    sys.modules.setdefault("flatbuffers", _vendor)
    sys.modules.setdefault("flatbuffers.compat", _vendor.compat)
    sys.modules.setdefault("flatbuffers.builder", _vendor.builder)
    sys.modules.setdefault("flatbuffers.table", _vendor.table)
    sys.modules.setdefault("flatbuffers.util", _vendor.util)
    sys.modules.setdefault("flatbuffers.number_types", _vendor.number_types)
    sys.modules.setdefault("flatbuffers.packer", _vendor.packer)
    sys.modules.setdefault("flatbuffers.encode", _vendor.encode)
