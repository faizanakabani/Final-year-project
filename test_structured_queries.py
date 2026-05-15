import unittest

from structured_queries import (
    build_structured_query_response,
    format_category_list_response,
    haversine_km,
    parse_category_list_request,
    parse_distance_request,
)


SAMPLE_ROWS = [
    {
        "id": 1,
        "title": "Church of the Holy Spirit",
        "description": "One of Margao's oldest churches.",
        "category": "churches",
        "latitude": 15.2805,
        "longitude": 73.9610,
    },
    {
        "id": 2,
        "title": "Shri Mangueshi Temple",
        "description": "A prominent Goan temple.",
        "category": "Temples",
        "latitude": 15.4450,
        "longitude": 73.9724,
    },
    {
        "id": 3,
        "title": "Hindu Deities Carving",
        "description": "A carving connected to local worship.",
        "category": "Hindu Deities",
        "latitude": 15.4100,
        "longitude": 74.0100,
    },
    {
        "id": 4,
        "title": "Fort Aguada",
        "description": "A 17th-century Portuguese fort.",
        "category": "Fort",
        "latitude": 15.4925,
        "longitude": 73.7736,
    },
]


class StructuredQueriesTest(unittest.TestCase):
    def test_category_aliases_detect_church_list_request(self):
        parsed = parse_category_list_request("Please list all the churches in Goa")

        self.assertIsNotNone(parsed)
        label, aliases = parsed
        self.assertEqual(label, "churches")
        self.assertIn("churches", aliases)

    def test_temple_list_includes_temple_and_hindu_deity_categories(self):
        response, sources = build_structured_query_response(
            "show all temples",
            SAMPLE_ROWS,
        )

        self.assertIn("I found 2 temples", response)
        self.assertIn("Shri Mangueshi Temple", response)
        self.assertIn("Hindu Deities Carving", response)
        self.assertEqual(len(sources), 2)

    def test_category_list_formatting_is_numbered(self):
        response, sources = format_category_list_response(
            "churches",
            SAMPLE_ROWS,
            {"church", "churches"},
        )

        self.assertIn("I found 1 church", response)
        self.assertIn("1. Church of the Holy Spirit", response)
        self.assertIn("15.2805, 73.9610", response)
        self.assertEqual(sources[0]["title"], "Church of the Holy Spirit")

    def test_distance_parser_supports_from_to_queries(self):
        parsed = parse_distance_request("What is the distance from Panjim to Fort Aguada?")

        self.assertEqual(parsed, ("Panjim", "Fort Aguada"))

    def test_haversine_distance_is_approximately_correct(self):
        distance = haversine_km(15.4909, 73.8278, 15.4925, 73.7736)

        self.assertAlmostEqual(distance, 5.8, delta=0.3)

    def test_distance_response_uses_typed_origin_and_content_destination(self):
        response, sources = build_structured_query_response(
            "distance from Panjim to Fort Aguada",
            SAMPLE_ROWS,
        )

        self.assertIn("approximate straight-line distance", response)
        self.assertIn("Panaji", response)
        self.assertIn("Fort Aguada", response)
        self.assertIn("km", response)
        self.assertEqual(sources[-1]["title"], "Fort Aguada")


if __name__ == "__main__":
    unittest.main()
