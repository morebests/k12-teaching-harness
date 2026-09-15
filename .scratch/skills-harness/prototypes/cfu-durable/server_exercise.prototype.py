"""Real Agent Server dev API probe, fixed response. Run start, restart dev server, then resume."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

from langgraph_sdk import get_sync_client
import runtime_prototype as runtime

BASE=Path(__file__).resolve().parent
RECORD=BASE/'server-probe.json'
client=get_sync_client(url='http://127.0.0.1:62915')
mode=sys.argv[1]

if mode=='start':
    if RECORD.exists():
        raise ValueError('previous server probe exists; preserve it before a new experiment')
    assistant=client.assistants.create('cfu_probe',name='CFU runtime prototype')
    thread=client.threads.create(metadata={'purpose':'fixed-runtime-fixture'})
    task='server_'+datetime.now(timezone.utc).strftime('%H%M%S')
    state={'task':task,'work':str(BASE/'runs'/task),'actor':'fixture-user','behavior':runtime.BEHAVIOR}
    parts=[{'event':p.event,'data':p.data} for p in client.runs.stream(
        thread['thread_id'],assistant['assistant_id'],input=state,
        stream_mode='values',on_disconnect='continue',multitask_strategy='reject',durability='sync')]
    snapshot=client.threads.get_state(thread['thread_id'])
    report={'mode':'langgraph dev, local persistence; not PostgreSQL production',
            'assistant':assistant,'thread':thread,'task':task,'work':state['work'],
            'start_stream':parts,'before_restart':snapshot}
    RECORD.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    assert snapshot['next']==['await_focus']
    print(json.dumps({'thread':thread['thread_id'],'next':snapshot['next'],'request':snapshot['values']['request']},ensure_ascii=False))
elif mode=='resume':
    report=json.loads(RECORD.read_text()); tid=report['thread']['thread_id']
    after=client.threads.get_state(tid); before=report['before_restart']
    assert after['values']['request']==before['values']['request'] and after['next']==['await_focus']
    req=after['values']['request']
    event={'id':report['task']+':reply','actor':'fixture-user','origin':'fixture','focus':'initial',
           'request_id':req['id'],'snapshot':req['snapshot'],'raw':'测试脚本：改为初始值'}
    runtime.accept_event(report['work'],report['task'],event)
    ids=[i['id'] for task in after['tasks'] for i in task['interrupts']]
    parts=[{'event':p.event,'data':p.data} for p in client.runs.stream(tid,report['assistant']['assistant_id'],
        command={'resume':{i:event['id'] for i in ids}},stream_mode='values',
        on_disconnect='continue',multitask_strategy='reject',durability='sync')]
    final=client.threads.get_state(tid)
    report.update({'after_restart':after,'resume_event':event,'resume_stream':parts,'final':final})
    RECORD.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    assert final['values']['phase']=='runtime_probe_complete' and final['values']['decision']['focus']=='initial'
    print(json.dumps({'phase':final['values']['phase'],'same_request_after_restart':True,'streams':len(parts),'thread':tid}))
