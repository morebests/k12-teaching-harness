"""PROTOTYPE: fixed content, real LangGraph persistence; never production teaching quality."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, TypedDict

os.environ['LANGSMITH_TRACING'] = 'false'
os.environ['LANGCHAIN_TRACING_V2'] = 'false'

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[3]
RULE = REPO / 'k12-teacher-skills/plugin/skills/k12-check-for-understanding/references/verification.md'
BEHAVIOR = 'cfu-durable-prototype-v1'
FOCI = {
    'rate': '根据线性关系的两组对应值求变化率，并用单位解释它；区分 Δy/Δx 与 y/x。',
    'initial': '根据线性关系的两组对应值求初始值，并解释 x=0 的意义；区分已知时刻的值与初始值。',
}


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else encoded(value).encode()).hexdigest()


def connect(work):
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(work / 'PROTOTYPE-business.sqlite', timeout=10)
    con.row_factory = sqlite3.Row
    con.executescript('''
      CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, request TEXT NOT NULL,
        actor TEXT NOT NULL, status TEXT NOT NULL, event_id TEXT, delivery TEXT);
      CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, task TEXT NOT NULL,
        payload TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS observations (id INTEGER PRIMARY KEY, task TEXT,
        kind TEXT, payload TEXT, pid INTEGER, time REAL);
    ''')
    return con


def observe(work, task, kind, payload=None):
    with connect(work) as con:
        con.execute('INSERT INTO observations(task,kind,payload,pid,time) VALUES(?,?,?,?,?)',
                    (task, kind, encoded(payload), os.getpid(), time.time()))


def record(work, task):
    with connect(work) as con:
        row = con.execute('SELECT * FROM tasks WHERE id=?', (task,)).fetchone()
        if row is None:
            raise ValueError('unknown_task')
        return dict(row)


def fault(state, point):
    work = Path(state['work'])
    marker = work / f"{state['task']}.{point}.armed"
    if marker.exists():
        marker.unlink()
        observe(work, state['task'], 'hard_exit', {'point': point, 'exit_code': 86})
        os._exit(86)


def active(state):
    row = record(state['work'], state['task'])
    if row['status'] == 'cancelled':
        raise ValueError('cancelled_no_promotion')
    if state.get('behavior', BEHAVIOR) != BEHAVIOR:
        raise ValueError('unsupported_behavior_version')
    return row


def request_for(task, version=1):
    visible = {'standard': 'CCSS.Math.Content.8.F.B.4', 'version': version,
               'focus': FOCI['rate'], 'reason': '它检验学生是否用两个量的变化来解释速率，而非直接相除。',
               'alternatives': FOCI, 'fixture': True}
    return {'id': f'{task}:focus:{version}', 'snapshot': digest(visible), 'visible': visible}


class State(TypedDict, total=False):
    task: str
    work: str
    actor: str
    behavior: str
    request: dict
    decision: dict
    preselected: dict
    built: dict
    manifest: dict
    check: dict
    phase: str


def propose(state: State):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', state['task']):
        raise ValueError('invalid_task')
    if not Path(state['work']).resolve().is_relative_to(BASE / 'runs'):
        raise ValueError('prototype_work_must_be_inside_runs')
    req = request_for(state['task'])
    with connect(state['work']) as con:
        con.execute('INSERT OR IGNORE INTO tasks VALUES(?,?,?,?,NULL,NULL)',
                    (state['task'], encoded(req), state['actor'], 'active'))
    observe(state['work'], state['task'], 'proposal_entered')
    active(state)
    if state.get('preselected'):
        # This trusted caller input preserves the actual event and scope, not an approved flag.
        accept_event(state['work'], state['task'], state['preselected'])
    return {'request': req, 'behavior': BEHAVIOR, 'phase': 'proposed'}


def accept_event(work, task, event):
    """Prototype trusted caller seam. Production identity is NOT provided by this local script."""
    payload = encoded(event)
    with connect(work) as con:
        con.execute('BEGIN IMMEDIATE')
        previous = con.execute('SELECT * FROM events WHERE id=?', (event['id'],)).fetchone()
        if previous:
            if previous['task'] != task or previous['payload'] != payload:
                raise ValueError('event_id_payload_conflict')
            return 'duplicate'
        row = con.execute('SELECT * FROM tasks WHERE id=?', (task,)).fetchone()
        req = json.loads(row['request'])
        if row['status'] != 'active':
            raise ValueError('task_not_accepting_reply')
        if event['actor'] != row['actor']:
            raise ValueError('actor_not_authorized_in_fixture')
        if event['request_id'] != req['id'] or event['snapshot'] != req['snapshot']:
            raise ValueError('reply_targets_old_snapshot')
        if event['focus'] not in FOCI or event['origin'] not in ('fixture', 'real_user'):
            raise ValueError('unsupported_reply')
        if row['event_id']:
            raise ValueError('new_intent_requires_explicit_revision')
        con.execute('INSERT INTO events VALUES(?,?,?)', (event['id'], task, payload))
        con.execute('UPDATE tasks SET event_id=? WHERE id=?', (event['id'], task))
    observe(work, task, 'event_accepted', {'event_id': event['id'], 'origin': event['origin']})
    return 'accepted'


def wait_focus(state: State):
    row = active(state)
    observe(state['work'], state['task'], 'wait_node_entered')
    if state.get('preselected'):
        event_id = row['event_id']
    else:
        event_id = interrupt(json.loads(row['request']))
    row = active(state)
    if row['event_id'] != event_id:
        raise ValueError('resume_has_no_matching_saved_event')
    with connect(state['work']) as con:
        event = json.loads(con.execute('SELECT payload FROM events WHERE id=?', (event_id,)).fetchone()[0])
    if event['snapshot'] != state['request']['snapshot']:
        raise ValueError('saved_decision_no_longer_matches_request')
    return {'decision': event, 'phase': 'accepted'}


def fixed_materials(focus):
    if focus == 'rate':
        prompt = '水箱按恒定速率进水。开始时有 3 L，2 分钟时有 7 L，5 分钟时有 13 L。求进水速率并解释单位；说明为什么不能用 7÷2。'
        solution = '速率为 (13−7)/(5−2)=2 L/min；7÷2 包含原有的 3 L，不能代表新增水量的速率。'
    else:
        prompt = '一项租借费用随时间线性变化：2 小时费用 11 元，5 小时费用 23 元。求 0 小时时的费用并解释；说明为什么不是 11 元。'
        solution = '每小时增加 (23−11)/(5−2)=4 元；0 小时费用为 11−2×4=3 元。11 元已包含 2 小时的增加量。'
    return {'student.md': '# 运行验证用固定题面\n\n' + prompt + '\n',
            'teacher.md': '# 运行验证用固定教师说明\n\n' + prompt + '\n\n' + solution +
            '\n\n追问学生如何区分起始量与变化量。本材料未做完整教学质量评测。\n'}


class FixedToolModel(BaseChatModel):
    """Explicit scripted model to exercise create_agent. No vendor or reasoning-quality claim."""
    focus: str
    work: str
    task: str

    @property
    def _llm_type(self):
        return 'fixed-runtime-fixture'

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        observe(self.work, self.task, 'fixture_model_call', {'focus': self.focus})
        if isinstance(messages[-1], ToolMessage):
            msg = AIMessage(content=encoded(fixed_materials(self.focus)))
        else:
            msg = AIMessage(content='', tool_calls=[{'name': 'check_arithmetic',
                 'args': {'focus': self.focus}, 'id': 'fixed-calculation', 'type': 'tool_call'}])
        return ChatResult(generations=[ChatGeneration(message=msg)])


def build(state: State):
    active(state)
    observe(state['work'], state['task'], 'build_entered')

    @tool
    def check_arithmetic(focus: str) -> dict:
        """Check the fixed example's rate and intercept; no curriculum verification resource."""
        result = {'rate': (13-7)/(5-2)} if focus == 'rate' else {'rate': (23-11)/(5-2), 'initial': 11-2*4}
        observe(state['work'], state['task'], 'arithmetic_tool', result)
        return result

    agent = create_agent(FixedToolModel(focus=state['decision']['focus'], work=state['work'],
                                      task=state['task']), tools=[check_arithmetic],
                         system_prompt='Runtime fixture. Verification resources are not available here.')
    result = agent.invoke({'messages': [{'role': 'user', 'content': FOCI[state['decision']['focus']]}]},
                          {'recursion_limit': 6})
    return {'built': json.loads(result['messages'][-1].content), 'phase': 'built'}


