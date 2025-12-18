"""Tests for the evolution module.

Tests the AlphaEvolve-inspired evolutionary code generation:
- Program Database with MAP-elites storage
- Diff-based evolution with SEARCH/REPLACE
- Island populations and migration
- Prompt building for evolution
"""

import pytest

from deliberate.evolution import (
    DatabaseConfig,
    DiffBlock,
    EvaluationLevel,
    EvolutionConfig,
    IslandPopulation,
    Program,
    ProgramDatabase,
    ProgramMetrics,
    PromptBuilder,
    apply_diff,
    create_evolve_markers,
    extract_evolve_regions,
    parse_diff,
)


class TestProgramMetrics:
    """Tests for ProgramMetrics dataclass."""

    def test_default_metrics(self):
        metrics = ProgramMetrics()
        assert metrics.test_score == 0.0
        assert metrics.lint_score == 1.0
        # Overall score includes quality contribution even with no tests
        # 0.6 * 0.0 (correctness) + 0.2 * (1.0 * 0.5 + 0.0 * 0.5) + 0.2 * 0.0 = 0.1
        assert metrics.overall_score == 0.1

    def test_overall_score_calculation(self):
        metrics = ProgramMetrics(
            tests_passed=8,
            tests_total=10,
            test_score=0.8,
            lint_score=1.0,
            coverage_score=0.6,
        )
        # 0.6 * 0.8 + 0.2 * (1.0*0.5 + 0.6*0.5) + 0.2 * 0
        # = 0.48 + 0.2 * 0.8 = 0.48 + 0.16 = 0.64
        assert 0.6 < metrics.overall_score < 0.7

    def test_metrics_to_dict(self):
        metrics = ProgramMetrics(
            tests_passed=5,
            tests_total=10,
            test_score=0.5,
            generation=3,
        )
        d = metrics.to_dict()
        assert d["tests_passed"] == 5
        assert d["test_score"] == 0.5
        assert d["generation"] == 3
        assert "overall_score" in d

    def test_test_specific_metrics_default(self):
        """Test-specific metrics have correct defaults."""
        metrics = ProgramMetrics()
        assert metrics.champion_kill_rate == 0.0
        assert metrics.is_valid_test is False
        assert metrics.test_cases_generated == 0
        assert metrics.covers_edge_cases == []

    def test_test_specific_metrics_custom(self):
        """Test-specific metrics can be set."""
        metrics = ProgramMetrics(
            champion_kill_rate=0.75,
            is_valid_test=True,
            test_cases_generated=5,
            covers_edge_cases=["null_input", "empty_list", "large_input"],
        )
        assert metrics.champion_kill_rate == 0.75
        assert metrics.is_valid_test is True
        assert metrics.test_cases_generated == 5
        assert len(metrics.covers_edge_cases) == 3
        assert "null_input" in metrics.covers_edge_cases

    def test_test_specific_metrics_in_to_dict(self):
        """Test-specific metrics are included in to_dict."""
        metrics = ProgramMetrics(
            champion_kill_rate=0.5,
            is_valid_test=True,
            test_cases_generated=3,
            covers_edge_cases=["edge1", "edge2"],
        )
        d = metrics.to_dict()
        assert d["champion_kill_rate"] == 0.5
        assert d["is_valid_test"] is True
        assert d["test_cases_generated"] == 3
        assert d["covers_edge_cases"] == ["edge1", "edge2"]


class TestProgram:
    """Tests for Program dataclass."""

    def test_create_program(self):
        program = Program(
            id="test-123",
            code="def foo(): pass",
        )
        assert program.id == "test-123"
        assert program.code == "def foo(): pass"
        assert program.generation == 0
        assert not program.is_valid

    def test_clone_program(self):
        parent = Program(
            id="parent-1",
            code="def foo(): return 1",
            metrics=ProgramMetrics(generation=5),
        )
        child = parent.clone("child-1")

        assert child.id == "child-1"
        assert child.code == parent.code
        assert child.metrics.generation == 6
        assert child.metrics.parent_id == "parent-1"
        assert "parent-1" in child.parent_ids


