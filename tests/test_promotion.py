import copy
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import promotion


class PromotionTests(unittest.TestCase):
    def record(self):
        return {"image_digest":"sha256:"+"a"*64,"baseline_digest":"sha256:"+"b"*64,"reviewer":"operator","tested_at":"2026-10-15","status":"accepted","checks":dict.fromkeys(promotion.CHECKS,"pass"),"codecs":{c:{"supported":True,"hardware_encoding":"pass","zero_copy":"pass"} for c in ("h264","hevc","av1")}}

    def test_exact_accepted_image(self):
        record=self.record()
        self.assertTrue(promotion.validate(record,record["image_digest"]))

    def test_application_acceptance_is_bound_to_repository_and_digest(self):
        for image in ("wolf_steam", "wolf_lutris"):
            record=self.record()
            with self.assertRaisesRegex(ValueError,"repository"):
                promotion.validate(record,record["image_digest"],image)
            record["image_name"]=image
            self.assertTrue(promotion.validate(record,record["image_digest"],image))
            with self.assertRaisesRegex(ValueError,"repository"):
                promotion.validate(record,record["image_digest"])
            record["checks"]["controller"]="not-run"
            with self.assertRaisesRegex(ValueError,"session checks"):
                promotion.validate(record,record["image_digest"],image)

    def test_failed_incomplete_or_different_image_cannot_promote(self):
        for field in ("status","reviewer","tested_at","baseline_digest"):
            record=self.record(); record[field]=""
            with self.assertRaises(ValueError): promotion.validate(record,record["image_digest"])
        record=self.record()
        with self.assertRaises(ValueError): promotion.validate(record,"sha256:"+"c"*64)
        for check in promotion.CHECKS:
            record=self.record();record["checks"][check]="not-run"
            with self.assertRaises(ValueError): promotion.validate(record,record["image_digest"])

    def test_unsupported_codec_requires_evidence(self):
        record=self.record();record["codecs"]["av1"]={"supported":False}
        with self.assertRaises(ValueError): promotion.validate(record,record["image_digest"])
        record["codecs"]["av1"]["capability_evidence"]="driver capability inventory"
        self.assertTrue(promotion.validate(record,record["image_digest"]))

    def test_software_fallback_is_not_hardware_acceptance(self):
        record=self.record();record["codecs"]["hevc"]["hardware_encoding"]="software-fallback"
        with self.assertRaises(ValueError): promotion.validate(record,record["image_digest"])

    def test_cpu_smoke_only_cannot_promote(self):
        record=self.record();record["checks"]={"static":"pass"}
        with self.assertRaisesRegex(ValueError,"session checks"):
            promotion.validate(record,record["image_digest"])
