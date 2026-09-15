"""Actual LangSmith SDK -> local HTTP recorder. NOT a LangSmith server or cloud integration."""
import json
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from urllib3.util.retry import Retry
from langsmith import Client
from langchain_core.tracers.langchain import LangChainTracer, wait_for_all_tracers
from langgraph.checkpoint.sqlite import SqliteSaver
import runtime_prototype as runtime

BASE=Path(__file__).resolve().parent
WORK=BASE/'runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ-trace')
WORK.mkdir(parents=True)
CANARY='PRIVATE_CONTEXT_CANARY_NOT_FOR_TRACE'
PAYLOADS=[]
HTTP_STATUS=200


class Recorder(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass

    def do_POST(self):
        body=self.rfile.read(int(self.headers.get('Content-Length','0')))
        PAYLOADS.append({'path':self.path,'method':self.command,'status':HTTP_STATUS,
                         'body':json.loads(body) if body else None})
        self.send_response(HTTP_STATUS)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(b'{}')

    do_PATCH=do_POST


server=ThreadingHTTPServer(('127.0.0.1',0),Recorder)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
allow={'thread_id','task_id','request_snapshot'}
client=Client(api_url=f'http://127.0.0.1:{server.server_address[1]}',api_key='local-prototype-placeholder',
              auto_batch_tracing=False,hide_inputs=True,hide_outputs=True,
              hide_metadata=lambda values:{k:v for k,v in values.items() if k in allow},
              omit_traced_runtime_info=True,retry_config=Retry(total=0),timeout_ms=1000,info={})
results=[]
try:
    for name,status in [('capture',200),('unavailable',503)]:
        HTTP_STATUS=status
        req=runtime.request_for(name)
        event={'id':name+':fixture','actor':'fixture-user','origin':'fixture','focus':'rate',
               'request_id':req['id'],'snapshot':req['snapshot'],'raw':CANARY}
        with SqliteSaver.from_conn_string(str(WORK/f'{name}-checkpoints.sqlite')) as cp:
            graph=runtime.builder().compile(checkpointer=cp)
            tracer=LangChainTracer(project_name='local-sdk-transport-probe',client=client)
            state=graph.invoke({'task':name,'work':str(WORK),'actor':'fixture-user','preselected':event},
                {'configurable':{'thread_id':name},'callbacks':[tracer],
                 'metadata':{'task_id':name,'thread_id':name,'request_snapshot':req['snapshot'],
                             'private_learner_note':CANARY}},durability='sync')
            wait_for_all_tracers()
            results.append({'case':name,'http_status':status,'phase':state['phase'],
                            'task_id':name,'request_snapshot':req['snapshot'],
                            'artifact_hashes':state['check']['hashes'],
                            'delivery_exists':runtime.record(WORK,name)['delivery'] is not None})
    text=json.dumps(PAYLOADS,ensure_ascii=False)
    runs=[x['body'] for x in PAYLOADS if x['status']==200 and x['method']=='POST']
    report={'scope':'actual LangSmith SDK HTTP serialization into a local recorder; no LangSmith backend',
            'results':results,'request_count':len(PAYLOADS),'run_types':sorted(set(x.get('run_type','') for x in runs)),
            'private_canary_absent':CANARY not in text,
            'inputs_hidden':all(not x.get('inputs') for x in runs),
            'metadata_allowlist':sorted(allow),
            'correlated_runs':sum(x.get('extra',{}).get('metadata',{}).get('task_id')=='capture' for x in runs),
            'payloads':PAYLOADS}
    (WORK/'sdk-transport.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    assert runs and report['private_canary_absent'] and report['inputs_hidden']
    assert 'llm' in report['run_types'] and 'tool' in report['run_types']
    assert all(x['phase']=='runtime_probe_complete' and x['delivery_exists'] for x in results)
    print(json.dumps({k:v for k,v in report.items() if k!='payloads'},ensure_ascii=False))
    print(str(WORK/'sdk-transport.json'))
finally:
    client.close();server.shutdown();server.server_close()