def write_pair(state: State):
    active(state)
    manifest = {}
    folder = Path(state['work']) / 'artifacts' / state['task'] / state['request']['snapshot'][:16]
    folder.mkdir(parents=True, exist_ok=True)
    for role, content in state['built'].items():
        data = content.encode()
        path = folder / role
        if path.exists():
            if path.read_bytes() != data:
                raise ValueError('artifact_content_conflict')
            observe(state['work'], state['task'], 'artifact_reused', {'role': role})
        else:
            temp = path.with_suffix('.pending')
            with temp.open('wb') as out:
                out.write(data)
                out.flush()
                os.fsync(out.fileno())
            os.replace(temp, path)
            observe(state['work'], state['task'], 'artifact_created', {'role': role, 'sha256': digest(data)})
        fault(state, 'after_' + role.split('.')[0])
        manifest[role] = {'path': str(path), 'sha256': digest(data), 'snapshot': state['request']['snapshot']}
    return {'manifest': manifest, 'phase': 'written'}


def actual_hashes(state):
    manifest = state.get('manifest', {})
    if set(manifest) != {'student.md', 'teacher.md'}:
        raise ValueError('pair_manifest_incomplete')
    hashes = {}
    for role, ref in manifest.items():
        p = Path(ref['path'])
        if not p.is_file():
            raise ValueError('material_missing')
        value = digest(p.read_bytes())
        if ref['snapshot'] != state['request']['snapshot'] or value != ref['sha256']:
            raise ValueError('material_snapshot_or_hash_mismatch')
        hashes[role] = value
    return hashes


