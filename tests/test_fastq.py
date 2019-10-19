import pytest
from hypothesis import errors, given

from hypothesis_bio.hypothesis_bio import (
    MAX_ASCII,
    fastq,
    fastq_quality,
    illumina_sequence_id,
    nanopore_sequence_id,
)

from .minimal import minimal


def test_fastq_quality_smallest_example():
    actual = minimal(fastq_quality())
    expected = ""

    assert actual == expected


def test_fastq_quality_smallest_non_empty_with_default_ascii():
    actual = minimal(fastq_quality(size=1))
    expected = "0"  # for some reason hypothesis shrinks towards 0 for unicodes

    assert actual == expected


def test_fastq_quality_size_three_with_one_quality_score():
    actual = minimal(fastq_quality(size=3, min_score=5, max_score=5))
    expected = "&&&"

    assert actual == expected


def test_fastq_quality_size_three_with_one_quality_score_and_sanger_offset():
    actual = minimal(fastq_quality(size=3, min_score=5, max_score=5, offset=64))
    expected = "EEE"

    assert actual == expected


def test_fastq_quality_min_score_larger_than_max_score_raises_error():
    min_score = 10
    max_score = 9
    with pytest.raises(errors.InvalidArgument):
        minimal(fastq_quality(min_score=min_score, max_score=max_score))


def test_fastq_quality_offset_causes_outside_ascii_range_raises_error():
    min_score = 100
    max_score = 101
    with pytest.raises(ValueError):
        minimal(fastq_quality(min_score=min_score, max_score=max_score))


def test_fastq_smallest_example():
    actual = minimal(fastq())
    expected = "@0 0\n\n+0 0\n"

    assert actual == expected


def test_fastq_smallest_non_empty():
    actual = minimal(fastq(size=1))
    expected = "@0 0\nA\n+0 0\n0"

    assert actual == expected


@given(fastq(size=10))
def test_fastq_size_over_one(fastq_string: str):
    fields = fastq_string.split("\n")
    header_begin = fields[0][0]
    assert header_begin == "@"

    seq_id, comment = fields[0][1:].split()
    seq_id_opt, comment_opt = fields[2][1:].split()
    if seq_id:
        assert all(33 <= ord(c) <= MAX_ASCII for c in seq_id)
        assert all(33 <= ord(c) <= MAX_ASCII for c in seq_id_opt)
    if comment:
        assert all(33 <= ord(c) <= MAX_ASCII for c in comment)
        assert all(33 <= ord(c) <= MAX_ASCII for c in comment_opt)

    sequence = fields[1]
    assert all(c in "ACGT" for c in sequence)

    seq_qual_sep = fields[2][0]
    assert seq_qual_sep == "+"

    quality = fields[-1]
    assert all(33 <= ord(c) <= MAX_ASCII for c in quality)


@given(fastq(size=10, additional_description=False))
def test_fastq_size_over_one_with_comment_no_additional_description(fastq_string: str):
    fields = fastq_string.split("\n")
    header_begin = fields[0][0]
    assert header_begin == "@"

    seq_id, comment = fields[0][1:].split()
    if seq_id:
        assert all(33 <= ord(c) <= MAX_ASCII for c in seq_id)
    if comment:
        assert all(33 <= ord(c) <= MAX_ASCII for c in comment)

    sequence = fields[1]
    assert all(c in "ACGT" for c in sequence)

    seq_qual_sep = fields[2][0]
    assert seq_qual_sep == "+"

    optional_description = fields[2][1:].split()
    assert not optional_description

    quality = fields[-1]
    assert all(33 <= ord(c) <= MAX_ASCII for c in quality)


@given(fastq(size=10))
def test_fastq_size_over_one_with_comment(fastq_string: str):
    fields = fastq_string.split("\n")
    header_begin = fields[0][0]
    assert header_begin == "@"

    seq_id, comment = fields[0][1:].split()
    seq_id_opt, comment_opt = fields[2][1:].split()
    if seq_id:
        assert all(33 <= ord(c) <= MAX_ASCII for c in seq_id)
        assert all(33 <= ord(c) <= MAX_ASCII for c in seq_id_opt)
    if comment:
        assert all(33 <= ord(c) <= MAX_ASCII for c in comment)
        assert all(33 <= ord(c) <= MAX_ASCII for c in comment_opt)

    sequence = fields[1]
    assert all(c in "ACGT" for c in sequence)

    seq_qual_sep = fields[2][0]
    assert seq_qual_sep == "+"

    quality = fields[-1]
    assert all(33 <= ord(c) <= MAX_ASCII for c in quality)


@given(fastq(size=10, wrapped=3))
def test_fastq_wrapping_less_than_size_wraps_seq_and_quality(fastq_string: str):
    fields = fastq_string.split("\n")

    actual = len(fields)
    expected = 10

    assert actual == expected


@given(fastq(size=10, wrapped=30))
def test_fastq_wrapping_greater_than_size_doesnt_wrap(fastq_string: str):
    fields = fastq_string.split("\n")

    actual = len(fields)
    expected = 4

    assert actual == expected


def test_illumina_seq_id_minimal():
    actual = minimal(illumina_sequence_id())
    expected = "0:0:0:0:0:0:0:A+A 1:N:0:A"

    assert actual == expected


@given(illumina_sequence_id())
def test_illumina_seq_id_ensure_control_num_is_even_or_zero(seq_id):
    control_num = int(seq_id.split(":")[-2])

    assert control_num % 2 == 0


def test_nanopore_seq_id_minimal():
    actual = minimal(nanopore_sequence_id())
    expected = (
        "00000000-0000-0000-0000-000000000000 "
        "runid={} "
        "sampleid=0 "
        "read=0 "
        "ch=0 "
        "start_time=2000-01-01T00:00:00Z"  # Examples from this strategy shrink towards midnight on January 1st 2000.
    ).format("0" * 40)

    assert actual == expected
