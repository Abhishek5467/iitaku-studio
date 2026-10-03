"""Meaningful authorization/limits tests and an actual optical-flow encode test.
Run: python -m unittest backend.test_backend -v (requires httpx for TestClient)."""
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
from fastapi.testclient import TestClient

TEST_DIR=tempfile.TemporaryDirectory()
os.environ["DATA_DIR"]=TEST_DIR.name
os.environ["FREE_IP_DAILY"]="20"
from backend import server,processing

class ProcessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(server.app);cls.clip=Path(TEST_DIR.name)/"clip.mp4"
        writer=cv2.VideoWriter(str(cls.clip),cv2.VideoWriter_fourcc(*"mp4v"),10,(64,64))
        for i in range(10):
            f=np.zeros((64,64,3),np.uint8);cv2.rectangle(f,(8+i,20),(24+i,36),(120,210,190),-1);writer.write(f)
        writer.release()
    def submit(self,plan="flow_free",end="1",headers=None):
        return self.client.post("/v1/jobs",data={"plan_id":plan,"start":"0","end":end},files={"file":("clip.mp4",self.clip.read_bytes(),"video/mp4")},headers=headers or {})
    def test_unknown_plan_and_clip_limit(self):
        self.assertEqual(self.submit("paid=true").status_code,400)
        self.assertEqual(self.submit(end="6").status_code,400)
    def test_paid_plan_cannot_be_enabled_from_browser(self):
        self.assertEqual(self.submit("flow_9").status_code,403)
        self.assertEqual(self.submit("flow_9",headers={"Authorization":"Bearer not-a-key"}).status_code,403)
    def test_key_is_plan_bound_and_single_use(self):
        token="test-one-use-key"
        with server.db() as c:c.execute("INSERT OR REPLACE INTO keys VALUES(?,?,?,NULL)",(server.digest(token),"flow_9",time.time()+60))
        with patch.object(server.pool,"submit"):
            self.assertEqual(self.submit("flow_29",headers={"Authorization":f"Bearer {token}"}).status_code,403)
            first=self.submit("flow_9",headers={"Authorization":f"Bearer {token}"});self.assertEqual(first.status_code,202)
            self.assertEqual(self.submit("flow_9",headers={"Authorization":f"Bearer {token}"}).status_code,403)
            job=first.json();self.assertEqual(self.client.get(f"/v1/jobs/{job['id']}").status_code,404)
            self.assertEqual(self.client.get(f"/v1/jobs/{job['id']}",headers={"X-Job-Token":job["token"]}).status_code,200)
            self.client.delete(f"/v1/jobs/{job['id']}",headers={"X-Job-Token":job["token"]})
    def test_actual_flow_encode_has_correct_duration(self):
        result=self.submit();self.assertEqual(result.status_code,202);job=result.json();headers={"X-Job-Token":job["token"]}
        deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            status=self.client.get(f"/v1/jobs/{job['id']}",headers=headers).json()
            if status["status"] not in ["queued","running"]:break
            time.sleep(.05)
        self.assertEqual(status["status"],"completed",status)
        self.assertEqual(self.client.get(f"/v1/jobs/{job['id']}/output").status_code,404)
        output=self.client.get(f"/v1/jobs/{job['id']}/output",headers=headers);self.assertEqual(output.status_code,200)
        path=Path(TEST_DIR.name)/"result.mp4";path.write_bytes(output.content);duration,fps=processing.probe_video(path)
        self.assertAlmostEqual(duration,2,delta=.15);self.assertAlmostEqual(fps,10,delta=.1)
    def test_scene_cut_does_not_blend_unrelated_frames(self):
        a=np.zeros((32,32,3),np.uint8);b=np.full_like(a,255);np.testing.assert_array_equal(processing.interpolate(a,b,.5),a)

if __name__=="__main__":unittest.main()
