#!/usr/bin/env python3

import json
import unittest
from hifi_solves_run_humanwgs.backends.parameter_override import (
    generate_memory_override_inputs
)
from hifi_solves_run_humanwgs.upload_and_run import (
    import_backend_module
)
from hifi_solves_run_humanwgs.logger import logger
import pandas as pd


class TestGenerateInput(unittest.TestCase):
    expected_sample_info = pd.DataFrame.from_records(
        [
            (
                "HG005-fam",
                "HG005",
                ["movie1.bam", "movie2.bam"],
                "HG006",
                "HG007",
                "MALE",
                False,
            ),
            ("HG005-fam", "HG006", ["movie3.bam"], None, None, "MALE", False),
            ("HG005-fam", "HG007", ["movie4.bam"], None, None, "FEMALE", False),
        ],
        columns=[
            "family_id",
            "sample_id",
            "hifi_reads",
            "father_id",
            "mother_id",
            "sex",
            "affected",
        ],
    ).set_index("sample_id", drop=False)

    def test_all_memory_override_inputs(self):
        expected_memory_override_inputs = {
            "HumanWGS_wrapper.hiphase_override_mem_gb": 1,
            "HumanWGS_wrapper.merge_bam_stats_override_mem_gb": 2,
            "HumanWGS_wrapper.pbmm2_align_wgs_override_mem_gb": 3,
            "HumanWGS_wrapper.pbstarphase_diplotype_override_mem_gb": 5}
    
        input_memory_override_inputs = {
            "hiphase_override_mem_gb": 1,
            "merge_bam_stats_override_mem_gb": 2,
            "pbmm2_align_wgs_override_mem_gb": 3,
            "pbstarphase_diplotype_override_mem_gb": 5}

        test_mem_override_inputs = {}
        test_mem_override_inputs.update(generate_memory_override_inputs(input_memory_override_inputs))
        self.assertDictEqual(expected_memory_override_inputs, test_mem_override_inputs)

    def test_partial_memory_override_inputs(self):
        expected_memory_override_inputs = {
            "HumanWGS_wrapper.hiphase_override_mem_gb": 1,
            "HumanWGS_wrapper.pbstarphase_diplotype_override_mem_gb": 5}
    
        input_memory_override_inputs = {
            "hiphase_override_mem_gb": 1,
            "merge_bam_stats_override_mem_gb": None,
            "pbmm2_align_wgs_override_mem_gb": None,
            "pbstarphase_diplotype_override_mem_gb": 5}

        test_mem_override_inputs = {}
        test_mem_override_inputs.update(generate_memory_override_inputs(input_memory_override_inputs))
        self.assertDictEqual(expected_memory_override_inputs, test_mem_override_inputs)

    def test_none_memory_override_inputs(self):
        expected_memory_override_inputs = {}
        input_memory_override_inputs = {
            "hiphase_override_mem_gb": None,
            "merge_bam_stats_override_mem_gb": None,
            "pbmm2_align_wgs_override_mem_gb": None,
            "pbstarphase_diplotype_override_mem_gb": None}

        test_mem_override_inputs = {}
        test_mem_override_inputs.update(generate_memory_override_inputs(input_memory_override_inputs))
        self.assertDictEqual(expected_memory_override_inputs, test_mem_override_inputs)

    def test_gcp_generate_inputs(self):
        backend_module = import_backend_module("GCP")
        reference_input_bucket="testorg-reference-inputs"
        workflow_file_outputs_bucket="testorg-workflow-file-outputs"
        region="us-central1-b"
        container_registry="dnastack"
        expected_workflow_inputs = {
          "HumanWGS_wrapper.family": {
            "family_id": "HG005-fam",
            "samples": [
              {
                "sample_id": "HG005",
                "hifi_reads": [
                  "movie1.bam",
                  "movie2.bam"
                ],
                "father_id": "HG006",
                "mother_id": "HG007",
                "sex": "MALE",
                "affected": False
              },
              {
                "sample_id": "HG006",
                "hifi_reads": [
                  "movie3.bam"
                ],
                "sex": "MALE",
                "affected": False
              },
              {
                "sample_id": "HG007",
                "hifi_reads": [
                  "movie4.bam"
                ],
                "sex": "FEMALE",
                "affected": False
              }
            ]
          },
          "HumanWGS_wrapper.ref_map_file": "gs://testorg-reference-inputs/dataset/map_files/GRCh38.ref_map.v2p0p0.gcp.tsv",
          "HumanWGS_wrapper.backend": "GCP",
          "HumanWGS_wrapper.preemptible": True,
          "HumanWGS_wrapper.workflow_outputs_bucket": "gs://testorg-workflow-file-outputs",
          "HumanWGS_wrapper.zones": "us-central1-b-b us-central1-b-c",
          "HumanWGS_wrapper.container_registry": "dnastack",
          "HumanWGS_wrapper.hiphase_override_mem_gb": 1,
          "HumanWGS_wrapper.merge_bam_stats_override_mem_gb": 2,
          "HumanWGS_wrapper.pbmm2_align_wgs_override_mem_gb": 3,
          "HumanWGS_wrapper.pbstarphase_diplotype_override_mem_gb": 5
        }
        input_memory_override_inputs = {
            "hiphase_override_mem_gb": 1,
            "merge_bam_stats_override_mem_gb": 2,
            "pbmm2_align_wgs_override_mem_gb": 3,
            "pbstarphase_diplotype_override_mem_gb": 5}
        static_inputs = backend_module.get_static_workflow_inputs(
            reference_inputs_bucket=reference_input_bucket,
            workflow_file_outputs_bucket=workflow_file_outputs_bucket,
            region=region,
            container_registry=container_registry
        )
        workflow_inputs, engine_params = backend_module.generate_inputs_json(
            self.expected_sample_info,
            reference_input_bucket,
            workflow_file_outputs_bucket,
            region,
            container_registry=container_registry,
            **input_memory_override_inputs)
        self.assertDictEqual(workflow_inputs, expected_workflow_inputs)


if __name__ == '__main__':
    unittest.main()


# __END__