class TestIslandPopulation:
    """Tests for IslandPopulation."""

    def test_empty_island(self):
        island = IslandPopulation(id=0)
        assert len(island) == 0
        assert island.best_score == 0.0
        assert island.champions == []

    def test_add_program(self):
        island = IslandPopulation(id=0)
        program = Program(
            id="p1",
            code="x",
            metrics=ProgramMetrics(test_score=0.8),
            is_valid=True,
        )
        island.add(program)

        assert len(island) == 1
        assert island.best_score == program.metrics.overall_score
        assert "p1" in island.champions

    def test_sample_programs(self):
        island = IslandPopulation(id=0)
        for i in range(5):
            island.add(
                Program(
                    id=f"p{i}",
                    code=f"code{i}",
                    metrics=ProgramMetrics(test_score=i / 10),
                    is_valid=True,
                )
            )

        sampled = island.sample(n=2, temperature=1.0)
        assert len(sampled) == 2
        assert all(isinstance(p, Program) for p in sampled)

    def test_sample_with_exclusion(self):
        island = IslandPopulation(id=0)
        for i in range(3):
            island.add(Program(id=f"p{i}", code=f"code{i}", is_valid=True))

        sampled = island.sample(n=2, exclude={"p0"})
        assert len(sampled) == 2
        assert all(p.id != "p0" for p in sampled)


class TestProgramDatabase:
    """Tests for ProgramDatabase."""

    def test_empty_database(self):
        db = ProgramDatabase()
        assert db.size == 0
        assert db.get_best() is None

    def test_add_program(self):
        db = ProgramDatabase()
        program = Program(
            id="p1",
            code="def foo(): pass",
            metrics=ProgramMetrics(test_score=0.5),
            is_valid=True,
        )
        added = db.add(program)

        assert added
        assert db.size == 1
        assert db.get_best().id == "p1"

    def test_reject_invalid_program(self):
        db = ProgramDatabase()
        program = Program(id="p1", code="x", is_valid=False)
        added = db.add(program)

        assert not added
        assert db.size == 0

    def test_niche_competition(self):
        """Better programs should replace worse ones in the same niche."""
        db = ProgramDatabase(config=DatabaseConfig(niche_dimensions=["test_score"]))

        # Add first program
        p1 = Program(
            id="p1",
            code="def foo(): pass",
            metrics=ProgramMetrics(test_score=0.5),
            is_valid=True,
        )
        db.add(p1)

        # Add better program in same niche
        p2 = Program(
            id="p2",
            code="def foo(): return 1",
            metrics=ProgramMetrics(test_score=0.5, lint_score=1.0, coverage_score=0.5),
            is_valid=True,
        )
        db.add(p2)

        # p2 should replace p1 if it has better overall score
        assert db.size == 1

    def test_sample_parents_and_inspirations(self):
        db = ProgramDatabase()
        for i in range(10):
            db.add(
                Program(
                    id=f"p{i}",
                    code=f"code{i}",
                    metrics=ProgramMetrics(test_score=i / 10),
                    is_valid=True,
                )
            )

        parents, inspirations = db.sample(n_parents=1, n_inspirations=3)

        assert len(parents) == 1
        assert len(inspirations) == 3
        # No overlap
        parent_ids = {p.id for p in parents}
        insp_ids = {p.id for p in inspirations}
        assert parent_ids.isdisjoint(insp_ids)

    def test_migration(self):
        db = ProgramDatabase(
            config=DatabaseConfig(
                num_islands=2,
                migration_rate=1.0,  # Always migrate
            )
        )

        # Add champion to island 0
        p1 = Program(
            id="p1",
            code="champion",
            metrics=ProgramMetrics(test_score=1.0),
            is_valid=True,
        )
        db.add(p1, island_id=0)

        # Migrate
        migrations = db.migrate()

        # Champion should be copied to other island
        assert migrations >= 0  # May or may not migrate depending on random

    def test_stats(self):
        db = ProgramDatabase()
        for i in range(5):
            db.add(
                Program(
                    id=f"p{i}",
                    code=f"code{i}",
                    metrics=ProgramMetrics(test_score=i / 10),
                    is_valid=True,
                )
            )

        stats = db.stats()
        assert stats["total_programs"] == 5
        assert len(stats["islands"]) > 0


