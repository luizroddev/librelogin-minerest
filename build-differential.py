import base64, hashlib, json, os, re, subprocess, urllib.request, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent
TARGET = ROOT / 'build' / 'differential'
TARGET.mkdir(parents=True, exist_ok=True)
lock = json.loads((ROOT / 'source-lock.json').read_text())
def run(args):
    subprocess.run([str(x) for x in args], check=True)
def fetch(url, sha, name):
    path = TARGET / name
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != sha:
        run(['curl', '--fail', '--location', '--silent', '--show-error', '--max-time', '90', '--output', path, url])
    if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
        raise RuntimeError('Checksum mismatch: ' + name)
    return path
jdk = Path(os.environ['JAVA_HOME']) / 'bin'
javac, java = jdk / 'javac', jdk / 'java'
version = subprocess.check_output([str(javac), '-version'], text=True)
if not version.startswith('javac 25'):
    raise RuntimeError('JDK 25 required')
original = fetch(lock['upstreamBinary']['url'], lock['upstreamBinary']['sha256'], 'LibreLogin-official.jar')
velocity = fetch(lock['velocity']['url'], lock['velocity']['sha256'], 'velocity.jar')
with zipfile.ZipFile(original) as archive:
    manifest = json.loads(archive.read('libby.json'))
    entries = {name: archive.read(name) for name in archive.namelist() if not name.endswith('/')}
rules = {a.replace('{}','.'): b.replace('{}','.') for a,b in manifest['relocations'].items()}
deps = {d['name']: fetch(d['url'], d['sha256'], d['name']+'.jar') for d in lock['buildDependencies']}
tools = TARGET / 'tools'
tools.mkdir(exist_ok=True)
toolcp = os.pathsep.join(str(deps[x]) for x in ('relocator','asm','asm-commons','asm-tree'))
run([javac,'-proc:none','--release','21','-cp',toolcp,'-d',tools,ROOT/'Relocate.java'])
ruleargs = [x for pair in sorted(rules.items()) for x in pair]
def relocate(path):
    out = TARGET / ('relocated-'+path.name)
    run([java,'-cp',str(tools)+os.pathsep+toolcp,'Relocate',path,out,*ruleargs])
    return out
classpath = [original,velocity]
for library in manifest['libraries']:
    if library['name'] not in lock['compileLibraries']:
        continue
    relative = library['group'].replace('{}','/')+'/'+library['name']+'/'+library['version']+'/'+library['name']+'-'+library['version']+'.jar'
    for repo in manifest['repositories']:
        try:
            path = fetch(repo.rstrip('/')+'/'+relative,base64.b64decode(library['checksum']).hex(),relative.rsplit('/',1)[1])
            break
        except (RuntimeError,subprocess.CalledProcessError):
            continue
    else:
        raise RuntimeError('Dependency unavailable: '+relative)
    classpath.append(relocate(path))
classpath.extend(relocate(deps[x]) for x in ('jsr305','annotations','floodgate'))
sourcepath = 'Plugin/src/main/java/xyz/kyngs/librelogin/common/authorization/AuthenticAuthorizationProvider.java'
source = (ROOT/sourcepath).read_text()
for a,b in sorted(rules.items(),key=lambda p:-len(p[0])):
    source = re.sub(r'(?<![\w.])'+re.escape(a)+r'(?=[.;\s])',b,source)
src = TARGET / 'source' / sourcepath
src.parent.mkdir(parents=True,exist_ok=True)
src.write_text(source)
classes = TARGET/'classes'
classes.mkdir(exist_ok=True)
run([javac,'-proc:none','--release','21','-encoding','UTF-8','-sourcepath',str(TARGET/'source'),'-cp',os.pathsep.join(map(str,classpath)),'-d',classes,src])
changed = []
for path in classes.rglob('*.class'):
    name = path.relative_to(classes).as_posix()
    if not name.startswith('xyz/kyngs/librelogin/common/authorization/AuthenticAuthorizationProvider'):
        raise RuntimeError('Unexpected compiled class: '+name)
    entries[name] = path.read_bytes()
    changed.append(name)
# Preserve upstream descriptors and bootstrap: internal version remains 0.24.0.
entries['LICENSE'] = (ROOT/'LICENSE').read_bytes()
for name in list(entries):
    if name.upper().startswith('META-INF/') and name.upper().endswith(('.SF','.RSA','.DSA')):
        raise RuntimeError('Signed upstream jar is not supported')
out = TARGET/('LibreLogin-'+lock['forkVersion']+'.jar')
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as archive:
    for name,data in sorted(entries.items()):
        info=zipfile.ZipInfo(name,(2026,11,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
        archive.writestr(info,data)
print('Differential build:',out,'compiled classes:',changed,'SHA256:',hashlib.sha256(out.read_bytes()).hexdigest())
