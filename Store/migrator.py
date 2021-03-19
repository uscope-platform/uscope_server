import redis
import json
import Database

store = Database.DataStore("172.23.0.2")
redis_if = redis.Redis(host='0.0.0.0', port=6379, db=2, charset="utf-8", decode_responses=True)

applications = redis_if.hgetall('Applications')
for i in applications:
    applications[i] = json.loads(applications[i])
    store.add_application(i, applications[i])

peripherals = redis_if.hgetall('Peripherals')
for i in peripherals:
    peripherals[i] = json.loads(peripherals[i])
    store.add_peripheral(i, peripherals[i])

scripts = redis_if.hgetall('Scripts')
for i in scripts:
    scripts[i] = json.loads(scripts[i])
    store.add_scripts(i, scripts[i])

programs = redis_if.hgetall('Programs')
for i in programs:
    programs[i] = json.loads(programs[i])
    store.add_program(int(i), programs[i])
a = 0
