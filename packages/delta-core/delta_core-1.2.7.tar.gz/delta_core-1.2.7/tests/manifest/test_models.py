import importlib.resources
import json
import unittest

from delta.manifest.models import Manifest, License, Copyright


class TestManifestPydanticModel(unittest.TestCase):
    def test_minimal_manifest(self):
        expected_license = License(
            name="LGPLv3",
            url="https://www.gnu.org/licenses/gpl-3.0.txt",
            copyrights=[
                Copyright(company="GAEL Systems", years=[2023, 2024])
            ]
        )

        traversable = (
            importlib.resources.files("delta.manifest.v1_4")
            .joinpath("minimum.json")
        )
        with importlib.resources.as_file(traversable) as path:
            with open(path) as fp:
                manifest_data = json.load(fp)
        manifest = Manifest.model_validate(manifest_data)

        self.assertEqual(manifest.name, "Delta Twin name")
        self.assertEqual(manifest.description, "Delta Twin Description")
        self.assertIsNone(manifest.short_description)
        self.assertEqual(manifest.license, expected_license)
        self.assertEqual(manifest.owner, "GAEL Systems")
        self.assertEqual(manifest.resources, {})
        self.assertEqual(manifest.inputs, {})
        self.assertEqual(manifest.outputs, {})
        self.assertEqual(manifest.models, {})
        self.assertEqual(manifest.dependencies, {})
