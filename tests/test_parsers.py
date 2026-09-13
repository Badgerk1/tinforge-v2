from src.parsers import CSVParser, PDFParser


def test_csv_parser_supports_headers_and_delimiters(tmp_path):
    file_path = tmp_path / "points.csv"
    file_path.write_text("ID,X,Y,Z,Description\n1,10,20,30,BM\n2,11,21,31,EP\n", encoding="utf-8")
    points = CSVParser().parse_file(file_path)
    assert [point.point_id for point in points] == [1, 2]
    assert points[1].description == "EP"


def test_csv_parser_without_header_uses_xyz_description_schema():
    points = CSVParser().parse_text("10,20,30,BM\n11,21,31,EP\n")
    assert [point.point_id for point in points] == [1, 2]
    assert points[0].x == 10.0
    assert points[0].description == "BM"


def test_csv_parser_ignores_spaces_inside_comma_delimited_descriptions():
    points = CSVParser().parse_text("ID,X,Y,Z,Description\n1,10,20,30,Boundary Marker\n", delimiter=None)
    assert len(points) == 1
    assert points[0].description == "Boundary Marker"


def test_pdf_parser_extracts_and_deduplicates_points():
    text = "1 100.0 200.0 50.0 BM\n2 101.0 201.0 51.0 EP\n1 100.0 200.0 50.0 BM\n"
    result = PDFParser().parse_text(text, source_name="survey.txt")
    assert len(result.points) == 2
    assert result.duplicates_removed == 1
    assert result.metadata["source"] == "survey.txt"


def test_pdf_parser_preserves_conflicting_duplicate_ids():
    text = "1 100.0 200.0 50.0 BM\n1 101.0 201.0 51.0 EP\n"
    result = PDFParser().parse_text(text, source_name="survey.txt")
    assert len(result.points) == 2
    assert result.points[1].point_id == 2
    assert result.errors


def test_pdf_parser_handles_multiple_conflicting_duplicates_for_same_id():
    text = "1 100.0 200.0 50.0 BM\n1 101.0 201.0 51.0 EP\n1 102.0 202.0 52.0 CL\n"
    result = PDFParser().parse_text(text, source_name="survey.txt")
    assert [point.point_id for point in result.points] == [1, 2, 3]


def test_pdf_parser_deduplicates_repeated_conflicting_observations():
    text = "1 100.0 200.0 50.0 BM\n1 101.0 201.0 51.0 EP\n1 101.0 201.0 51.0 EP\n"
    result = PDFParser().parse_text(text, source_name="survey.txt")
    assert [point.point_id for point in result.points] == [1, 2]
    assert result.duplicates_removed == 1
