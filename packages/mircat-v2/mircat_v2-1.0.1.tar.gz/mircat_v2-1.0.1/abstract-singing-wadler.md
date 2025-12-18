# mircat-v2 Decoupling and Code Organization Plan

## Goal
Reduce coupling between components while maintaining backward compatibility and improving maintainability.

---

## Phase 1: BatchWriter for Database Operations (High Impact, Low Risk)

**Problem:** Four modules duplicate the same batch insertion pattern:
- `converter.py` - accumulates `metadata_batch`, checks size, inserts, resets
- `analyzer.py` - accumulates `batch_data` dict, checks modulo, inserts per table
- `segmentor.py` - calls insert twice (completed/failed)
- `extractor.py` - single insert at end

**Solution:** Add `BatchWriter` and `MultiBatchWriter` to [dbase.py](src/mircat_v2/dbase.py)

```python
class BatchWriter:
    """Context manager for batched database writes."""
    def __init__(self, dbase_path, table, batch_size=100, ignore=False):
        ...
    def add(self, record: dict) -> None: ...
    def add_many(self, records: list[dict]) -> None: ...
    def flush(self) -> None: ...
    def __enter__(self): return self
    def __exit__(self, *args): self.flush()

class MultiBatchWriter:
    """Manages multiple BatchWriters for different tables."""
    def __init__(self, dbase_path, tables, batch_size=100, ignore=False): ...
    def add(self, table: str, record: dict) -> None: ...
    def flush_all(self) -> None: ...
```

**Files to modify:**
- [dbase.py](src/mircat_v2/dbase.py) - Add new classes
- [converter.py](src/mircat_v2/dicom_conversion/converter.py) - Use BatchWriter
- [analyzer.py](src/mircat_v2/stats/analyzer.py) - Use MultiBatchWriter
- [segmentor.py](src/mircat_v2/segmentation/segmentor.py) - Use BatchWriter
- [extractor.py](src/mircat_v2/radiomics/extractor.py) - Use BatchWriter

**Effort:** 2-3 hours

---

## Phase 2: Extract Stats Formatters from StatsNifti (High Impact, Medium Risk)

**Problem:** `StatsNifti.format_stats_for_db()` is 237 lines with 9 nested functions that hardcode database table structures, tightly coupling the NIfTI data model to the database schema.

**Solution:** Create [stats/formatters.py](src/mircat_v2/stats/formatters.py) with individual formatter classes:

```python
class StatsFormatter(Protocol):
    table_name: str
    def format(self, stats: dict, identifier: dict) -> list[dict]: ...

class MetadataFormatter: ...
class VolIntFormatter: ...
class ContrastFormatter: ...
class VertebraeFormatter: ...
class AortaMetricsFormatter: ...
class AortaDiametersFormatter: ...
class TissuesVolumetricFormatter: ...
class TissuesVertebralFormatter: ...
class IliacFormatter: ...

class StatsFormatterRegistry:
    def register(self, formatter): ...
    def format_all(self, stats, identifier) -> dict[str, list[dict]]: ...
```

**Files to modify:**
- [stats/formatters.py](src/mircat_v2/stats/formatters.py) - New file
- [nifti.py](src/mircat_v2/nifti.py) - Delegate `format_stats_for_db()` to registry

**Effort:** 4-5 hours

---

## Phase 3: Consolidate Nifti Resampling (Low Risk, Quick Win)

**Problem:** `SegNifti` and `S3SegNifti` have identical `resample_and_save_for_segmentation()` methods (17 lines duplicated).

**Solution:** Extract to standalone function in [nifti.py](src/mircat_v2/nifti.py):

```python
def resample_and_save(img, spacing, new_spacing, output_path, interpolator_type) -> None:
    """Standalone function for resampling and saving NIfTI images."""
    if len(new_spacing) == 2:
        new_spacing = [*new_spacing, spacing[-1]]
    resampled = resample_with_sitk(img, new_spacing, is_label=False, interpolator_type=interpolator_type)
    sitk.WriteImage(resampled, output_path)
```

