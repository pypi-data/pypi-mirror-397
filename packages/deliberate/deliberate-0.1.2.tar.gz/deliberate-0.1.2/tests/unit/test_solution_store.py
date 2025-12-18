"""Unit tests for the SolutionStore."""

from pathlib import Path

import pytest

from deliberate.tracking.solution_store import SolutionRecord, SolutionStore
from deliberate.tracking.tracker import AgentPerformanceTracker


@pytest.fixture
def tracker(tmp_path: Path):
    """Create a tracker with a temporary database."""
    db_path = tmp_path / "test.duckdb"
    tracker = AgentPerformanceTracker(db_path)
    yield tracker
    tracker.close()


@pytest.fixture
def store(tracker):
    """Create a SolutionStore with the test tracker."""
    return SolutionStore(tracker)


class TestSolutionRecord:
    """Tests for SolutionRecord dataclass."""

    def test_new_id_generates_unique_ids(self):
        """Should generate unique IDs."""
        ids = [SolutionRecord.new_id() for _ in range(100)]
        assert len(set(ids)) == 100

    def test_new_id_format(self):
        """Should generate IDs with correct prefix."""
        id = SolutionRecord.new_id()
        assert id.startswith("sol_")
        assert len(id) == 16  # "sol_" + 12 hex chars

    def test_to_metrics_dict(self):
        """Should extract metrics as dictionary."""
        record = SolutionRecord(
            id="sol_test",
            task_hash="hash123",
            solution_type="iteration_attempt",
            agent="claude",
            success=True,
            overall_score=0.85,
            test_score=0.9,
            tests_passed=9,
            tests_total=10,
            lint_score=1.0,
            runtime_ms=150.0,
            memory_mb=50.0,
        )
        metrics = record.to_metrics_dict()

        assert metrics["test_score"] == 0.9
        assert metrics["tests_passed"] == 9
        assert metrics["tests_total"] == 10
        assert metrics["lint_score"] == 1.0
        assert metrics["runtime_ms"] == 150.0
        assert metrics["memory_mb"] == 50.0


class TestSolutionStoreCRUD:
    """Tests for basic CRUD operations."""

    def test_add_and_get(self, store):
        """Should add and retrieve a solution."""
        record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_abc",
            solution_type="iteration_attempt",
            agent="claude",
            success=True,
            overall_score=0.85,
            code_content="def foo(): pass",
            is_valid=True,
        )

        # Add with immediate write
        store.add(record, immediate=True)

        # Retrieve
        retrieved = store.get_by_id(record.id)
        assert retrieved is not None
        assert retrieved.id == record.id
        assert retrieved.task_hash == "task_abc"
        assert retrieved.overall_score == 0.85
        assert retrieved.code_content == "def foo(): pass"

    def test_add_batched(self, store):
        """Should batch writes when immediate=False."""
        records = []
        for i in range(5):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                task_hash="task_batch",
                solution_type="evolution_program",
                agent="gpt4",
                success=True,
                overall_score=0.5 + i * 0.1,
                is_valid=True,
            )
            records.append(record)
            store.add(record, immediate=False)

        # Not flushed yet, shouldn't find them
        assert store.get_by_id(records[0].id) is None

        # Flush
        count = store.flush()
        assert count == 5

        # Now should find them
        assert store.get_by_id(records[0].id) is not None

    def test_update(self, store):
        """Should update an existing record."""
        record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_update",
            solution_type="iteration_attempt",
            agent="claude",
            success=False,
            overall_score=0.3,
            is_valid=False,
        )
        store.add(record, immediate=True)

        # Update
        record.success = True
        record.overall_score = 0.9
        record.is_valid = True
        record.is_champion = True
        store.update(record)

        # Verify
        retrieved = store.get_by_id(record.id)
        assert retrieved.success is True
        assert retrieved.overall_score == 0.9
        assert retrieved.is_valid is True
        assert retrieved.is_champion is True

    def test_delete(self, store):
        """Should delete a record."""
        record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_delete",
            solution_type="iteration_attempt",
            agent="claude",
            success=True,
            overall_score=0.5,
        )
        store.add(record, immediate=True)

        # Delete
        result = store.delete(record.id)
        assert result is True

        # Verify gone
        assert store.get_by_id(record.id) is None


