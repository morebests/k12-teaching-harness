"""Bounded fault-injection experiment, all responses explicitly fixtures. No vendor calls."""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import runtime_prototype as runtime
from langgraph.checkpoint.sqlite import SqliteSaver

BASE = Path(__file__).resolve().parent
RUN = BASE / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ-faults')
RUN.mkdir(parents=True)
COMMANDS = []
CASES = []


def save():
    report = {'run': str(RUN), 'source_sha256': hashlib.sha256((BASE/'runtime_prototype.py').read_bytes()).hexdigest(),
              'event_origin': 'fixture', 'model': 'FixedToolModel via LangChain create_agent; no external model',
              'checkpoint': 'SQLite sync; process exits, not machine power failure',
              'cases': CASES, 'commands': COMMANDS}
    (RUN/'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')


def call(task, command, *extra, code=0):
    cmd = [sys.executable, str(BASE/'runtime_prototype.py'), command, '--work', str(RUN/task), '--task', task, *map(str, extra)]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
    result = json.loads(proc.stdout) if proc.stdout.strip() else None
    COMMANDS.append({'command': cmd[2:], 'returncode': proc.returncode, 'result': result, 'stderr': proc.stderr})
    save()
    assert proc.returncode == code, f'{task}/{command}: expected {code}, got {proc.returncode}: {proc.stderr} {proc.stdout}'
    return result


def event(task, focus='rate', name='reply', **changes):
    req = runtime.request_for(task)
    obj = {'id': task+':'+name, 'actor': 'fixture-user', 'request_id': req['id'],
           'snapshot': req['snapshot'], 'focus': focus, 'origin': 'fixture',
           'raw': '测试脚本：采用变化率' if focus=='rate' else '测试脚本：改为初始值'}
    obj.update(changes)
    p = RUN/f'{task}-{name}-{len(COMMANDS)}.json'
    p.write_text(json.dumps(obj,ensure_ascii=False))
    return p


def arm(task, point):
    p = RUN/task/f'{task}.{point}.armed'
    p.write_text('PROTOTYPE one-shot hard process exit\n')


def passed(name, evidence):
    CASES.append({'name': name, 'passed': True, 'evidence': evidence})
    save()
    print(name + ': PASS', flush=True)


def update_state(task, changes):
    with SqliteSaver.from_conn_string(str(RUN/task/'PROTOTYPE-checkpoints.sqlite')) as cp:
        graph = runtime.builder().compile(checkpointer=cp)
        graph.update_state({'configurable': {'thread_id': task}}, changes)
    COMMANDS.append({'fault_injection': 'update checkpoint using public graph API', 'task': task, 'changes': changes})
    save()