def verify(state: State):
    active(state)
    hashes = actual_hashes(state)  # Fail before opening the full CFU verification resource.
    resource = RULE.read_bytes()
    observe(state['work'], state['task'], 'verification_resource_read',
            {'sha256': digest(resource), 'bytes': len(resource), 'actual_materials': hashes})
    # Fixed fixture integrity only. The actual two pedagogical gates remain untested.
    check = {'hashes': hashes, 'request_snapshot': state['request']['snapshot'],
             'rule_sha256': digest(resource), 'scope': 'fixture integrity; not pedagogical gate evaluation'}
    return {'check': check, 'phase': 'checked'}


def deliver(state: State):
    active(state)
    hashes = actual_hashes(state)
    check = state['check']
    if hashes != check['hashes'] or check['request_snapshot'] != state['request']['snapshot']:
        raise ValueError('check_is_for_another_material_version')
    if check['rule_sha256'] != digest(RULE.read_bytes()):
        raise ValueError('verification_rule_changed')
    fault(state, 'before_delivery')
    delivery = {'manifest': state['manifest'], 'check': check,
                'event_id': state['decision']['id'], 'teaching_quality': 'not_evaluated'}
    with connect(state['work']) as con:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT * FROM tasks WHERE id=?', (state['task'],)).fetchone()
        if row['status'] == 'cancelled':
            raise ValueError('cancelled_no_promotion')
        if json.loads(row['request'])['snapshot'] != state['request']['snapshot']:
            raise ValueError('current_request_version_changed')
        con.execute('UPDATE tasks SET delivery=? WHERE id=?', (encoded(delivery), state['task']))
    observe(state['work'], state['task'], 'candidate_committed', {'hashes': hashes})
    return {'phase': 'runtime_probe_complete'}