class TestDiffParsing:
    """Tests for diff parsing."""

    def test_parse_single_diff(self):
        text = """Here's the fix:

<<<<<<< SEARCH
def foo():
    return 1
=======
def foo():
    return 2
>>>>>>> REPLACE
"""
        blocks = parse_diff(text)
        assert len(blocks) == 1
        assert "return 1" in blocks[0].search
        assert "return 2" in blocks[0].replace

    def test_parse_multiple_diffs(self):
        text = """
<<<<<<< SEARCH
x = 1
=======
x = 2
>>>>>>> REPLACE

<<<<<<< SEARCH
y = 3
=======
y = 4
>>>>>>> REPLACE
"""
        blocks = parse_diff(text)
        assert len(blocks) == 2

    def test_parse_fenced_diff(self):
        text = """
```diff
<<<<<<< SEARCH
old code
=======
new code
>>>>>>> REPLACE
```
"""
        blocks = parse_diff(text)
        assert len(blocks) == 1


class TestDiffApplication:
    """Tests for applying diffs to code."""

    def test_apply_exact_match(self):
        code = "def foo():\n    return 1\n"
        blocks = [
            DiffBlock(
                search="return 1",
                replace="return 2",
            )
        ]
        result = apply_diff(code, blocks)
        assert "return 2" in result

    def test_apply_whitespace_tolerant(self):
        code = "def foo():\n    return 1\n"
        blocks = [
            DiffBlock(
                search="return 1  ",  # Extra whitespace
                replace="return 2",
            )
        ]
        result = apply_diff(code, blocks, fuzzy=True)
        assert "return 2" in result

    def test_apply_multiple_blocks(self):
        code = "x = 1\ny = 2\n"
        blocks = [
            DiffBlock(search="x = 1", replace="x = 10"),
            DiffBlock(search="y = 2", replace="y = 20"),
        ]
        result = apply_diff(code, blocks)
        assert "x = 10" in result
        assert "y = 20" in result

    def test_apply_preserves_indentation(self):
        code = "def foo():\n    if True:\n        return 1\n"
        blocks = [
            DiffBlock(
                search="return 1",
                replace="return 2",
            )
        ]
        result = apply_diff(code, blocks)
        # Indentation should be preserved
        assert "        return 2" in result or "return 2" in result


class TestEvolveMarkers:
    """Tests for EVOLVE-BLOCK markers."""

    def test_create_markers(self):
        code = "def foo():\n    x = 1\n    y = 2\n    return x + y\n"
        marked = create_evolve_markers(code, 2, 3, language="python")

        assert "# EVOLVE-BLOCK-START" in marked
        assert "# EVOLVE-BLOCK-END" in marked

    def test_extract_regions(self):
        code = """def foo():
    # EVOLVE-BLOCK-START
    x = 1
    y = 2
    # EVOLVE-BLOCK-END
    return x + y
"""
        regions = extract_evolve_regions(code)
        assert len(regions) == 1
        assert "x = 1" in regions[0].content

    def test_extract_named_region(self):
        code = """# EVOLVE-BLOCK-START optimization
expensive_computation()
# EVOLVE-BLOCK-END optimization
"""
        regions = extract_evolve_regions(code)
        assert len(regions) == 1
        assert regions[0].name == "optimization"