try:
    a = call('normal', 'start')
    b = call('normal', 'status')
    assert a['pid'] != b['pid'] and a['request'] == b['request'] and not b['events']
    assert call('normal','resume',code=2)['error']=='still_waiting_for_real_event'
    e = event('normal')
    c = call('normal','reply','--event',e)
    assert c['state']['phase']=='runtime_probe_complete' and c['counts']['fixture_model_call']==2
    assert c['counts']['proposal_entered']==1 and c['counts']['wait_node_entered']==2
    d = call('normal','reply','--event',e)
    assert d['outcome']=='duplicate' and d['counts']==c['counts']
    conflict = event('normal','initial')
    assert call('normal','reply','--event',conflict,code=2)['error']=='event_id_payload_conflict'
    passed('fresh_process_wait_resume_and_duplicate', {'first_pid':a['pid'],'resume_pid':c['pid'],'counts':c['counts']})

    call('redirect','start')
    r = call('redirect','reply','--event',event('redirect','initial'))
    assert r['state']['decision']['focus']=='initial' and not r['next']
    assert '0 小时费用为' in Path(r['state']['manifest']['teacher.md']['path']).read_text()
    passed('explicit_redirection_without_second_confirmation', r['counts'])

    for point in ('after_event','after_student','after_teacher'):
        task=point
        call(task,'start')
        arm(task,point)
        call(task,'reply','--event',event(task),code=86)
        stopped=call(task,'status')
        assert stopped['delivery'] is None and stopped['counts'].get('verification_resource_read',0)==0
        if point!='after_event':
            assert call(task,'verify',code=2)['error']=='pair_manifest_incomplete'
        done=call(task,'resume')
        assert done['state']['phase']=='runtime_probe_complete'
        assert done['counts']['fixture_model_call']==2 and done['counts']['artifact_created']==2
        assert done['counts']['event_accepted']==1
        passed(point+'_hard_crash_recovered', {'stopped_next':stopped['next'],'counts':done['counts']})

    for name,mutation,error in [('missing','unlink','material_missing'),('altered','rewrite','material_snapshot_or_hash_mismatch')]:
        call(name,'start'); arm(name,'before_delivery')
        call(name,'reply','--event',event(name),code=86)
        state=call(name,'status')['state']; ref=Path(state['manifest']['student.md']['path'])
        original=ref.read_bytes()
        ref.unlink() if mutation=='unlink' else ref.write_text('stale or modified file')
        assert call(name,'deliver',code=2)['error']==error
        assert call(name,'verify',code=2)['error']==error
        rejected=call(name,'status')
        assert rejected['delivery'] is None and rejected['counts']['verification_resource_read']==1
        ref.write_bytes(original)
        done=call(name,'resume')
        assert done['state']['phase']=='runtime_probe_complete'
        passed(name+'_material_blocks_handoff_and_resource_read', {'counts':done['counts'],'repaired':'same exact bytes restored'})

    call('oldcheck','start'); arm('oldcheck','before_delivery')
    call('oldcheck','reply','--event',event('oldcheck'),code=86)
    s=call('oldcheck','status')['state']
    ref=Path(s['manifest']['student.md']['path']); ref.write_text(ref.read_text()+'\n修改后的题面。\n')
    s['manifest']['student.md']['sha256']=runtime.digest(ref.read_bytes())
    update_state('oldcheck',{'manifest':s['manifest']})
    assert call('oldcheck','deliver',code=2)['error']=='check_is_for_another_material_version'
    passed('new_material_cannot_reuse_old_check', {'delivery':call('oldcheck','status')['delivery']})

    call('oldreply','start'); old=event('oldreply')
    call('oldreply','supersede')
    assert call('oldreply','reply','--event',old,code=2)['error']=='reply_targets_old_snapshot'
    assert not call('oldreply','status')['events']
    passed('superseded_proposal_rejects_old_reply', {'accepted_events':0})

    call('cancelled','start'); arm('cancelled','before_delivery')
    call('cancelled','reply','--event',event('cancelled'),code=86)
    call('cancelled','cancel')
    assert call('cancelled','deliver',code=2)['error']=='cancelled_no_promotion'
    assert call('cancelled','resume',code=2)['error']=='cancelled_no_resume'
    passed('cancelled_result_not_promoted', {'delivery':call('cancelled','status')['delivery']})

    done=call('preselected','start','--preselected',event('preselected'))
    assert done['counts']['wait_node_entered']==1 and done['state']['phase']=='runtime_probe_complete'
    assert done['events'][0]['origin']=='fixture'
    passed('existing_scoped_event_skips_interrupt', done['counts'])

    call('race','start'); e=event('race')
    cmd=[sys.executable,str(BASE/'runtime_prototype.py'),'reply','--work',str(RUN/'race'),'--task','race','--event',str(e)]
    procs=[subprocess.Popen(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for _ in range(2)]
    outputs=[]
    for proc in procs:
        out,err=proc.communicate(timeout=30); assert proc.returncode==0,err
        outputs.append(json.loads(out))
    COMMANDS.append({'concurrent_cli_replies':outputs})
    final=call('race','status')
    assert final['counts']['build_entered']==1 and final['counts']['candidate_committed']==1
    passed('concurrent_duplicate_cli_reply_serialized', final['counts'])

    call('badbehavior','start','--behavior','unsupported-prototype-v0',code=2)
    passed('unsupported_behavior_is_explicitly_rejected', {'scope':'application guard, not deployment migration'})
except Exception as exc:
    CASES.append({'name':'experiment_stopped','passed':False,'error':repr(exc)})
    save()
    raise
print(json.dumps({'report':str(RUN/'results.json'),'cases':len(CASES),'all_passed':all(c['passed'] for c in CASES)}))