Both classes call the shared function.

**Files to modify:**
- [nifti.py](src/mircat_v2/nifti.py) - Extract function, update both classes

**Effort:** 1 hour

---

## Phase 4: Base Processor Class (Medium Impact, Medium Risk)

**Problem:** `Analyzer`, `MircatSegmentor`, `DicomConverter` all implement:
- Multiprocessing Pool management
- Progress logging: `[{i}/{total}] ({i/total:.2%})`
- KeyboardInterrupt handling with cleanup
- Batch accumulation and insertion

**Solution:** Create [processing/base.py](src/mircat_v2/processing/base.py):

```python
class BatchProcessor(ABC, Generic[T, R]):
    def __init__(self, n_processes, batch_size, verbose, quiet): ...

    @abstractmethod
    def process_item(self, item: T) -> R: ...

    @abstractmethod
    def get_task_name(self) -> str: ...

    def on_success(self, item, result, index, total): ...
    def on_failure(self, item, error, index, total): ...
    def on_interrupt(self): ...

    def run(self, items: list[T]) -> list[R]:
        with Pool(self.n_processes) as pool:
            for i, result in enumerate(pool.imap_unordered(self.process_item, items), 1):
                # progress tracking, error handling
```

**Files to modify:**
- [processing/base.py](src/mircat_v2/processing/base.py) - New file
- [processing/__init__.py](src/mircat_v2/processing/__init__.py) - New file
- [analyzer.py](src/mircat_v2/stats/analyzer.py) - Inherit from BatchProcessor
- [segmentor.py](src/mircat_v2/segmentation/segmentor.py) - Inherit from BatchProcessor
- [converter.py](src/mircat_v2/dicom_conversion/converter.py) - Inherit from BatchProcessor

**Effort:** 4-6 hours

---

## Phase 5: Configuration Caching (Low Risk, Quick Win)

**Problem:** Config functions read the JSON file repeatedly. Also `extractor.py` reads config at module import time (global state).

**Solution:** Add `@lru_cache` to config functions in [configs/config.py](src/mircat_v2/configs/config.py):

```python
@lru_cache(maxsize=1)
def read_config() -> dict: ...

@lru_cache(maxsize=1)
def read_dbase_config() -> dict: ...

def invalidate_config_cache() -> None:
    """Clear cache after write_config()."""
    read_config.cache_clear()
    ...
```

**Files to modify:**
- [configs/config.py](src/mircat_v2/configs/config.py) - Add caching
- [extractor.py](src/mircat_v2/radiomics/extractor.py) - Move config reads to class init

**Effort:** 1 hour

---

## Implementation Order

```
Phase 1 (BatchWriter) ─────┬──> Phase 4 (Base Processor)
                           │
Phase 3 (Resampling) ──────┤   (can be done independently)
                           │
Phase 5 (Config Cache) ────┘

Phase 2 (Formatters) ──────────> (independent, can start anytime)
```

**Recommended sequence:**
1. **Phase 1** - Highest impact, immediate benefit to all DB operations
2. **Phase 5** - Quick win, 1 hour, no risk
3. **Phase 3** - Quick win, 1 hour, removes duplication
4. **Phase 2** - Medium effort, breaks up the god class
5. **Phase 4** - Most complex, do after others are stable

---

## Testing Strategy

For each phase, verify:
1. `mircat-v2 convert` - conversion + DB insertion works
2. `mircat-v2 segment` - segmentation + DB insertion works
3. `mircat-v2 stats` - stats calculation + DB insertion works
4. `mircat-v2 radiomics` - radiomics extraction + DB insertion works

---

## Total Effort Estimate

| Phase | Effort | Risk |
|-------|--------|------|
| Phase 1: BatchWriter | 2-3 hours | Low |
| Phase 2: Formatters | 4-5 hours | Medium |
| Phase 3: Resampling | 1 hour | Low |
| Phase 4: Base Processor | 4-6 hours | Medium |
| Phase 5: Config Cache | 1 hour | Low |
| **Total** | **12-16 hours** | - |