class TestSolutionStoreQueries:
    """Tests for query operations."""

    def test_get_best_for_task(self, store):
        """Should return best solutions for a task."""
        # Add solutions with varying scores
        for i in range(10):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                task_hash="task_best",
                solution_type="iteration_attempt",
                agent="claude",
                success=True,
                overall_score=i * 0.1,
                is_valid=True,
            )
            store.add(record, immediate=True)

        # Get top 3
        best = store.get_best_for_task("task_best", limit=3, min_score=0.5)
        assert len(best) == 3
        assert best[0].overall_score == pytest.approx(0.9)
        assert best[1].overall_score == pytest.approx(0.8)
        assert best[2].overall_score == pytest.approx(0.7)

    def test_get_best_for_task_filters_invalid(self, store):
        """Should exclude invalid solutions."""
        # Add valid solution
        valid = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_valid",
            solution_type="iteration_attempt",
            agent="claude",
            success=True,
            overall_score=0.9,
            is_valid=True,
        )
        store.add(valid, immediate=True)

        # Add invalid solution with higher score
        invalid = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_valid",
            solution_type="iteration_attempt",
            agent="claude",
            success=True,
            overall_score=0.95,
            is_valid=False,  # Invalid
        )
        store.add(invalid, immediate=True)

        best = store.get_best_for_task("task_valid", limit=5, min_score=0.0)
        assert len(best) == 1
        assert best[0].id == valid.id

    def test_get_best_for_task_by_type(self, store):
        """Should filter by solution type."""
        # Add iteration attempt
        iter_rec = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_type",
            solution_type="iteration_attempt",
            agent="claude",
            success=True,
            overall_score=0.8,
            is_valid=True,
        )
        store.add(iter_rec, immediate=True)

        # Add evolution program
        evo_rec = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_type",
            solution_type="evolution_program",
            agent="gpt4",
            success=True,
            overall_score=0.9,
            is_valid=True,
        )
        store.add(evo_rec, immediate=True)

        # Filter by type
        iterations = store.get_best_for_task(
            "task_type",
            limit=5,
            min_score=0.0,
            solution_type="iteration_attempt",
        )
        assert len(iterations) == 1
        assert iterations[0].solution_type == "iteration_attempt"

    def test_get_champions(self, store):
        """Should return champion solutions."""
        # Add champions
        for i in range(3):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                task_hash="task_champ",
                solution_type="evolution_program",
                agent="claude",
                success=True,
                overall_score=0.8 + i * 0.05,
                is_valid=True,
                is_champion=True,
            )
            store.add(record, immediate=True)

        # Add non-champions
        for i in range(5):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                task_hash="task_champ",
                solution_type="evolution_program",
                agent="claude",
                success=True,
                overall_score=0.5,
                is_valid=True,
                is_champion=False,
            )
            store.add(record, immediate=True)

        champions = store.get_champions(limit=10)
        assert len(champions) == 3
        assert all(c.is_champion for c in champions)

    def test_get_champions_by_task(self, store):
        """Should filter champions by task."""
        # Champions for task A
        for i in range(2):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                task_hash="task_a",
                solution_type="evolution_program",
                agent="claude",
                success=True,
                overall_score=0.9,
                is_valid=True,
                is_champion=True,
            )
            store.add(record, immediate=True)

        # Champions for task B
        record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_b",
            solution_type="evolution_program",
            agent="claude",
            success=True,
            overall_score=0.9,
            is_valid=True,
            is_champion=True,
        )
        store.add(record, immediate=True)

        champions_a = store.get_champions(limit=10, task_hash="task_a")
        assert len(champions_a) == 2

        champions_b = store.get_champions(limit=10, task_hash="task_b")
        assert len(champions_b) == 1

    def test_get_by_workflow(self, store):
        """Should return all solutions for a workflow."""
        workflow_id = "wf_test123"

        for i in range(5):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                workflow_id=workflow_id,
                task_hash="task_wf",
                solution_type="iteration_attempt",
                agent="claude",
                success=True,
                overall_score=0.5 + i * 0.1,
            )
            store.add(record, immediate=True)

        solutions = store.get_by_workflow(workflow_id)
        assert len(solutions) == 5
        assert all(s.workflow_id == workflow_id for s in solutions)

    def test_count_by_task(self, store):
        """Should count solutions for a task."""
        for i in range(7):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                task_hash="task_count",
                solution_type="iteration_attempt",
                agent="claude",
                success=True,
                overall_score=0.5,
            )
            store.add(record, immediate=True)

        count = store.count_by_task("task_count")
        assert count == 7


class TestSolutionStoreEvolution:
    """Tests for evolution-related operations."""

    def test_sample_for_evolution_basic(self, store):
        """Should sample parents and inspirations."""
        # Add pool of solutions
        for i in range(20):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                task_hash="task_evo",
                solution_type="evolution_program",
                agent="claude",
                success=True,
                overall_score=0.5 + (i % 10) * 0.05,
                is_valid=True,
                is_champion=(i < 3),  # First 3 are champions
            )
            store.add(record, immediate=True)

        parents, inspirations = store.sample_for_evolution(
            "task_evo",
            num_parents=2,
            num_inspirations=3,
        )

        assert len(parents) == 2
        assert len(inspirations) == 3

        # Parents and inspirations should not overlap
        parent_ids = {p.id for p in parents}
        inspiration_ids = {i.id for i in inspirations}
        assert parent_ids.isdisjoint(inspiration_ids)

    def test_sample_for_evolution_empty(self, store):
        """Should handle empty pool gracefully."""
        parents, inspirations = store.sample_for_evolution(
            "nonexistent_task",
            num_parents=2,
            num_inspirations=3,
        )

        assert parents == []
        assert inspirations == []

    def test_sample_for_evolution_small_pool(self, store):
        """Should handle pool smaller than requested sample."""
        # Add only 2 solutions
        for i in range(2):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                task_hash="task_small",
                solution_type="evolution_program",
                agent="claude",
                success=True,
                overall_score=0.8,
                is_valid=True,
            )
            store.add(record, immediate=True)

        parents, inspirations = store.sample_for_evolution(
            "task_small",
            num_parents=5,
            num_inspirations=5,
        )

        # Should return what's available
        assert len(parents) == 2
        assert len(inspirations) == 0  # All used as parents