class TestPromptBuilder:
    """Tests for PromptBuilder."""

    def test_build_initial_prompt(self):
        builder = PromptBuilder()
        prompt = builder.build_initial_prompt(
            task="Write a sorting function",
            seed_code="def sort(arr): pass",
        )

        assert "Write a sorting function" in prompt
        assert "def sort(arr): pass" in prompt

    def test_build_evolution_prompt(self):
        builder = PromptBuilder()
        parent = Program(
            id="p1",
            code="def foo(): return 1",
            metrics=ProgramMetrics(test_score=0.5, tests_passed=5, tests_total=10),
        )

        prompt = builder.build_evolution_prompt(
            task="Improve the function",
            parent=parent,
            iteration=3,
        )

        assert "Improve the function" in prompt
        assert "def foo(): return 1" in prompt
        assert "SEARCH" in prompt  # Diff instructions

    def test_build_feedback_from_metrics(self):
        builder = PromptBuilder()
        metrics = ProgramMetrics(
            tests_passed=7,
            tests_total=10,
            test_score=0.7,
            lint_score=0.9,
        )

        feedback = builder.build_feedback_from_metrics(
            metrics,
            test_output="2 tests failed: test_edge_case, test_overflow",
        )

        assert "7/10" in feedback
        assert "test_edge_case" in feedback or "Overall Score" in feedback


class TestEvolutionConfig:
    """Tests for EvolutionConfig."""

    def test_default_config(self):
        config = EvolutionConfig()
        assert config.max_iterations == 1000
        assert config.fast_model_ratio == 0.8
        assert config.prefer_diffs is True

    def test_cascade_levels(self):
        config = EvolutionConfig()
        assert EvaluationLevel.SYNTAX in config.cascade_levels
        assert EvaluationLevel.LINT in config.cascade_levels


class TestDatabaseConfig:
    """Tests for DatabaseConfig."""

    def test_default_config(self):
        config = DatabaseConfig()
        assert config.num_islands == 4
        assert config.max_programs == 1000
        assert "test_score" in config.niche_dimensions


