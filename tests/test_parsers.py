from src.parsers import CSVParser, PDFParser


def test_csv_parser_supports_headers_and_delimiters(tmp_path):
    file_path = tmp_path / "points.csv"
    file_path.write_text("ID,X,Y,Z,Description\n1,10,20,30,BM\n2,11,21,31,EP\n", encoding="utf-8")
    points = CSVParser().parse_file(file_path)
    assert [point.point_id for point in points] == [1, 2]
    assert points[1].description == "EP"


def test_pdf_parser_extracts_and_deduplicates_points():
    text = "1 100.0 200.0 50.0 BM\n2 101.0 201.0 51.0 EP\n1 100.0 200.0 50.0 BM\n"
    result = PDFParser().parse_text(text, source_name="survey.txt")
    assert len(result.points) == 2
    assert result.duplicates_removed == 1
    assert result.metadata["source"] == "survey.txt"