class TestSolutionStoreNiches:
    """Tests for niche operations (MAP-Elites)."""

    def test_update_and_get_niche(self, store):
        """Should update and retrieve niche occupants."""
        record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_niche",
            solution_type="evolution_program",
            agent="claude",
            success=True,
            overall_score=0.8,
            is_valid=True,
        )
        store.add(record, immediate=True)

        # Set niche
        dimensions = {"test_score": 0.8, "runtime_ms": 100.0}
        store.update_niche(record.id, "niche_0.8_100", dimensions)

        # Retrieve
        occupant = store.get_niche_occupant("niche_0.8_100")
        assert occupant is not None
        assert occupant.id == record.id

    def test_update_niche_replaces(self, store):
        """Should replace existing niche occupant."""
        old_record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_niche",
            solution_type="evolution_program",
            agent="claude",
            success=True,
            overall_score=0.7,
            is_valid=True,
        )
        store.add(old_record, immediate=True)
        store.update_niche(old_record.id, "niche_key", {"score": 0.7})

        new_record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_niche",
            solution_type="evolution_program",
            agent="claude",
            success=True,
            overall_score=0.9,
            is_valid=True,
        )
        store.add(new_record, immediate=True)
        store.update_niche(new_record.id, "niche_key", {"score": 0.9})

        # Should now be new record
        occupant = store.get_niche_occupant("niche_key")
        assert occupant.id == new_record.id

    def test_get_all_niches(self, store):
        """Should retrieve all occupied niches."""
        records = []
        for i in range(3):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                task_hash="task_all_niches",
                solution_type="evolution_program",
                agent="claude",
                success=True,
                overall_score=0.5 + i * 0.1,
                is_valid=True,
            )
            store.add(record, immediate=True)
            records.append(record)
            store.update_niche(record.id, f"niche_{i}", {"score": 0.5 + i * 0.1})

        niches = store.get_all_niches(task_hash="task_all_niches")
        assert len(niches) == 3
        assert "niche_0" in niches
        assert "niche_1" in niches
        assert "niche_2" in niches


class TestSolutionStoreChampions:
    """Tests for champion management."""

    def test_mark_champion(self, store):
        """Should mark a solution as champion."""
        record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_mark",
            solution_type="evolution_program",
            agent="claude",
            success=True,
            overall_score=0.9,
            is_valid=True,
            is_champion=False,
        )
        store.add(record, immediate=True)

        store.mark_champion(record.id, True)

        retrieved = store.get_by_id(record.id)
        assert retrieved.is_champion is True

    def test_clear_champions(self, store):
        """Should clear all champion flags for a task."""
        # Create champions
        for i in range(3):
            record = SolutionRecord(
                id=SolutionRecord.new_id(),
                task_hash="task_clear",
                solution_type="evolution_program",
                agent="claude",
                success=True,
                overall_score=0.9,
                is_valid=True,
                is_champion=True,
            )
            store.add(record, immediate=True)

        # Clear
        store.clear_champions("task_clear")

        # Verify
        champions = store.get_champions(task_hash="task_clear")
        assert len(champions) == 0


class TestSolutionStoreJSONFields:
    """Tests for JSON field handling."""

    def test_inspiration_ids_roundtrip(self, store):
        """Should properly serialize/deserialize inspiration_ids."""
        record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_json",
            solution_type="evolution_program",
            agent="claude",
            success=True,
            overall_score=0.8,
            inspiration_ids=["sol_a", "sol_b", "sol_c"],
        )
        store.add(record, immediate=True)

        retrieved = store.get_by_id(record.id)
        assert retrieved.inspiration_ids == ["sol_a", "sol_b", "sol_c"]

    def test_tags_roundtrip(self, store):
        """Should properly serialize/deserialize tags."""
        record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_json",
            solution_type="evolution_program",
            agent="claude",
            success=True,
            overall_score=0.8,
            tags=["fast", "optimized", "v2"],
        )
        store.add(record, immediate=True)

        retrieved = store.get_by_id(record.id)
        assert retrieved.tags == ["fast", "optimized", "v2"]

    def test_empty_json_fields(self, store):
        """Should handle empty JSON fields."""
        record = SolutionRecord(
            id=SolutionRecord.new_id(),
            task_hash="task_json",
            solution_type="evolution_program",
            agent="claude",
            success=True,
            overall_score=0.8,
            inspiration_ids=[],
            tags=[],
        )
        store.add(record, immediate=True)

        retrieved = store.get_by_id(record.id)
        assert retrieved.inspiration_ids == []
        assert retrieved.tags == []