def builder():
    g = StateGraph(State)
    nodes = [('propose', propose), ('await_focus', wait_focus), ('build', build),
             ('write_pair', write_pair), ('verify', verify), ('deliver', deliver)]
    previous = START
    for name, fn in nodes:
        g.add_node(name, fn)
        g.add_edge(previous, name)
        previous = name
    g.add_edge(previous, END)
    return g


# Agent Server injects its own checkpointer. SQLite is used only by the standalone CLI below.
graph = builder().compile()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['start', 'reply', 'resume', 'status', 'cancel', 'verify', 'deliver', 'supersede'])
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--task', default='probe')
    p.add_argument('--event', type=Path)
    p.add_argument('--actor', default='fixture-user')
    p.add_argument('--preselected', type=Path)
    p.add_argument('--behavior', default=BEHAVIOR)
    args = p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.task):
        raise ValueError('invalid_task')
    args.work = args.work.resolve()
    args.work.mkdir(parents=True, exist_ok=True)
    # CLI-only serialization. Agent Server owns same-thread run scheduling in the server probe.
    driver_lock = (args.work / f'{args.task}.driver.lock').open('a')
    if args.command in ('start', 'reply', 'resume'):
        fcntl.flock(driver_lock, fcntl.LOCK_EX)
    config = {'configurable': {'thread_id': args.task}, 'recursion_limit': 30}
    with SqliteSaver.from_conn_string(str(args.work/'PROTOTYPE-checkpoints.sqlite')) as cp:
        g = builder().compile(checkpointer=cp)
        try:
            outcome = None
            if args.command == 'start':
                if g.get_state(config).values:
                    raise ValueError('task_already_started')
                initial = {'task': args.task, 'work': str(args.work), 'actor': args.actor, 'behavior': args.behavior}
                if args.preselected:
                    initial['preselected'] = json.loads(args.preselected.read_text())
                g.invoke(initial, config, durability='sync')
            elif args.command in ('reply', 'resume'):
                if args.command == 'reply':
                    outcome = accept_event(args.work, args.task, json.loads(args.event.read_text()))
                    fault({'work': str(args.work), 'task': args.task}, 'after_event')
                snap = g.get_state(config)
                row = record(args.work, args.task)
                if row['status'] == 'cancelled':
                    raise ValueError('cancelled_no_resume')
                if snap.next:
                    interrupts = [i for t in snap.tasks for i in t.interrupts]
                    if interrupts:
                        if not row['event_id']:
                            raise ValueError('still_waiting_for_real_event')
                        g.invoke(Command(resume={i.id: row['event_id'] for i in interrupts}), config, durability='sync')
                    else:
                        g.invoke(None, config, durability='sync')
            elif args.command == 'cancel':
                with connect(args.work) as con:
                    con.execute('UPDATE tasks SET status=? WHERE id=?', ('cancelled', args.task))
            elif args.command == 'supersede':
                with connect(args.work) as con:
                    con.execute('UPDATE tasks SET request=?,event_id=NULL WHERE id=?',
                                (encoded(request_for(args.task, 2)), args.task))
            elif args.command in ('verify', 'deliver'):
                state = g.get_state(config).values
                outcome = (verify if args.command == 'verify' else deliver)(state)
            snap = g.get_state(config)
            row = record(args.work, args.task)
            with connect(args.work) as con:
                counts = dict(con.execute('SELECT kind, count(*) FROM observations WHERE task=? GROUP BY kind', (args.task,)))
                events = [json.loads(r[0]) for r in con.execute('SELECT payload FROM events WHERE task=?', (args.task,))]
            print(encoded({'pid': os.getpid(), 'outcome': outcome, 'state': snap.values,
                           'next': list(snap.next), 'request': json.loads(row['request']),
                           'status': row['status'], 'delivery': json.loads(row['delivery']) if row['delivery'] else None,
                           'events': events, 'counts': counts}))
        except ValueError as exc:
            print(encoded({'error': str(exc), 'pid': os.getpid()}))
            sys.exit(2)


if __name__ == '__main__':
    main()