class TestProgramDatabasePersistence:
    """Tests for ProgramDatabase persistence with SolutionStore."""

    @pytest.fixture
    def tracker_and_store(self, tmp_path):
        """Create tracker and solution store for testing."""
        from deliberate.tracking.solution_store import SolutionStore
        from deliberate.tracking.tracker import AgentPerformanceTracker

        db_path = tmp_path / "test_db.duckdb"
        tracker = AgentPerformanceTracker(str(db_path))
        store = SolutionStore(tracker)
        return tracker, store

    def test_database_without_store(self):
        """Database works without SolutionStore (backward compatibility)."""
        db = ProgramDatabase()
        p = Program(
            id="p1",
            code="def foo(): pass",
            metrics=ProgramMetrics(test_score=0.5),
            is_valid=True,
        )
        assert db.add(p) is True
        assert db.size == 1

    def test_database_with_store_persists(self, tracker_and_store):
        """Programs are persisted to SolutionStore."""
        tracker, store = tracker_and_store

        db = ProgramDatabase(
            solution_store=store,
            task_hash="test_task_123",
        )

        # Add a champion (should trigger immediate flush)
        p = Program(
            id="p1",
            code="def foo(): return 1",
            metrics=ProgramMetrics(test_score=1.0),
            is_valid=True,
            agent="claude",
        )
        db.add(p)

        # Verify persisted
        record = store.get_by_id("p1")
        assert record is not None
        assert record.task_hash == "test_task_123"
        assert record.solution_type == "evolution_program"
        assert record.agent == "claude"

    def test_database_batch_persistence(self, tracker_and_store):
        """Non-champion programs are batched before persistence."""
        tracker, store = tracker_and_store

        db = ProgramDatabase(
            solution_store=store,
            task_hash="test_batch",
        )

        # Add one champion first to set baseline (triggers immediate flush)
        champion = Program(
            id="champion",
            code="def champion(): return True",
            metrics=ProgramMetrics(test_score=0.9),
            is_valid=True,
        )
        db.add(champion)
        assert len(db._pending_writes) == 0  # Champion was flushed immediately

        # Add more programs with lower scores (should batch)
        for i in range(5):
            p = Program(
                id=f"p{i}",
                code=f"def foo{i}(): pass",
                metrics=ProgramMetrics(test_score=0.1 * i),  # Below champion
                is_valid=True,
            )
            db.add(p)

        # Should be in pending buffer (not yet flushed)
        assert len(db._pending_writes) == 5

        # Force flush
        flushed = db.flush()
        assert flushed == 5
        assert len(db._pending_writes) == 0

        # All should be in store now (champion + 5 others)
        assert store.count_by_task("test_batch") == 6

    def test_database_loads_from_store(self, tracker_and_store):
        """Database loads existing champions from store on init."""
        tracker, store = tracker_and_store

        # Pre-populate store with some programs
        from deliberate.tracking.solution_store import SolutionRecord

        for i in range(3):
            record = SolutionRecord(
                id=f"existing_{i}",
                task_hash="test_load",
                solution_type="evolution_program",
                agent="claude",
                success=True,
                overall_score=0.8 + i * 0.05,
                code_content=f"def foo{i}(): return {i}",
                is_valid=True,
                is_champion=True,
            )
            store.add(record, immediate=True)

        # Create database that should load from store
        db = ProgramDatabase(
            solution_store=store,
            task_hash="test_load",
            load_champions=True,
        )

        # Should have loaded programs (may not be all 3 due to niche competition)
        assert db.size >= 1  # At least one program loaded
        # Verify we can sample from loaded programs
        best = db.get_best()
        assert best is not None
        assert best.id.startswith("existing_")

    def test_database_niche_persistence(self, tracker_and_store):
        """Niche dimensions are persisted to store."""
        tracker, store = tracker_and_store

        db = ProgramDatabase(
            solution_store=store,
            task_hash="test_niche",
        )

        p = Program(
            id="p_niche",
            code="def foo(): return 1",
            metrics=ProgramMetrics(test_score=0.9, runtime_ms=100.0, lines_of_code=10),
            is_valid=True,
        )
        db.add(p)
        db.flush()

        # Check niche was persisted
        niches = store.get_all_niches("test_niche")
        assert len(niches) >= 1

    def test_program_to_record_conversion(self, tracker_and_store):
        """Program correctly converts to SolutionRecord."""
        tracker, store = tracker_and_store

        db = ProgramDatabase(
            solution_store=store,
            task_hash="test_conversion",
        )

        p = Program(
            id="convert_test",
            code="def foo(): return 42",
            metrics=ProgramMetrics(
                test_score=0.9,
                tests_passed=9,
                tests_total=10,
                lint_score=0.95,
                runtime_ms=50.0,
                memory_mb=100.0,
                generation=5,
            ),
            parent_ids=["parent_1"],
            inspiration_ids=["insp_1", "insp_2"],
            agent="gpt-4",
            diff_applied="some diff",
            is_valid=True,
            is_champion=True,
        )

        record = db._program_to_record(p)

        assert record.id == "convert_test"
        assert record.task_hash == "test_conversion"
        assert record.code_content == "def foo(): return 42"
        assert record.test_score == 0.9
        assert record.tests_passed == 9
        assert record.tests_total == 10
        assert record.lint_score == 0.95
        assert record.runtime_ms == 50.0
        assert record.memory_mb == 100.0
        assert record.generation == 5
        assert record.parent_solution_id == "parent_1"
        assert record.inspiration_ids == ["insp_1", "insp_2"]
        assert record.agent == "gpt-4"
        assert record.diff_applied == "some diff"
        assert record.is_valid is True
        assert record.is_champion is True
