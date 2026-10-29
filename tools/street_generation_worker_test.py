"""Offline checks for resumed/no-deadline collection and owned-queue deadline stop."""
import json, runpy, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import street_comfy

class StopLoop(BaseException):pass

class WorkerTest(unittest.TestCase):
    def run_worker(self, deadline=None, owned_running=True):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);folder=root/'art-migration/generation/ours';folder.mkdir(parents=True)
            (root/'outputs/street-reskin').mkdir(parents=True)
            (folder/'job.json').write_text(json.dumps({'promptId':'ours','status':'submitted'}),'utf8')
            calls=[]
            def request(endpoint,data=None):
                calls.append((endpoint,data))
                if endpoint.startswith('/history'):return {}
                if endpoint=='/queue' and data is None:return {'queue_pending':[[0,'ours'],[1,'someone-else']], 'queue_running':[[2,'ours' if owned_running else 'someone-else']]}
                return {}
            args=['street_generation_worker.py']+(['--until-utc',deadline] if deadline else [])
            with patch.object(street_comfy,'ROOT',root),patch.object(street_comfy,'request',request),patch('sys.argv',args),patch('time.sleep',side_effect=StopLoop):
                try:runpy.run_path(str(Path(__file__).with_name('street_generation_worker.py')))
                except StopLoop:pass
            result=json.loads((root/'outputs/street-reskin/generation-worker.json').read_text('utf8'))
            return result,calls
    def test_resumed_without_deadline(self):
        result,calls=self.run_worker()
        self.assertEqual(result['status'],'active');self.assertIsNone(result['deadlineUtc'])
        self.assertFalse(any(data is not None for _,data in calls))
    def test_future_deadline_keeps_collecting(self):
        result,calls=self.run_worker('2099-01-01T00:00:00+00:00')
        self.assertEqual(result['status'],'active');self.assertFalse(any(data is not None for _,data in calls))
    def test_deadline_stops_owned_only(self):
        result,calls=self.run_worker('2000-01-01T00:00:00+00:00')
        self.assertEqual(result['status'],'deadline-stopped')
        self.assertIn(('/queue',{'delete':['ours']}),calls);self.assertIn(('/interrupt',{}),calls)
        self.assertNotIn('someone-else',result['cancelledPending'])
    def test_deadline_does_not_interrupt_other_running_job(self):
        _,calls=self.run_worker('2000-01-01T00:00:00+00:00',False)
        self.assertNotIn(('/interrupt',{}),calls)

if __name__=='__main__':unittest.main()
