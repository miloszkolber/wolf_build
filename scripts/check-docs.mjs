import { readdirSync, readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';

const root = resolve(import.meta.dir, '..');
const walk = dir => readdirSync(dir, {withFileTypes:true}).flatMap(e => e.name.startsWith('.') ? [] : e.isDirectory() ? walk(resolve(dir,e.name)) : [resolve(dir,e.name)]);
const files = ['README.md','AGENTS.md', ...walk(resolve(root,'openspec')), ...walk(resolve(root,'compose'))].map(p=>resolve(root,p)).filter(p=>p.endsWith('.md'));
let failures=0;
for (const file of files) {
  const text=readFileSync(file,'utf8');
  if (/^```[^\n]*```/m.test(text) || /^```[ \t]+\S/m.test(text)) { console.error(`${file}: malformed fence`); failures++; }
  for (const [,href] of text.matchAll(/\[[^\]]*\]\(([^\s)]+)\)/g)) {
    if (/^https?:/.test(href)) continue;
    const path=href.split('#')[0];
    if (path && !existsSync(resolve(dirname(file),path))) {console.error(`${file}: missing ${href}`);failures++;}
  }
}
console.log(`${files.length} Markdown files checked, ${failures} failures`);
if (failures) process.exitCode=1;
